from typing import List

import requests
from pydantic import BaseModel, parse_obj_as, PydanticValueError


class ErrorBody(BaseModel):
    status: str
    code: str
    title: str = ''
    detail: str = ''


class ErrorResponse(BaseModel):
    errors: List[ErrorBody]


class SignalsNotebookError(Exception):
    def __init__(self, response: requests.Response):
        """Handle Signals Notebook API errors

        Args:
            response: Response object, which contains a server's response to an HTTP request.
        """
        self.parsed_response = parse_obj_as(ErrorResponse, response.json())

    def __str__(self) -> str:
        error = self.parsed_response.errors[0]
        return (
            f'<SignalsNotebookError status={error.status} code={error.code}> title={error.title} detail={error.detail}>'
        )


class EIDError(PydanticValueError):
    msg_template = 'incorrect EID value: "{value}"'


class BulkExportJobAlreadyRunningError(Exception):
    def __init__(self, message=None):
        super().__init__(message)

    def __str__(self) -> str:
        return 'Only one Bulk Export job can be processed at a time'
