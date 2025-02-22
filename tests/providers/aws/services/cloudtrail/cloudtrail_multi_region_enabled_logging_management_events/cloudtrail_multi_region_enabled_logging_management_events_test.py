from unittest import mock

from boto3 import client
from moto import mock_cloudtrail, mock_s3

from tests.providers.aws.audit_info_utils import (
    AWS_ACCOUNT_ARN,
    AWS_ACCOUNT_NUMBER,
    AWS_REGION_US_EAST_1,
    set_mocked_aws_audit_info,
)


class Test_cloudtrail_multi_region_enabled_logging_management_events:
    @mock_cloudtrail
    def test_no_trails(self):
        from prowler.providers.aws.services.cloudtrail.cloudtrail_service import (
            Cloudtrail,
        )

        current_audit_info = set_mocked_aws_audit_info([AWS_REGION_US_EAST_1])

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=current_audit_info,
        ):
            with mock.patch(
                "prowler.providers.aws.services.cloudtrail.cloudtrail_multi_region_enabled_logging_management_events.cloudtrail_multi_region_enabled_logging_management_events.cloudtrail_client",
                new=Cloudtrail(current_audit_info),
            ):
                # Test Check
                from prowler.providers.aws.services.cloudtrail.cloudtrail_multi_region_enabled_logging_management_events.cloudtrail_multi_region_enabled_logging_management_events import (
                    cloudtrail_multi_region_enabled_logging_management_events,
                )

                check = cloudtrail_multi_region_enabled_logging_management_events()
                result = check.execute()
                assert len(result) == 1
                assert result[0].resource_id == AWS_ACCOUNT_NUMBER
                assert result[0].resource_arn == AWS_ACCOUNT_ARN
                assert result[0].region == AWS_REGION_US_EAST_1
                assert result[0].status == "FAIL"
                assert (
                    result[0].status_extended
                    == "No trail found with multi-region enabled and logging management events."
                )

    @mock_cloudtrail
    @mock_s3
    def test_compliant_trail_advanced_event_selector(self):
        cloudtrail_client_us_east_1 = client(
            "cloudtrail", region_name=AWS_REGION_US_EAST_1
        )
        s3_client_us_east_1 = client("s3", region_name=AWS_REGION_US_EAST_1)
        trail_name_us = "trail_test_us"
        bucket_name_us = "bucket_test_us"
        s3_client_us_east_1.create_bucket(Bucket=bucket_name_us)
        trail_us = cloudtrail_client_us_east_1.create_trail(
            Name=trail_name_us, S3BucketName=bucket_name_us, IsMultiRegionTrail=True
        )
        _ = cloudtrail_client_us_east_1.start_logging(Name=trail_name_us)
        _ = cloudtrail_client_us_east_1.put_event_selectors(
            TrailName=trail_name_us,
            AdvancedEventSelectors=[
                {
                    "Name": "Management events selector",
                    "FieldSelectors": [
                        {"Field": "eventCategory", "Equals": ["Management"]}
                    ],
                }
            ],
        )

        from prowler.providers.aws.services.cloudtrail.cloudtrail_service import (
            Cloudtrail,
        )

        current_audit_info = set_mocked_aws_audit_info([AWS_REGION_US_EAST_1])

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=current_audit_info,
        ):
            with mock.patch(
                "prowler.providers.aws.services.cloudtrail.cloudtrail_multi_region_enabled_logging_management_events.cloudtrail_multi_region_enabled_logging_management_events.cloudtrail_client",
                new=Cloudtrail(current_audit_info),
            ):
                # Test Check
                from prowler.providers.aws.services.cloudtrail.cloudtrail_multi_region_enabled_logging_management_events.cloudtrail_multi_region_enabled_logging_management_events import (
                    cloudtrail_multi_region_enabled_logging_management_events,
                )

                check = cloudtrail_multi_region_enabled_logging_management_events()
                result = check.execute()
                assert len(result) == 1
                assert result[0].resource_id == trail_name_us
                assert result[0].resource_arn == trail_us["TrailARN"]
                assert result[0].region == AWS_REGION_US_EAST_1
                assert result[0].status == "PASS"
                assert (
                    result[0].status_extended
                    == f"Trail {trail_name_us} from home region {AWS_REGION_US_EAST_1} is multi-region, is logging and have management events enabled."
                )

    @mock_cloudtrail
    @mock_s3
    def test_non_compliant_trail_advanced_event_selector(self):
        cloudtrail_client_us_east_1 = client(
            "cloudtrail", region_name=AWS_REGION_US_EAST_1
        )
        s3_client_us_east_1 = client("s3", region_name=AWS_REGION_US_EAST_1)
        trail_name_us = "trail_test_us"
        bucket_name_us = "bucket_test_us"
        s3_client_us_east_1.create_bucket(Bucket=bucket_name_us)
        _ = cloudtrail_client_us_east_1.create_trail(
            Name=trail_name_us, S3BucketName=bucket_name_us, IsMultiRegionTrail=True
        )
        _ = cloudtrail_client_us_east_1.start_logging(Name=trail_name_us)
        _ = cloudtrail_client_us_east_1.put_event_selectors(
            TrailName=trail_name_us,
            AdvancedEventSelectors=[
                {
                    "Name": "Management events selector",
                    "FieldSelectors": [
                        {"Field": "eventCategory", "Equals": ["Managment"]},
                        {"Field": "readOnly", "Equals": ["true"]},
                    ],
                }
            ],
        )

        from prowler.providers.aws.services.cloudtrail.cloudtrail_service import (
            Cloudtrail,
        )

        current_audit_info = set_mocked_aws_audit_info([AWS_REGION_US_EAST_1])

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=current_audit_info,
        ):
            with mock.patch(
                "prowler.providers.aws.services.cloudtrail.cloudtrail_multi_region_enabled_logging_management_events.cloudtrail_multi_region_enabled_logging_management_events.cloudtrail_client",
                new=Cloudtrail(current_audit_info),
            ):
                # Test Check
                from prowler.providers.aws.services.cloudtrail.cloudtrail_multi_region_enabled_logging_management_events.cloudtrail_multi_region_enabled_logging_management_events import (
                    cloudtrail_multi_region_enabled_logging_management_events,
                )

                check = cloudtrail_multi_region_enabled_logging_management_events()
                result = check.execute()
                assert result[0].resource_id == AWS_ACCOUNT_NUMBER
                assert result[0].resource_arn == AWS_ACCOUNT_ARN
                assert result[0].region == AWS_REGION_US_EAST_1
                assert result[0].status == "FAIL"
                assert (
                    result[0].status_extended
                    == "No trail found with multi-region enabled and logging management events."
                )

    @mock_cloudtrail
    @mock_s3
    def test_compliant_trail_classic_event_selector(self):
        cloudtrail_client_us_east_1 = client(
            "cloudtrail", region_name=AWS_REGION_US_EAST_1
        )
        s3_client_us_east_1 = client("s3", region_name=AWS_REGION_US_EAST_1)
        trail_name_us = "trail_test_us"
        bucket_name_us = "bucket_test_us"
        s3_client_us_east_1.create_bucket(Bucket=bucket_name_us)
        trail_us = cloudtrail_client_us_east_1.create_trail(
            Name=trail_name_us, S3BucketName=bucket_name_us, IsMultiRegionTrail=True
        )
        _ = cloudtrail_client_us_east_1.start_logging(Name=trail_name_us)
        _ = cloudtrail_client_us_east_1.put_event_selectors(
            TrailName=trail_name_us,
            EventSelectors=[
                {
                    "ReadWriteType": "All",
                    "IncludeManagementEvents": True,
                    "DataResources": [],
                }
            ],
        )

        from prowler.providers.aws.services.cloudtrail.cloudtrail_service import (
            Cloudtrail,
        )

        current_audit_info = set_mocked_aws_audit_info([AWS_REGION_US_EAST_1])

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=current_audit_info,
        ):
            with mock.patch(
                "prowler.providers.aws.services.cloudtrail.cloudtrail_multi_region_enabled_logging_management_events.cloudtrail_multi_region_enabled_logging_management_events.cloudtrail_client",
                new=Cloudtrail(current_audit_info),
            ):
                # Test Check
                from prowler.providers.aws.services.cloudtrail.cloudtrail_multi_region_enabled_logging_management_events.cloudtrail_multi_region_enabled_logging_management_events import (
                    cloudtrail_multi_region_enabled_logging_management_events,
                )

                check = cloudtrail_multi_region_enabled_logging_management_events()
                result = check.execute()
                assert len(result) == 1
                assert result[0].resource_id == trail_name_us
                assert result[0].resource_arn == trail_us["TrailARN"]
                assert result[0].region == AWS_REGION_US_EAST_1
                assert result[0].status == "PASS"
                assert (
                    result[0].status_extended
                    == f"Trail {trail_name_us} from home region {AWS_REGION_US_EAST_1} is multi-region, is logging and have management events enabled."
                )

    @mock_cloudtrail
    @mock_s3
    def test_non_compliant_trail_classic_event_selector(self):
        cloudtrail_client_us_east_1 = client(
            "cloudtrail", region_name=AWS_REGION_US_EAST_1
        )
        s3_client_us_east_1 = client("s3", region_name=AWS_REGION_US_EAST_1)
        trail_name_us = "trail_test_us"
        bucket_name_us = "bucket_test_us"
        s3_client_us_east_1.create_bucket(Bucket=bucket_name_us)
        _ = cloudtrail_client_us_east_1.create_trail(
            Name=trail_name_us, S3BucketName=bucket_name_us, IsMultiRegionTrail=True
        )
        _ = cloudtrail_client_us_east_1.start_logging(Name=trail_name_us)
        _ = cloudtrail_client_us_east_1.put_event_selectors(
            TrailName=trail_name_us,
            EventSelectors=[
                {
                    "ReadWriteType": "ReadOnly",
                    "IncludeManagementEvents": False,
                    "DataResources": [],
                }
            ],
        )

        from prowler.providers.aws.services.cloudtrail.cloudtrail_service import (
            Cloudtrail,
        )

        current_audit_info = set_mocked_aws_audit_info([AWS_REGION_US_EAST_1])

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=current_audit_info,
        ):
            with mock.patch(
                "prowler.providers.aws.services.cloudtrail.cloudtrail_multi_region_enabled_logging_management_events.cloudtrail_multi_region_enabled_logging_management_events.cloudtrail_client",
                new=Cloudtrail(current_audit_info),
            ):
                # Test Check
                from prowler.providers.aws.services.cloudtrail.cloudtrail_multi_region_enabled_logging_management_events.cloudtrail_multi_region_enabled_logging_management_events import (
                    cloudtrail_multi_region_enabled_logging_management_events,
                )

                check = cloudtrail_multi_region_enabled_logging_management_events()
                result = check.execute()
                assert result[0].resource_id == AWS_ACCOUNT_NUMBER
                assert result[0].resource_arn == AWS_ACCOUNT_ARN
                assert result[0].region == AWS_REGION_US_EAST_1
                assert result[0].status == "FAIL"
                assert (
                    result[0].status_extended
                    == "No trail found with multi-region enabled and logging management events."
                )
