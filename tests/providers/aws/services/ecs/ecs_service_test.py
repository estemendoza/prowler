from unittest.mock import patch

from boto3 import client
from moto import mock_ecs

from prowler.providers.aws.services.ecs.ecs_service import ECS
from tests.providers.aws.audit_info_utils import (
    AWS_REGION_EU_WEST_1,
    set_mocked_aws_audit_info,
)


def mock_generate_regional_clients(service, audit_info):
    regional_client = audit_info.audit_session.client(
        service, region_name=AWS_REGION_EU_WEST_1
    )
    regional_client.region = AWS_REGION_EU_WEST_1
    return {AWS_REGION_EU_WEST_1: regional_client}


@patch(
    "prowler.providers.aws.lib.service.service.generate_regional_clients",
    new=mock_generate_regional_clients,
)
class Test_ECS_Service:
    # Test ECS Service
    def test_service(self):
        audit_info = set_mocked_aws_audit_info()
        ecs = ECS(audit_info)
        assert ecs.service == "ecs"

    # Test ECS client
    def test_client(self):
        audit_info = set_mocked_aws_audit_info()
        ecs = ECS(audit_info)
        for reg_client in ecs.regional_clients.values():
            assert reg_client.__class__.__name__ == "ECS"

    # Test ECS session
    def test__get_session__(self):
        audit_info = set_mocked_aws_audit_info()
        ecs = ECS(audit_info)
        assert ecs.session.__class__.__name__ == "Session"

    # Test list ECS task definitions
    @mock_ecs
    def test__list_task_definitions__(self):
        ecs_client = client("ecs", region_name=AWS_REGION_EU_WEST_1)

        definition = dict(
            family="test_ecs_task",
            containerDefinitions=[
                {
                    "name": "hello_world",
                    "image": "hello-world:latest",
                    "memory": 400,
                }
            ],
        )

        task_definition = ecs_client.register_task_definition(**definition)
        audit_info = set_mocked_aws_audit_info()
        ecs = ECS(audit_info)

        assert len(ecs.task_definitions) == 1
        assert (
            ecs.task_definitions[0].name == task_definition["taskDefinition"]["family"]
        )
        assert (
            ecs.task_definitions[0].arn
            == task_definition["taskDefinition"]["taskDefinitionArn"]
        )
        assert ecs.task_definitions[0].environment_variables == []

    @mock_ecs
    # Test describe ECS task definitions
    def test__describe_task_definitions__(self):
        ecs_client = client("ecs", region_name=AWS_REGION_EU_WEST_1)

        definition = dict(
            family="test_ecs_task",
            containerDefinitions=[
                {
                    "name": "hello_world",
                    "image": "hello-world:latest",
                    "memory": 400,
                    "environment": [
                        {"name": "test-env", "value": "test-env-value"},
                        {"name": "test-env2", "value": "test-env-value2"},
                    ],
                }
            ],
            tags=[
                {"key": "test", "value": "test"},
            ],
        )

        task_definition = ecs_client.register_task_definition(**definition)
        audit_info = set_mocked_aws_audit_info()
        ecs = ECS(audit_info)

        assert len(ecs.task_definitions) == 1
        assert (
            ecs.task_definitions[0].name == task_definition["taskDefinition"]["family"]
        )
        assert ecs.task_definitions[0].tags == [
            {"key": "test", "value": "test"},
        ]
        assert (
            ecs.task_definitions[0].arn
            == task_definition["taskDefinition"]["taskDefinitionArn"]
        )
        assert (
            ecs.task_definitions[0].environment_variables[0].name
            == task_definition["taskDefinition"]["containerDefinitions"][0][
                "environment"
            ][0]["name"]
        )
        assert (
            ecs.task_definitions[0].environment_variables[0].value
            == task_definition["taskDefinition"]["containerDefinitions"][0][
                "environment"
            ][0]["value"]
        )
        assert (
            ecs.task_definitions[0].environment_variables[1].name
            == task_definition["taskDefinition"]["containerDefinitions"][0][
                "environment"
            ][1]["name"]
        )
        assert (
            ecs.task_definitions[0].environment_variables[1].value
            == task_definition["taskDefinition"]["containerDefinitions"][0][
                "environment"
            ][1]["value"]
        )
