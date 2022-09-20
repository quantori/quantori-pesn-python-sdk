import logging
from typing import cast, Union

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import MID, Response, ResponseData
from signals_notebook.materials.asset import Asset
from signals_notebook.materials.batch import Batch
from signals_notebook.materials.library import Library
from signals_notebook.materials.material import Material

log = logging.getLogger(__name__)


class MaterialResponse(Response[Union[Library, Asset, Batch]]):
    pass


class MaterialStore:
    @classmethod
    def _get_endpoint(cls) -> str:
        return 'materials'

    @classmethod
    def get(cls, eid: MID) -> Material:
        """Fetch material by entity ID.

        Args:
            eid: Unique material identifier

        Returns:
            Material
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get Material Store for %s', eid)

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(), eid),
        )

        result = MaterialResponse(**response.json())

        return cast(ResponseData, result.data).body
