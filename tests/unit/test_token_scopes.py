import pytest

from cdk.service.constants import READ_SCOPE, READERS_GROUP, WRITE_SCOPE, WRITERS_GROUP
from service.logic.token_scopes import GROUP_SCOPES, access_token_customization, scopes_for_groups


def test_cdk_and_service_agree_on_groups_and_scopes():
    # Given: The group and scope names defined in the CDK constants (user pool) and in the service (trigger logic)
    # When & Then: They are the same, otherwise the deployed groups would not grant any scope
    assert set(GROUP_SCOPES) == {READERS_GROUP, WRITERS_GROUP}
    assert GROUP_SCOPES[READERS_GROUP] == (READ_SCOPE,)
    assert GROUP_SCOPES[WRITERS_GROUP] == (READ_SCOPE, WRITE_SCOPE)


@pytest.mark.parametrize(
    'groups, expected',
    [
        ([READERS_GROUP], [READ_SCOPE]),
        ([WRITERS_GROUP], [READ_SCOPE, WRITE_SCOPE]),
        ([READERS_GROUP, WRITERS_GROUP], [READ_SCOPE, WRITE_SCOPE]),  # no duplicate read scope
        (['unknown-group'], []),
        ([READERS_GROUP, 'unknown-group'], [READ_SCOPE]),
        ([], []),
    ],
)
def test_scopes_for_groups(groups, expected):
    # Given: The user pool groups of a user
    # When: Mapping them to access token scopes
    scopes = scopes_for_groups(groups)

    # Then: Only known groups grant scopes, without duplicates
    assert scopes == expected


def test_access_token_customization_adds_audience_and_scopes():
    # Given: A client id and a user in the writers group
    # When: Building the pre token generation response
    response = access_token_customization('1example23456789', [WRITERS_GROUP])

    # Then: The access token gets the client id as audience and the read and write scopes
    access_token = response['claimsAndScopeOverrideDetails']['accessTokenGeneration']
    assert access_token['claimsToAddOrOverride'] == {'aud': '1example23456789'}
    assert access_token['scopesToAdd'] == [READ_SCOPE, WRITE_SCOPE]


def test_access_token_customization_only_customizes_the_access_token():
    # Given: A user in the readers group
    # When: Building the pre token generation response
    response = access_token_customization('1example23456789', [READERS_GROUP])

    # Then: The ID token and the groups are untouched
    assert list(response['claimsAndScopeOverrideDetails']) == ['accessTokenGeneration']
