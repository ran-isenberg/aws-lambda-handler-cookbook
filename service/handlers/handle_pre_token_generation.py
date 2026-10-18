from typing import Any

from service.logic.token_scopes import access_token_customization


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Cognito pre token generation (V2) trigger, see access_token_customization.

    This function is deployed without the common layer, so it must not import third party packages.
    """
    client_id: str = event['callerContext']['clientId']
    groups: list[str] = event.get('request', {}).get('groupConfiguration', {}).get('groupsToOverride') or []
    event['response'] = access_token_customization(client_id, groups)
    return event
