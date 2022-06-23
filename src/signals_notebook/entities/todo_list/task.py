import json
from typing import Literal, List, Dict, Union, cast, Optional
from uuid import UUID

from pydantic import Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import EntityType, ResponseData, Response
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container


class TaskProperty:
    pass


# class TaskPropertiesResponse(Response[TaskProperty]):
#     pass


class Task(Entity):
    type: Literal[EntityType.TASK] = Field(allow_mutation=False)
    _properties: List[TaskProperty] = PrivateAttr(default=[])
    _properties_by_id: Dict[Union[str, UUID], TaskProperty] = PrivateAttr(default={})

    def __getitem__(self, index: Union[int, str, UUID]) -> TaskProperty:
        if not self._properties:
            self._reload_properties()

        if isinstance(index, int):
            return self._properties[index]

        if isinstance(index, str):
            try:
                return self._properties_by_id[UUID(index)]
            except ValueError:
                return self._properties_by_id[index]

        if isinstance(index, UUID):
            return self._properties_by_id[index]

        raise IndexError('Invalid index')

    def __iter__(self):
        if not self._properties:
            self._reload_properties()
        return self._properties.__iter__()

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.TASK

    @classmethod
    def _get_task_endpoint(cls) -> str:
        return 'task'

    def _reload_properties(self) -> None:
        self._properties = []
        self._properties_by_id = {}

        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_task_endpoint(), self.eid, 'properties'),
            params={'value': 'normalized'},
        )

        # result = SamplePropertiesResponse(**response.json())
        # properties = [cast(ResponseData, item).body for item in result.data]
        #
        # for item in properties:
        #     sample_property = cast(TaskProperty, item)
        #     assert sample_property.id
        #
        #     self._properties.append(sample_property)
        #     self._properties_by_id[sample_property.id] = sample_property

    # def save(self, force: bool = True) -> None:
    #     api = SignalsNotebookApi.get_default_api()
    #
    #     request_body = []
    #     for item in self._properties:
    #         if item.is_changed:
    #             request_body.append(item.representation_for_update.dict(exclude_none=True))
    #
    #     if not request_body:
    #         return
    #
    #     api.call(
    #         method='PATCH',
    #         path=(self._get_samples_endpoint(), self.eid, 'properties'),
    #         params={
    #             'force': json.dumps(force),
    #             'value': 'normalized',
    #         },
    #         json={
    #             'data': {'attributes': {'data': request_body}},
    #         },
    #     )
    #     self._reload_properties()

    # @classmethod
    # def create(
    #     cls,
    #     *,
    #     properties: Optional[List[TaskProperty]] = None,
    #     template: Optional['Sample'] = None,
    #     ancestors: Optional[List[Union[Container, 'SamplesContainer']]] = None,
    #     digest: str = None,
    #     force: bool = True,
    # ) -> 'Sample':
    #     relationships = None
    #     if template or ancestors:
    #         relationships = _SampleRelationships(
    #             ancestors=Ancestors(data=[item.short_description for item in ancestors]) if ancestors else None,
    #             template={'data': template.short_description} if template else None,
    #         )
    #
    #     request = _SampleRequestPayload(
    #         data=_SampleRequestBody(
    #             type=cls._get_entity_type(),
    #             attributes=_SampleAttributes(fields=properties),
    #             relationships=relationships,
    #         )
    #     )
    #
    #     return super()._create(
    #         digest=digest,
    #         force=force,
    #         request=request,
    #     )
