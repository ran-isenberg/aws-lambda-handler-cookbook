from typing import Any, Dict, List
from pydantic import BaseModel
from aws_lambda_powertools.utilities.parser.models import EventBridgeModel
from aws_lambda_powertools.utilities.parser import parse, event_parser

    """In this example we want to use an attribute from the EventBridge envelope, the region string and also to use our payload UserModel data. 
       However, if we parse as before by usig the envelope parameter (envelope=EventBridgeEnvelope) we dont have access to the envelope parameters.
       This file shows how to get around that. Notice that we define 'detail' in MyEventBridgeModel as UserModel and extend EventBridgeModel. 
       we redefine detail to be UserModel intead of Dict (as it's defined in EventBridgeModel) to get an automatic parse and we extend the model so we could get all the envelope attributes for free.
    """


class UserModel(BaseModel):
    username: str
    password1: str
    password2: str

class MyEventBridgeModel(EventBridgeModel):
    detail: UserModel



@event_parser(model=UserModel, envelope=EventBridgeEnvelope)
def handle_eventbridge_with_decorator_with_envelope_cant_access_region_parameter(event: UserModel, context: LambdaContext) -> None:
    print(f'username={event.username}')
    # cant print region from EventBridgeModel :(


@event_parser(model=MyEventBridgeModel)
def handle_eventbridge_with_decorator_no_envelope_use_extended_model(event: MyEventBridgeModel, context: LambdaContext) -> None:
    print(f'eventbridge_region= {event.region}, username={event.detail.username}')
    

# When you dont use the decorator, you have more power over the excpetion handling
def handle_eventbridge_with_parse_no_envelope_no_decorator(event: Dict[str, Optional[Any]], context: LambdaContext) -> None:
    try:
       parsed_event: MyEventBridgeModel = parse(model=MyEventBridgeModel, event=event)
       print(f'eventbridge_region= {parsed_event.region}, username={parsed_event.detail.username}')
    except ValidationError:
        # handle
        raise 
    