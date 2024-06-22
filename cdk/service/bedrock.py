from pathlib import Path

from aws_cdk.aws_lambda_python_alpha import PythonFunction
from cdklabs.generative_ai_cdk_constructs.bedrock import (
    ActionGroupExecutor,
    Agent,
    AgentActionGroup,
    ApiSchema,
    BedrockFoundationModel,
)
from constructs import Construct


class BedrockAgentsConstruct(Construct):
    def __init__(self, scope: Construct, construct_id: str, action_group_function: PythonFunction, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        agent = Agent(
            self,
            'Agent',
            foundation_model=BedrockFoundationModel.ANTHROPIC_CLAUDE_INSTANT_V1_2,
            instruction='You are a helpful and friendly agent that answers questions about placing orders.',
            should_prepare_agent=True,
        )

        executor_group = ActionGroupExecutor(lambda_=action_group_function)
        root_dir = Path(__file__).parent.parent.parent
        openapi_path = Path(root_dir / 'docs' / 'swagger' / 'openapi.json')
        action_group = AgentActionGroup(
            self,
            'ActionGroup',
            action_group_name='OrdersPlacement',
            description='Use these functions for placing orders',
            action_group_executor=executor_group,
            action_group_state='ENABLED',
            api_schema=ApiSchema.from_asset(str(openapi_path)),
        )
        agent.add_action_group(action_group)
