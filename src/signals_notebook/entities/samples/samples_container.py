import csv
import logging
from enum import Enum
from io import StringIO
from typing import Any, cast, ClassVar, Dict, Generator, List, Literal, Optional, Union
from uuid import UUID

from pydantic import Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import EID, EntityType, File, Response, ResponseData
from signals_notebook.entities import Sample
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.jinja_env import env
from signals_notebook.utils import FSHandler

log = logging.getLogger(__name__)


class SamplesContainerFormat(str, Enum):
    CSV = 'csv'
    SDF = 'sdf'


class SamplesContainerResponse(Response[Sample]):
    pass


class SamplesContainer(ContentfulEntity):
    type: Literal[EntityType.SAMPLES_CONTAINER] = Field(allow_mutation=False)
    _template_name: ClassVar = 'samplesContainer.html'
    _samples: List[Sample] = PrivateAttr(default=[])
    _samples_by_id: Dict[EID, Sample] = PrivateAttr(default={})

    def __getitem__(self, index: Union[int, str, UUID, EID]) -> Sample:
        if not self._samples:
            self._reload_samples()

        if isinstance(index, int):
            return self._samples[index]

        if isinstance(index, str):
            return self._samples_by_id[EID(index)]

        if isinstance(index, EID):
            return self._samples_by_id[index]

        raise IndexError('Invalid index')

    def __iter__(self):
        if not self._samples:
            self._reload_samples()
        return self._samples.__iter__()

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.SAMPLES_CONTAINER

    def get_content(self, format: Optional[SamplesContainerFormat] = None) -> File:
        """Get SamplesContainer content

        Returns:
            File
        """
        return super()._get_content(format=format)

    def _reload_samples(self) -> None:
        log.debug('Reloading samples for Samples Container: %s...', self.eid)

        self._samples = []
        self._samples_by_id = {}
        for item in self._get_samples():
            sample = cast(Sample, item)
            assert sample.eid

            self._samples.append(item)
            self._samples_by_id[sample.eid] = sample
        log.debug('Data in Samples Container: %s were reloaded', self.eid)

    def _get_samples(self) -> Generator[Sample, None, None]:
        log.debug('Getting samples for Samples Container: %s...', self.eid)
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(super()._get_endpoint(), self.eid, 'children'),
        )

        result = SamplesContainerResponse(**response.json())

        yield from [cast(ResponseData, item).body for item in result.data]

        while result.links and result.links.next:
            response = api.call(
                method='GET',
                path=result.links.next,
            )

            result = SamplesContainerResponse(**response.json())
            yield from [cast(ResponseData, item).body for item in result.data]
        log.debug('Samples for SamplesContainer: %s were got successfully.', self.eid)

    def save(self, force: bool = True) -> None:
        """Save SamplesContainer content.

        Args:
            force: Force to update content without doing digest check.

        Returns:

        """
        log.debug('Saving SamplesContainer: %s...', self.eid)
        for item in self._samples:
            item.save(force=force)
        self._reload_samples()
        log.debug('SamplesContainer: %s were saved successfully.', self.eid)

    def get_html(self) -> str:
        """Get in HTML format

        Returns:
            Rendered HTML in string format
        """
        file = self.get_content()
        content = StringIO(file.content.decode('utf-8'))
        csv_data = list(csv.reader(content))
        table_head = csv_data[0]
        rows = csv_data[1:]
        template = env.get_template(self._template_name)
        log.info('Html template for %s:%s has been rendered.', self.__class__.__name__, self.eid)

        return template.render(name=self.name, table_head=table_head, rows=rows)

    def dump(self, base_path: str, fs_handler: FSHandler, alias: Optional[List[str]] = None) -> None:
        """Dump SampleContainer

        Args:
            base_path: content path where create templates dump
            fs_handler: FSHandler
            alias: Backup alias

        Returns:

        """
        super().dump(base_path=base_path, fs_handler=fs_handler)

        samples_path = fs_handler.join_path(base_path, self.eid)
        for item in self:
            item.dump(base_path=samples_path, fs_handler=fs_handler)

    @classmethod
    def load(cls, path: str, fs_handler: FSHandler, parent: Container) -> None:
        """Load SampleContainer

        Args:
            path: content path where create templates dump
            fs_handler: FSHandler
            parent: Container where load SampleContainer entity and Samples

        Returns:

        """
        cls._load(path, fs_handler, parent)

    @classmethod
    def _load(cls, path: str, fs_handler: FSHandler, parent: Any) -> None:
        from signals_notebook.item_mapper import ItemMapper

        child_entities_folders = fs_handler.list_subfolders(path)
        for child_entity in child_entities_folders:
            child_entity_type = child_entity.split(':')[0]
            ItemMapper.get_item_class(child_entity_type)._load(
                fs_handler.join_path(path, child_entity), fs_handler, parent
            )
