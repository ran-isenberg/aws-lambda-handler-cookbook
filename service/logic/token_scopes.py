from typing import Any

# Deleting orders requires this scope. Creating, getting and listing your own orders only requires a valid access token.
MANAGE_SCOPE = 'orders/manage'

# Cognito user pool group -> scopes granted in the access token
GROUP_SCOPES: dict[str, tuple[str, ...]] = {
    'orders-managers': (MANAGE_SCOPE,),
}


def scopes_for_groups(groups: list[str]) -> list[str]:
    """Map user pool groups to access token scopes. Unknown groups grant nothing; result has no duplicates."""
    scopes: dict[str, None] = {}  # dict keeps insertion order
    for group in groups:
        for scope in GROUP_SCOPES.get(group, ()):
            scopes[scope] = None
    return list(scopes)


def access_token_customization(client_id: str, groups: list[str]) -> dict[str, Any]:
    """The 'response' of the Cognito pre token generation (V2) event.

    Adds the 'aud' claim (must equal the app client id, the only value Cognito accepts) and the scopes of the user's groups to the access token.
    Only the access token is customized: an empty 'groupOverrideDetails' would suppress the user's groups.
    """
    return {
        'claimsAndScopeOverrideDetails': {
            'accessTokenGeneration': {
                'claimsToAddOrOverride': {'aud': client_id},
                'scopesToAdd': scopes_for_groups(groups),
            },
        }
    }
