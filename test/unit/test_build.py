import pytest

import build
import test_constants

BUILD_ID = 'some-build'
BUILD_STATUS = 'SUCCEEDED'
LOG_GROUP_NAME = "log-group"
LOG_STREAM_NAME = "log-stream"


@pytest.fixture
def mock_codebuild(mocker):
    mocker.patch.object(build, 'CODEBUILD')
    return build.CODEBUILD


@pytest.fixture
def mock_cw_logs(mocker):
    mocker.patch.object(build, 'CW_LOGS')
    return build.CW_LOGS


@pytest.fixture
def mock_bucket(mocker):
    mocker.patch.object(build, 'BUCKET')
    return build.BUCKET


def test_init():
    build_obj = build.Build(_mock_build_event())
    assert build_obj.id == BUILD_ID
    assert build_obj.project_name == test_constants.PROJECT_NAME
    assert build_obj.status == BUILD_STATUS


def test_get_pr_id_not_pr(mocker, mock_codebuild):
    _mock_build_details('master')
    build_obj = build.Build(_mock_build_event())
    assert build_obj.get_pr_id() is None


def test_get_pr_id_is_pr(mocker, mock_codebuild):
    _mock_build_details('pr/123')
    build_obj = build.Build(_mock_build_event())
    assert build_obj.get_pr_id() == 123


def test_is_pr_build_not_pr(mocker, mock_codebuild):
    _mock_build_details('master')
    build_obj = build.Build(_mock_build_event())
    assert build_obj.is_pr_build() is False


def test_is_pr_build_is_pr(mocker, mock_codebuild):
    _mock_build_details('pr/123')
    build_obj = build.Build(_mock_build_event())
    assert build_obj.is_pr_build() is True


def test_copy_logs(mocker, mock_codebuild, mock_cw_logs, mock_bucket):
    mock_cw_logs.get_paginator.return_value.paginate.return_value = [
        {
            'events': [
                {
                    'message': 'foo',
                },
                {
                    'message': 'bar',
                }
            ]
        },
        {
            'events': [
                {
                    'message': 'baz',
                },
                {
                    'message': 'blah',
                }
            ]
        },
    ]
    _mock_build_details('pr/123')

    build_obj = build.Build(_mock_build_event())
    build_obj.copy_logs()

    mock_codebuild.batch_get_builds.assert_called_once_with(ids=[BUILD_ID])

    mock_cw_logs.get_paginator.assert_called_once_with('filter_log_events')
    mock_cw_logs.get_paginator.return_value.paginate.assert_called_once_with(
        logGroupName=LOG_GROUP_NAME,
        logStreamNames=[LOG_STREAM_NAME]
    )

    mock_bucket.put_object.assert_called_once_with(
        Key=LOG_STREAM_NAME + '/build.log',
        Body='foobarbazblah',
        ContentType="text/plain"
    )


def test_get_logs_url(mocker, mock_codebuild):
    mocker.patch.object(build, 'S3')
    build.S3.generate_presigned_url.return_value = 'url'
    _mock_build_details('pr/123')
    build_obj = build.Build(_mock_build_event())

    assert build_obj.get_logs_url() == 'url'

    build.S3.generate_presigned_url.assert_called_once_with(
        ClientMethod='get_object',
        ExpiresIn=test_constants.EXPIRATION_IN_DAYS * 3600 * 24,
        Params={
            'Bucket': test_constants.BUCKET_NAME,
            'Key': LOG_STREAM_NAME + '/build.log'
        }
    )


def _mock_build_event():
    return {
        'detail': {
            'build-id': BUILD_ID,
            'project-name': test_constants.PROJECT_NAME,
            'build-status': BUILD_STATUS
        }
    }


def _mock_build_details(source_version):
    build.CODEBUILD.batch_get_builds.return_value = {
        'builds': [
            {
                'sourceVersion': source_version,
                'logs': {
                    'groupName': LOG_GROUP_NAME,
                    'streamName': LOG_STREAM_NAME,
                }
            }
        ]
    }
