import json
from http import HTTPStatus
from typing import Any, Dict


def build_response(http_status: HTTPStatus, body: Dict[str, Any]) -> Dict[str, Any]:
    return {'statusCode': http_status, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps(body)}
