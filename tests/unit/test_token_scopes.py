import pytest

from cdk.service.constants import MANAGE_SCOPE, MANAGERS_GROUP
from service.logic.token_scopes import GROUP_SCOPES, access_token_customization, scopes_for_groups


def test_cdk_and_service_agree_on_groups_and_scopes():
    # Given: The group and scope names defined in the CDK constants (user pool) and in the service (trigger logic)
    # When & Then: They are the same, otherwise the deployed group would not grant the manage scope
    assert GROUP_SCOPES == {MANAGERS_GROUP: (MANAGE_SCOPE,)}


@pytest.mark.parametrize(
    'groups, expected',
    [
        ([MANAGERS_GROUP], [MANAGE_SCOPE]),
        ([MANAGERS_GROUP, MANAGERS_GROUP], [MANAGE_SCOPE]),  # no duplicate scope
        (['unknown-group'], []),
        ([MANAGERS_GROUP, 'unknown-group'], [MANAGE_SCOPE]),
        ([], []),  # a user in no group: can still get and list their own orders, which need no scope
    ],
)
def test_scopes_for_groups(groups, expected):
    # Given: The user pool groups of a user
    # When: Mapping them to access token scopes
    scopes = scopes_for_groups(groups)

    # Then: Only known groups grant scopes, without duplicates
    assert scopes == expected


def test_access_token_customization_adds_audience_and_scopes():
    # Given: A client id and a user in the managers group
    # When: Building the pre token generation response
    response = access_token_customization('1example23456789', [MANAGERS_GROUP])

    # Then: The access token gets the client id as audience and the manage scope
    access_token = response['claimsAndScopeOverrideDetails']['accessTokenGeneration']
    assert access_token['claimsToAddOrOverride'] == {'aud': '1example23456789'}
    assert access_token['scopesToAdd'] == [MANAGE_SCOPE]


def test_access_token_customization_only_customizes_the_access_token():
    # Given: A user in the managers group
    # When: Building the pre token generation response
    response = access_token_customization('1example23456789', [MANAGERS_GROUP])

    # Then: The ID token and the groups are untouched
    assert list(response['claimsAndScopeOverrideDetails']) == ['accessTokenGeneration']
