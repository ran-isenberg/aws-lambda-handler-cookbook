---
title: Authentication & Authorization
description: Amazon Cognito, the Powertools JWT verifier, scopes and order ownership
---
The order API is protected with Amazon Cognito access tokens. Each Lambda function verifies the token itself with the Powertools for AWS Lambda [JWT verifier](https://github.com/aws-powertools/powertools-lambda-python/releases/tag/v3.36.0){:target="_blank" rel="noopener"} (`aws_lambda_powertools.utilities.auth_alpha.JWTVerifier`), there is no API Gateway authorizer.

Authorization has two levels: a scope per route, and order ownership, so users only reach their own orders.

!!! warning "Alpha utility"
    The `auth_alpha` utilities may change before they are generally available. Pin the Powertools version and install the extra: `aws-lambda-powertools[jwt]`.

## **How it works**

1. A caller signs in to the Cognito user pool and gets an access token.
2. The caller sends the token in the `Authorization: Bearer <token>` header.
3. The route middleware created by `verifier.require(scopes=[...])` verifies the signature (with the user pool JWKS), the issuer, the expiration, the app client and the audience, and checks the scope.
4. The response is `401` for a missing or invalid token (an ID token is rejected too) and `403` for a missing scope. The `/swagger` endpoints stay public.
5. The handler reads the caller's user id from the verified token and only reaches that user's orders, see [Order ownership](#order-ownership).

| Route                                               | Required scope |
| --------------------------------------------------- | -------------- |
| `GET /api/orders`, `GET /api/orders/{order_id}`     | `orders/read`  |
| `POST /api/orders`, `DELETE /api/orders/{order_id}` | `orders/write` |

## **Verifier and routes**

```python title="service/handlers/utils/auth.py"
--8<-- "service/handlers/utils/auth.py"
```

The verifier is created once per execution environment. It caches the user pool JWKS for 5 minutes (the Powertools default) and then fetches it again, so warm invocations don't download the keys on every request. A route uses the verifier with `middlewares=REQUIRE_READ` or `middlewares=REQUIRE_WRITE`.

The LIST function is the exception: it runs in the Lambda Managed Instances VPC, which has no route to the public JWKS URL. A CloudFormation custom resource fetches the JWKS at deploy time and passes it to the function in the `COGNITO_JWKS` environment variable,
and the verifier uses those keys instead of downloading them. A new user pool triggers the custom resource again, which fetches the new keys.

!!! warning "Signing key rotation"
    Cognito [might rotate](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html){:target="_blank" rel="noopener"} the signing keys of a user pool and does not publish a schedule.
    After a rotation the LIST function only has the keys fetched at deploy time, so it rejects new tokens with `401` until the next deployment fetches the new keys.
    A production service should refresh the keys periodically, for example with a scheduled function that stores the JWKS in SSM Parameter Store, read by the LIST function through a VPC endpoint.

!!! note "Validation runs before authorization"
    The Event Handler validates the request before it runs route middleware. A caller without a token that sends an invalid request gets a `422` before it gets a `401`. A valid request gets the `401`.

## **Order ownership**

Every order belongs to the user that created it, and users can only get, delete and list their own orders.

```python title="service/handlers/utils/caller.py"
--8<-- "service/handlers/utils/caller.py"
```

- The owner is the access token `sub` claim, read with `get_caller_id()` from the claims the auth middleware adds to the resolver context. `sub` is immutable and unique, unlike the username, which can be reused after a user is deleted.
- The orders table is keyed by `owner_id` (partition key) and `id` (sort key). Get and delete read the item by both keys, so an order of another user returns `404`, exactly like an order that does not exist. This does not reveal which order ids exist.
- List runs a strongly consistent `Query` on the caller's partition instead of a `Scan` of the whole table. A `next_token` of another user, or a forged one, returns `400`.
- The owner is part of the create order idempotency key, so the same request body sent by two users creates two orders.

!!! info "The reader role and ownership"
    Only writers can create orders, and users only see their own orders. A user in `orders-readers` alone therefore owns no orders: its get returns `404` and its list is empty.

    In this blueprint the reader role shows scope based authorization. A real service would give readers access to their own orders created by another process, or add a separate scope (for example support or admin) that can read across owners.

## **The audience claim**

`JWTVerifier.cognito()` requires the `aud` claim of the access token to match the resource audience. Cognito only adds a resource bound `aud` to access tokens in Managed Login flows, not to tokens issued by the Cognito API (`AdminInitiateAuth`), and those tokens only have the `aws.cognito.signin.user.admin` scope.

To get tokens without a browser, the user pool has a [pre token generation trigger](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-pre-token-generation.html){:target="_blank" rel="noopener"} (event version 2, which requires the Essentials feature plan) that adds to the access token:

- `aud`, set to the app client id.
- The scopes of the user's groups: `orders-readers` gets `orders/read`, `orders-writers` gets `orders/read` and `orders/write`.

```python title="service/handlers/handle_pre_token_generation.py"
--8<-- "service/handlers/handle_pre_token_generation.py"
```

The audience is therefore the app client id, which is weaker than a resource bound audience: every API that trusts this app client accepts the same token, so a token issued for one of them can be replayed against another. If you use Managed Login, request resource binding and pass your resource URL as the `audience`.

## **Testing with real tokens**

The integration and e2e tests do not mock the verifier. They use real tokens from the deployed user pool.

- The helpers in `tests/auth_utils.py` create a user with the admin API, add it to a group, sign it in to get a real access token and delete it.
- The fixtures in `tests/conftest.py` create four users once per test session: `writer_user`, `other_writer_user` (to test order ownership), `reader_user` and `no_scope_user`. They are deleted when the session ends, also when a test fails.
- The bearer token is passed to the tests as ready to use `Authorization` headers: `writer_headers`, `other_writer_headers`, `reader_headers` and `no_scope_headers`.
- `order_factory(owner, name, item_count)` creates orders owned by a test user (`owner.sub`) directly in DynamoDB.

The identity that runs the tests needs these permissions on the user pool: `cognito-idp:AdminCreateUser`, `AdminSetUserPassword`, `AdminAddUserToGroup`, `AdminInitiateAuth` and `AdminDeleteUser`.

## **More Details**

- [Powertools for AWS Lambda v3.36.0 release notes](https://github.com/aws-powertools/powertools-lambda-python/releases/tag/v3.36.0){:target="_blank" rel="noopener"}, which introduced the JWT verifier
- [Understanding the access token](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-access-token.html){:target="_blank" rel="noopener"} (Amazon Cognito)
- [Pre token generation Lambda trigger](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-pre-token-generation.html){:target="_blank" rel="noopener"} (Amazon Cognito)
- [Scopes, M2M, and resource servers](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-define-resource-servers.html){:target="_blank" rel="noopener"} (Amazon Cognito)
