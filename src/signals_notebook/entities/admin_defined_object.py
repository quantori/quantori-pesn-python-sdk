import json
import logging
from functools import cached_property
from typing import Any, ClassVar, List, Literal, Optional

from pydantic import BaseModel, Field

from signals_notebook.common_types import Ancestors, EntityCreationRequestPayload, EntityType, Template
from signals_notebook.entities import Notebook
from signals_notebook.entities.container import Container
from signals_notebook.jinja_env import env
from signals_notebook.utils import FSHandler

CUSTOM_SYSTEM_OBJECT = 'Custom System Object'
log = logging.getLogger(__name__)


class _Attributes(BaseModel):
    name: str
    description: Optional[str] = None


class _Relationships(BaseModel):
    template: Optional[Template] = None
    ancestors: Optional[Ancestors] = None


class _Meta(BaseModel):
    ado_type_name: str = Field(alias='adoTypeName')

    class Config:
        validate_assignment = True
        allow_population_by_field_name = True


class _RequestBody(BaseModel):
    type: EntityType
    meta: _Meta
    attributes: _Attributes
    relationships: Optional[_Relationships] = None


class _RequestPayload(EntityCreationRequestPayload[_RequestBody]):
    pass


class AdoType(BaseModel):
    id: str
    base_type: str = Field(alias='baseType')
    ado_name: str = Field(alias='adoName')

    class Config:
        validate_assignment = True
        allow_population_by_field_name = True


class AdminDefinedObject(Container):
    type: Literal[EntityType.ADO] = Field(allow_mutation=False)
    ado: AdoType = Field(default=CUSTOM_SYSTEM_OBJECT)
    _template_name: ClassVar = 'ado.html'

    class Config:
        keep_untouched = (cached_property,)

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.ADO

    @classmethod
    def create(
        cls,
        *,
        name: str,
        ado_type_name: str,
        description: Optional[str] = None,
        template: Optional['AdminDefinedObject'] = None,
        notebook: Optional[Notebook] = None,
        digest: Optional[str] = None,
        force: bool = True,
    ) -> 'AdminDefinedObject':
        """Create new AdminDefinedObject in Signals Notebook

        Args:
            name: name of AdminDefinedObject
            ado_type_name: new type name for ADO object
            description: description of AdminDefinedObject
            template: AdminDefinedObject template
            notebook: notebook where create AdminDefinedObject
            digest: Indicate digest
            force: Force to create without doing digest check

        Returns:
            AdminDefinedObject
        """
        relationships = None
        if template or notebook:
            relationships = _Relationships(
                ancestors=Ancestors(data=[notebook.short_description]) if notebook else None,
                template=Template(data=template.short_description) if template else None,
            )
        request = _RequestPayload(
            data=_RequestBody(
                type=cls._get_entity_type(),
                meta=_Meta(ado_type_name=ado_type_name),
                attributes=_Attributes(
                    name=name,
                    description=description,
                ),
                relationships=relationships,
            )
        )

        log.debug('Creating AdminDefinedObject for: %s', cls.__name__)
        return super()._create(
            digest=digest,
            force=force,
            request=request,
        )

    def get_html(self) -> str:
        """Get in HTML format

        Returns:
            Rendered template as a string
        """
        data = {
            'title': self.name,
            'description': self.description,
            'edited_at': self.edited_at,
            'children': self.get_children(),
        }

        template = env.get_template(self._template_name)
        log.info('Html template for %s:%s has been rendered.', self.__class__.__name__, self.eid)

        return template.render(data=data)

    def dump(
        self, base_path: str, fs_handler: FSHandler, alias: Optional[List[str]] = None
    ) -> None:  # type: ignore[override]
        """Dump AdminDefinedObject entity

        Args:
            base_path: content path where create dump
            fs_handler: FSHandler
            alias: Backup alias

        Returns:

        """
        metadata = {
            **self.ado.dict(exclude={'id'}),
            **{k: v for k, v in self.dict().items() if k in ('name', 'description', 'eid')},
        }
        fs_handler.write(
            fs_handler.join_path(base_path, self.eid, 'metadata.json'),
            json.dumps(metadata),
            base_alias=alias + [self.name, '__Metadata'] if alias else None,
        )
        for child in self.get_children():
            child.dump(fs_handler.join_path(base_path, self.eid), fs_handler)

    @classmethod
    def load(cls, path: str, fs_handler: FSHandler, notebook: Notebook) -> None:
        """Load AdminDefinedObject entity

        Args:
            path: content path
            fs_handler: FSHandler
            notebook: Container where load Experiment entity

        Returns:

        """
        cls._load(path, fs_handler, notebook)

    @classmethod
    def _load(cls, path: str, fs_handler: FSHandler, parent: Any) -> None:
        from signals_notebook.item_mapper import ItemMapper

        metadata = json.loads(fs_handler.read(fs_handler.join_path(path, 'metadata.json')))
        experiment = cls.create(
            notebook=parent,
            name=metadata['name'],
            ado_type_name=metadata.get('ado_name', CUSTOM_SYSTEM_OBJECT),
            description=metadata['description'],
            force=True,
        )
        child_entities_folders = fs_handler.list_subfolders(path)
        for child_entity in child_entities_folders:
            child_entity_type = child_entity.split(':')[0]
            ItemMapper.get_item_class(child_entity_type)._load(
                fs_handler.join_path(path, child_entity), fs_handler, experiment
            )
