import logging
from enum import Enum
from functools import cached_property
from typing import ClassVar, Literal, Optional, Union, Tuple

from pydantic import Field

from signals_notebook.common_types import ChemicalDrawingFormat, EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.entities.stoichiometry.stoichiometry import Stoichiometry
from signals_notebook.jinja_env import env
from signals_notebook.utils import FSHandler

log = logging.getLogger(__name__)


class ChemicalDrawing(ContentfulEntity):
    class ContentType(str, Enum):
        CDX = 'chemical/x-cdx'
        CDXML = 'chemical/x-cdxml'
        SDF = 'chemical/x-mdl-sdfile'
        MOL = 'chemical/x-mdl-molfile'
        RXN = 'chemical/x-mdl-rxnfile'
        SW = 'chemical/x-swissprot'
        SVG = 'image/svg+xml'
        CSV = 'text/csv'

    type: Literal[EntityType.CHEMICAL_DRAWING] = Field(allow_mutation=False)
    _template_name: ClassVar = 'chemical_drawing.html'

    class Config:
        keep_untouched = (cached_property,)

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.CHEMICAL_DRAWING

    @classmethod
    def create(
        cls,
        *,
        container: Container,
        name: str,
        content_type: str = ContentType.SVG,
        content: bytes = b'',
        force: bool = True,
    ) -> Entity:
        """Create ChemicalDrawing Entity

        Args:
            container: Container where create new ChemicalDrawing
            name: file name
            content_type: type of the file
            content: Entity content
            force: Force to post attachment

        Returns:
            ChemicalDrawing
        """
        if content_type:
            cls.ContentType(content_type)
        log.debug('Create entity: %s with name: %s in Container: %s', cls.__name__, name, container.eid)
        return container.add_child(
            name=name,
            content=content,
            content_type=content_type,
            force=force,
        )

    def get_content(self, format: Optional[ChemicalDrawingFormat] = None) -> File:
        """Get Entity content

        Args:
            format: Export resource format

        Returns:

        """
        return super()._get_content(format=format)

    @cached_property
    def stoichiometry(self) -> Union[Stoichiometry, list[Stoichiometry]]:
        """Fetch stoichiometry data of ChemicalDrawing

        Returns:
            Union[Stoichiometry, list[Stoichiometry]]
        """
        return Stoichiometry.fetch_data(self.eid)

    def get_html(self) -> str:
        """Get in HTML format

        Returns:
            Rendered template as a string
        """
        data = {'name': self.name, 'stoichiometry': {}}
        file = self.get_content(format=ChemicalDrawingFormat.SVG)
        data['svg'] = 'data:{};base64,{}'.format(file.content_type, file.base64.decode('ascii'))
        if isinstance(self.stoichiometry, Stoichiometry):
            data['stoichiometry_html'] = self.stoichiometry.get_html()

        template = env.get_template(self._template_name)
        log.info('Html template for %s:%s has been rendered.', self.__class__.__name__, self.eid)

        return template.render(data=data)

    @classmethod
    def dump_templates(cls, base_path: str, fs_handler: FSHandler, base_alias: Tuple[str]) -> None:
        """Dump ChemicalDrawing templates

        Args:
            base_path: content path where create templates dump
            fs_handler: FSHandler

        Returns:

        """
        from signals_notebook.entities import EntityStore

        entity_type = cls._get_entity_type()

        templates = EntityStore.get_list(
            include_types=[entity_type], include_options=[EntityStore.IncludeOptions.TEMPLATE]
        )
        try:
            for template in templates:
                template.dump(
                    fs_handler.join_path(base_path, 'templates', entity_type), fs_handler,
                    ('Templates', entity_type, template.name))
        except TypeError:
            pass
