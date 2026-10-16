---
title: Authentication
description: Amazon Cognito and the Powertools JWT verifier
---
The order API is protected with Amazon Cognito access tokens. Each Lambda function verifies the token itself with the Powertools for AWS Lambda [JWT verifier](https://github.com/aws-powertools/powertools-lambda-python/releases/tag/v3.36.0){:target="_blank" rel="noopener"} (`aws_lambda_powertools.utilities.auth_alpha.JWTVerifier`), there is no API Gateway authorizer.

!!! warning "Alpha utility"
    The `auth_alpha` utilities may change before they are generally available. Pin the Powertools version and install the extra: `aws-lambda-powertools[jwt]`.

## **How it works**

1. A caller signs in to the Cognito user pool and gets an access token.
2. The caller sends the token in the `Authorization: Bearer <token>` header.
3. The route middleware created by `verifier.require(scopes=[...])` verifies the signature (using the cached user pool JWKS), the issuer, the expiration, the app client and the audience, and checks the scope.
4. The response is `401` for a missing or invalid token (an ID token is rejected too) and `403` for a missing scope. The `/swagger` endpoints stay public.

| Route                                 | Required scope |
| ------------------------------------- | -------------- |
| `GET /api/orders`, `GET /api/orders/{order_id}` | `orders/read`  |
| `POST /api/orders`, `DELETE /api/orders/{order_id}` | `orders/write` |

## **Verifier and routes**

```python title="service/handlers/utils/auth.py"
--8<-- "service/handlers/utils/auth.py"
```

The verifier is created once per execution environment, so the JWKS is fetched once and reused by warm invocations.

The LIST function runs in the Lambda Managed Instances VPC, which has no internet access (and the Cognito VPC endpoint does not serve the JWKS), so it gets the JWKS at deploy time instead: a CloudFormation custom resource fetches it and passes it in the `COGNITO_JWKS` environment variable. A route uses it with `middlewares=REQUIRE_READ` or `middlewares=REQUIRE_WRITE`.

!!! note "Validation runs before authorization"
    The Event Handler validates the request before it runs route middleware. A caller without a token that sends an invalid body gets a `422` before it gets a `401`. A valid body gets the `401`.

## **The audience claim**

`JWTVerifier.cognito()` requires the `aud` claim of the access token to match the resource audience. Cognito only adds a resource bound `aud` to access tokens in Managed Login flows, not to tokens issued by the Cognito API (`AdminInitiateAuth`), and those tokens only have the `aws.cognito.signin.user.admin` scope.

To get tokens without a browser, the user pool has a [pre token generation trigger](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-pre-token-generation.html){:target="_blank" rel="noopener"} (event version 2, which requires the Essentials feature plan) that adds to the access token:

- `aud`, set to the app client id. This is the only value Cognito allows for `aud`.
- The scopes of the user's groups: `orders-readers` gets `orders/read`, `orders-writers` gets `orders/read` and `orders/write`.

```python title="service/handlers/handle_pre_token_generation.py"
--8<-- "service/handlers/handle_pre_token_generation.py"
```

The audience is therefore the app client id, which is weaker than a resource bound audience. If you use Managed Login, request resource binding and pass your resource URL as the `audience`.

## **Testing with real tokens**

The integration and e2e tests do not mock the verifier. They use real tokens from the deployed user pool.

- The helpers in `tests/auth_utils.py` create a user with the admin API, add it to a group, sign it in to get a real access token and delete it.
- The fixtures in `tests/conftest.py` create three users once per test session: `writer_user`, `reader_user` and `no_scope_user`. They are deleted when the session ends, also when a test fails.
- The bearer token is passed to the tests as ready to use `Authorization` headers: `writer_headers`, `reader_headers` and `no_scope_headers`.

The identity that runs the tests needs these permissions on the user pool: `cognito-idp:AdminCreateUser`, `AdminSetUserPassword`, `AdminAddUserToGroup`, `AdminInitiateAuth` and `AdminDeleteUser`.

## **More Details**

Go to [https://github.com/aws-powertools/powertools-lambda-python/releases/tag/v3.36.0](https://github.com/aws-powertools/powertools-lambda-python/releases/tag/v3.36.0){:target="_blank" rel="noopener"}
