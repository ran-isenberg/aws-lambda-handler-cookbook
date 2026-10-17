from typing import Any

from service.handlers.handle_pre_token_generation import lambda_handler
from tests.utils import generate_context

# The pre token generation trigger is invoked by Cognito, so this calls its Lambda entry point like the other integration tests.
CLIENT_ID = '1example23456789'


def generate_pre_token_event(groups: list[str] | None) -> dict[str, Any]:
    group_configuration: dict[str, Any] = {} if groups is None else {'groupsToOverride': groups, 'iamRolesToOverride': [], 'preferredRole': None}
    return {
        'version': '2',
        'triggerSource': 'TokenGeneration_Authentication',
        'region': 'us-east-1',
        'userPoolId': 'us-east-1_EXAMPLE',
        'userName': 'tester',
        'callerContext': {'awsSdkVersion': 'aws-sdk-unknown-unknown', 'clientId': CLIENT_ID},
        'request': {
            'userAttributes': {'sub': 'a1b2c3d4-5678-90ab-cdef-EXAMPLE11111'},
            'groupConfiguration': group_configuration,
            'scopes': ['aws.cognito.signin.user.admin'],
        },
        'response': {'claimsAndScopeOverrideDetails': None},
    }


def test_adds_audience_and_scopes_of_the_users_groups():
    # Given: A token generation event of a user that is a member of the managers group
    event = generate_pre_token_event(['orders-managers'])

    # When: The trigger runs
    result = lambda_handler(event, generate_context())

    # Then: The access token gets the app client id as audience and the manage scope
    access_token = result['response']['claimsAndScopeOverrideDetails']['accessTokenGeneration']
    assert access_token['claimsToAddOrOverride'] == {'aud': CLIENT_ID}
    assert access_token['scopesToAdd'] == ['orders/manage']


def test_user_without_groups_gets_audience_but_no_scopes():
    # Given: A user that is not a member of any group (groupsToOverride is missing/empty in the event)
    for event in (generate_pre_token_event(None), generate_pre_token_event([])):
        # When: The trigger runs
        result = lambda_handler(event, generate_context())

        # Then: The audience is added, but no scope is granted (the user can still get and list their own orders)
        access_token = result['response']['claimsAndScopeOverrideDetails']['accessTokenGeneration']
        assert access_token['claimsToAddOrOverride'] == {'aud': CLIENT_ID}
        assert access_token['scopesToAdd'] == []


def test_does_not_override_groups_or_id_token():
    # Given: A token generation event
    event = generate_pre_token_event(['orders-managers'])

    # When: The trigger runs
    result = lambda_handler(event, generate_context())

    # Then: Only the access token is customized (an empty groupOverrideDetails would suppress the user's groups)
    assert list(result['response']['claimsAndScopeOverrideDetails']) == ['accessTokenGeneration']
