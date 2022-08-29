import json
import logging
from datetime import datetime
from enum import Enum
from typing import cast, Generator, List, Union

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import EID, EntityType, Response, ResponseData
from signals_notebook.entities import Entity
from signals_notebook.utils import FSHandler

log = logging.getLogger(__name__)


class EntityStore:
    class IncludeOptions(str, Enum):
        MINE = 'mine'
        OTHER = 'other'
        SHARED = 'shared'
        TRASHED = 'trashed'
        UNTRASHED = 'untrashed'
        TRASHED_ANCESTOR = 'trashedAncestor'
        STARRED = 'starred'
        UNSTARRED = 'unstarred'
        TEMPLATE = 'template'
        NONTEMPLATE = 'nontemplate'
        SYSTEM_TEMPLATE = 'systemTemplate'
        NON_SYSTEM_TEMPLATE = 'nonSystemTemplate'

    @staticmethod
    def _get_endpoint() -> str:
        return 'entities'

    @classmethod
    def get(cls, eid: EID) -> Entity:
        """Get Entity by ID

        Args:
            eid: Entity ID

        Returns:
            Entity
        """

        api = SignalsNotebookApi.get_default_api()
        log.debug('Get Entity: %s from EntityStore...', eid)

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(), eid),
        )

        entity_classes = (*Entity.get_subclasses(), Entity)
        result = Response[Union[entity_classes]](**response.json())  # type: ignore
        log.debug('Entity: %s was got successfully from EntityStore.', eid)

        return cast(ResponseData, result.data).body

    @classmethod
    def get_list(
        cls,
        include_types: List[EntityType] = None,
        exclude_types: List[EntityType] = None,
        include_options: List[IncludeOptions] = None,
        modified_after: datetime = None,
        modified_before: datetime = None,
    ) -> Generator[Entity, None, None]:
        """Get all entities

        Args:
            include_types: Included entity types, separated by comma ','.
                For example, 'experiment, journal, ado'.
                The default include types are experiment, request and journal.
            exclude_types: Excluded entity types, separated by comma ','. For example, 'experiment, journal'.
            include_options: Flags of entities, separated by comma ','.
            modified_after: Return the entities which are modified after start time.
            modified_before: Return the entities which are modified before end time.

        Returns:
            Entity
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get List of Entities from EntityStore...')

        params = {}
        if include_types:
            params['includeTypes'] = ','.join(include_types)
        if exclude_types:
            params['excludeTypes'] = ','.join(exclude_types)
        if include_options:
            params['includeOptions'] = ','.join(include_options)
        if modified_after:
            params['start'] = modified_after.isoformat()
        if modified_before:
            params['end'] = modified_before.isoformat()

        entity_classes = (*Entity.get_subclasses(), Entity)

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(),),
            params=params or None,
        )

        result = Response[Union[entity_classes]](**response.json())  # type: ignore
        yield from [cast(ResponseData, item).body for item in result.data]

        while result.links and result.links.next:
            response = api.call(
                method='GET',
                path=result.links.next,
            )

            result = Response[Union[entity_classes]](**response.json())  # type: ignore
            yield from [cast(ResponseData, item).body for item in result.data]

        log.debug('List of Entities were got successfully from EntityStore.')

    @classmethod
    def refresh(cls, entity: Entity) -> None:
        """Refresh Entity with new values

        Args:
            entity: Entity

        Returns:

        """
        refreshed_entity = cls.get(entity.eid)
        for field in entity.__fields__.values():
            if field.field_info.allow_mutation:
                new_value = getattr(refreshed_entity, field.name)
                setattr(entity, field.name, new_value)

    @classmethod
    def delete(cls, eid: EID, digest: str = None, force: bool = True) -> None:
        """Delete Entity by ID

        Args:
            eid: Entity ID
            digest: Indicate digest of entity. It is used to avoid conflict while concurrent editing.
                If the parameter 'force' is true, this parameter is optional.
                If the parameter 'force' is false, this parameter is required.
            force: Force to delete without doing digest check.

        Returns:

        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Deleting Entity: %s from EntityStore...', eid)

        api.call(
            method='DELETE',
            path=(cls._get_endpoint(), eid),
            params={
                'digest': digest,
                'force': json.dumps(force),
            },
        )
        log.debug('Entity: %s was deleted from EntityStore successfully', eid)

    @classmethod
    def dump_templates(cls, base_path: str, fs_handler: FSHandler) -> None:
        """Dump all templates from system

        Args:
            base_path: content path where create templates dump
            fs_handler: FSHandler

        Returns:

        """

        for item in Entity.get_subclasses():
            try:
                item.dump_templates(base_path, fs_handler)
            except Exception as e:
                log.error('Failed to dump templates for %s with error %s' % (str(item), str(e)))
