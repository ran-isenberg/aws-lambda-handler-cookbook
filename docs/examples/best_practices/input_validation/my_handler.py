from http import HTTPStatus
from typing import Any

from aws_lambda_powertools.utilities.parser import ValidationError, parse
from aws_lambda_powertools.utilities.parser.envelopes import ApiGatewayEnvelope
from aws_lambda_powertools.utilities.typing import LambdaContext

from .schema import Input


def my_handler(event: dict[str, Any], context: LambdaContext):
    try:
        input: Input = parse(event=event, model=Input, envelope=ApiGatewayEnvelope)  # noqa: F841
    except (ValidationError, TypeError):
        # log error, return BAD_REQUEST
        return {'statusCode': HTTPStatus.BAD_REQUEST}
    # process input
