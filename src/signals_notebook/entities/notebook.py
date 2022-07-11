import json
import logging
from typing import Literal, Optional

from pydantic import BaseModel, Field

from signals_notebook.common_types import EntityCreationRequestPayload, EntityType
from signals_notebook.entities import EntityStore
from signals_notebook.entities.container import Container

log = logging.getLogger(__name__)


class _Attributes(BaseModel):
    name: str
    description: Optional[str] = None


class _RequestBody(BaseModel):
    type: EntityType
    attributes: _Attributes


class _RequestPayload(EntityCreationRequestPayload[_RequestBody]):
    pass


class Notebook(Container):
    type: Literal[EntityType.NOTEBOOK] = Field(allow_mutation=False)

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.NOTEBOOK

    @classmethod
    def create(
        cls,
        *,
        name: str,
        description: Optional[str] = None,
        digest: str = None,
        force: bool = True,
    ) -> 'Notebook':
        """Create Notebook in Signals Notebooks

        Args:
            name: Notebook name
            description: Notebook description
            digest: Indicate digest
            force: Force to create without doing digest check

        Returns:

        """

        request = _RequestPayload(
            data=_RequestBody(
                type=cls._get_entity_type(),
                attributes=_Attributes(
                    name=name,
                    description=description,
                ),
            )
        )

        log.debug('Creating Notebook for: %s', cls.__name__)
        return super()._create(
            digest=digest,
            force=force,
            request=request,
        )

    def dump(self, base_path, fs_handler):
        fs_handler.write(base_path + '/' + self.eid + '/metadata.json', json.dumps(self.get_metadata()))
        for child in self.get_children():
            child.dump(base_path + '/' + self.eid, fs_handler)

    @classmethod
    def load(cls, path, fs_handler):
        metadata = json.loads(fs_handler.read(path+'/'+'metadata.json'))
        notebook = Notebook.create(name='restore:' + metadata['name'], description=metadata['description'], force=True)
        child_entities_folders = fs_handler.list_subfolders(path)
        for child_entity in child_entities_folders:
            child_entity_type = child_entity.split(':')[0]
            EntityStore.get_entity_class(child_entity_type).load(
                path+'/'+child_entity, fs_handler, notebook
            )
