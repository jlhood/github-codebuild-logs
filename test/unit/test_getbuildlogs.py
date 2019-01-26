import pytest
import json

import getbuildlogs
import test_constants


@pytest.fixture
def mock_s3link(mocker):
    mocker.patch.object(getbuildlogs, 's3link')
    return getbuildlogs.s3link


def test_handler_no_log_key(mock_s3link):
    api_event = _mock_api_event()
    response = getbuildlogs.handler(api_event, None)

    assert response == {
        'statusCode': 400,
        'headers': {},
        'body': json.dumps({
            'error': 'missing expected query parameter: key'
        })
    }

    mock_s3link.get_presigned_url.assert_not_called()


def test_handler_log_key_no_exist(mock_s3link):
    mock_s3link.get_presigned_url.return_value = None

    api_event = _mock_api_event({'key': 'no_exist'})
    response = getbuildlogs.handler(api_event, None)

    assert response == {
        'statusCode': 404,
        'headers': {},
        'body': None
    }

    mock_s3link.get_presigned_url.assert_called_with('no_exist')


def test_handler_happycase(mock_s3link):
    mock_s3link.get_presigned_url.return_value = 'url'

    api_event = _mock_api_event({'key': 'foo%2Fbuild.log'})
    response = getbuildlogs.handler(api_event, None)

    assert response == {
        'statusCode': 307,
        'headers': {
            'Location': 'url'
        },
        'body': None
    }

    mock_s3link.get_presigned_url.assert_called_with('foo/build.log')


def _mock_api_event(query_parameters={}):
    return {
        'queryStringParameters': query_parameters
    }
