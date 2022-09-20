import json
import logging
from enum import Enum
from functools import cached_property
from typing import Any, cast, ClassVar, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import ChemicalDrawingFormat, EntityType, File, Response, ResponseData
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.entities.stoichiometry.stoichiometry import Stoichiometry
from signals_notebook.jinja_env import env
from signals_notebook.utils import FSHandler

log = logging.getLogger(__name__)

EMPTY_CDXML_FILE_CONTENT = b'<CDXML />'


class ChemicalDrawingPosition(str, Enum):
    REACTANTS = 'reactants'
    REAGENTS = 'reagents'
    PRODUCTS = 'products'


class ChemicalStructure(str, Enum):
    REACTANT = 'reactant'
    REAGENT = 'reagent'
    PRODUCT = 'product'


class ChemicalStructureFormat(str, Enum):
    INCHI = 'inchi'
    CDXML = 'cdxml'


class Structure(BaseModel):
    id: str
    type: ChemicalStructure
    inchi: Optional[str]
    cdxml: Optional[str]

    class Config:
        validate_assignment = True


class ChemicalDrawingResponse(Response[Structure]):
    pass


class StructureAttribute(BaseModel):
    dataType: ChemicalStructureFormat  # noqa
    data: str


class StructureRequestData(BaseModel):
    attributes: StructureAttribute


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
        SMILES = 'chemical/x-daylight-smiles'

    class CreationContentType(str, Enum):
        CDX = 'chemical/x-cdx'
        CDXML = 'chemical/x-cdxml'
        MOL = 'chemical/x-mdl-molfile'

    type: Literal[EntityType.CHEMICAL_DRAWING] = Field(allow_mutation=False)
    _template_name: ClassVar = 'chemical_drawing.html'

    class Config:
        keep_untouched = (cached_property,)

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.CHEMICAL_DRAWING

    @classmethod
    def _get_chemical_drawing_endpoint(cls) -> str:
        return 'chemicaldrawings'

    def get_structures(self, positions: ChemicalDrawingPosition) -> list[Structure]:
        """Get reactants, reagents and products of ChemicalDrawing

        Args:
            positions:  one of the ChemicalDrawing positions

        Returns:
            list of Structure objects
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Reloading structures in ChemicalDrawing: %s...', self.eid)

        response = api.call(
            method='GET',
            path=(self._get_chemical_drawing_endpoint(), self.eid, 'reaction', positions),
        )

        result = ChemicalDrawingResponse(**response.json())

        return [cast(ResponseData, item).body for item in result.data]

    def add_structures(
        self,
        structure: Structure,
        positions: ChemicalDrawingPosition,
        digest: str = None,
        force: bool = True,
    ) -> Structure:
        """Add reagent, reactant or product to ChemicalDrawing

        Args:
            structure: Structure object
            positions: one of the ChemicalDrawing positions
            digest: Indicate digest of entity. It is used to avoid conflict while concurrent editing.
                If the parameter 'force' is true, this parameter is optional.
                If the parameter 'force' is false, this parameter is required.
            force: Force to create without doing digest check

        Returns:
            Added Structure
        """
        api = SignalsNotebookApi.get_default_api()

        if structure.inchi:
            data_type = ChemicalStructureFormat.INCHI
            data = structure.inchi
        elif structure.cdxml:
            data_type = ChemicalStructureFormat.CDXML
            data = structure.cdxml
        else:
            raise ValueError('Structure doesn"t contain inchi and cdxml data')

        request_data = StructureRequestData(attributes=StructureAttribute(dataType=data_type, data=data))

        response = api.call(
            method='POST',
            path=(self._get_chemical_drawing_endpoint(), self.eid, 'reaction', positions),
            params={
                'digest': digest,
                'force': json.dumps(force),
            },
            json={'data': request_data.dict()},
        )
        result = ChemicalDrawingResponse(**response.json())
        return cast(ResponseData, result.data).body

    @classmethod
    def create(
        cls,
        *,
        container: Container,
        name: str,
        content_type: str = CreationContentType.CDXML,
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
            cls.CreationContentType(content_type)
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
    def dump_templates(cls, base_path: str, fs_handler: FSHandler) -> None:
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
                    fs_handler.join_path(base_path, 'templates', entity_type),
                    fs_handler,
                    ['Templates', entity_type.value],
                )
        except TypeError:
            pass

    def dump(self, base_path: str, fs_handler: FSHandler, alias: Optional[List[str]] = None) -> None:
        """Dump ChemicalDrawing

        Args:
            base_path: content path where create dump
            fs_handler: FSHandler
            alias: Backup alias

        Returns:

        """
        content = self.get_content()

        if content.content != EMPTY_CDXML_FILE_CONTENT:
            metadata: Dict[str, Any] = {
                'file_name': content.name,
                'content_type': content.content_type,
                **{k: v for k, v in self.dict().items() if k in ('name', 'description', 'eid')},
            }
            if content.content_type == self.ContentType.CDXML:
                reactants = self.get_structures(positions=ChemicalDrawingPosition.REACTANTS)
                products = self.get_structures(positions=ChemicalDrawingPosition.PRODUCTS)
                reagents = self.get_structures(positions=ChemicalDrawingPosition.REAGENTS)
                metadata = {
                    **metadata,
                    **{
                        'reactants': [{'id': i.id, 'inchi': i.inchi, 'cdxml': i.cdxml} for i in reactants],
                        'products': [{'id': i.id, 'inchi': i.inchi, 'cdxml': i.cdxml} for i in products],
                        'reagents': [{'id': i.id, 'inchi': i.inchi, 'cdxml': i.cdxml} for i in reagents],
                    },
                }

            fs_handler.write(
                fs_handler.join_path(base_path, self.eid, 'metadata.json'),
                json.dumps(metadata),
                base_alias=alias + [self.name, '__Metadata'] if alias else None
            )
            file_name = content.name
            data = content.content
            fs_handler.write(fs_handler.join_path(
                base_path, self.eid, file_name), data,
                base_alias=alias + [self.name, file_name] if alias else None
            )
