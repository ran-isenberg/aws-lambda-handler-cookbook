import json
from typing import Dict

import pytest
from app import handler, powertools_handler
from pydantic import ValidationError

ORDER = {
    "id": "abbcf84d-489e-4b60-bc4e-df2399a9f098",
    "description": "This is an order description",
    "items": [
        {
            "id": "1b67d0fc-c893-463c-80a0-1ff182767403",
            "quantity": 2,
            "description": "Laptop Model 1",
            "type": 'COMPUTER',
        },
        {
            "id": "aa95a311-e3e1-458c-99c6-089be4349703",
            "quantity": 5,
            "description": "Cable ST 1",
            "type": "ACCESSORIES",
        }
    ],
    "optional_field": "this is sometimes empty, sometimes not"
}


def create_sqs_event(body: Dict):
    return {
        "Records": [
            {
                "messageId": "4dec1221-adc7-4718-be30-61a51e50188a",
                "receiptHandle": "AQEBT1+7eqfovaBlc0Ls7W80Jn8TJRQQ5x75mOYMbI9mlu7Iq32HkmnH85ZOD18w1JqXTMpvW3k98pcC43N7uGsbUJmj2xhluQ/uD8/ENsSQ2RSOnvTbn7DxPiVkZbmfcZcGhDFWKpTfYWAt6s88+BG1DgLtGmsL/ZVekRNlVOH5n8rFRZ7E+UoBMrK3DZyb8EuGDMGMiZksbg6YwbaMzrBWpEgzHI4y85k3lFfOYaHplksg0lamQql+0evdsI6VNRK13nAKP7VtUfMYKx8SKxoDlRx2s7fYdrsw+fx1rO7XQOopNMNbvF9dfp7ZPF3Udt/rgGA/Gut0NWlJUuPKyM99iJx/3o2+WhoCegiuTksxjASFyjk+RNKJSS7A3dwbKruub47KcbrUg8+0aeHO2Cl+35x5oYvvwxewCFtVSwSiVpQ=",
                "body": json.dumps(body),
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1614012943241",
                    "SenderId": "AROAVDUMW4V4AHDL77CRK:amelnyk-Isengard",
                    "ApproximateFirstReceiveTimestamp": "1614012943242"
                },
                "messageAttributes": {},
                "md5OfBody": "098f6bcd4621d373cade4e832627b4f6",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:eu-central-1:351408678264:sam-app-OrderQueue-1QV3DHPPYMW9B",
                "awsRegion": "eu-central-1"
            }
        ]
    }


def test_lambda_handler():
    handler.lambda_handler(create_sqs_event(ORDER), None)


def test_malformed_input_handler():
    with pytest.raises(ValueError):
        handler.lambda_handler(create_sqs_event({"foo": "bar"}), None)


def test_lambda_handler_powertools():
    powertools_handler.lambda_handler(create_sqs_event(ORDER), None)


def test_lambda_handler_powertools_raises_validation_error():
    ORDER["items"][0]['quantity'] = -5
    with pytest.raises(ValidationError):
        powertools_handler.lambda_handler(create_sqs_event(ORDER), None)
