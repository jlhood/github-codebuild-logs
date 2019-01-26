import pytest

import botocore

import s3link
import test_constants


@pytest.fixture
def mock_s3(mocker):
    mocker.patch.object(s3link, 'S3')
    return s3link.S3


@pytest.fixture
def mock_bucket(mocker):
    mocker.patch.object(s3link, 'BUCKET')
    return s3link.BUCKET


def test_get_presigned_url_none_key(mock_s3, mock_bucket):
    assert s3link.get_presigned_url(None) is None
    mock_bucket.Object.assert_not_called()
    mock_s3.generate_presigned_url.assert_not_called()


def test_get_presigned_url_key_not_found(mock_s3, mock_bucket):
    mock_bucket.Object.return_value.load.side_effect = botocore.exceptions.ClientError(
        {
            'Error': {
                'Code': '404'
            }
        }, None
    )

    assert s3link.get_presigned_url('foo') is None
    mock_bucket.Object.assert_called_with('foo')
    mock_s3.generate_presigned_url.assert_not_called()


def test_get_presigned_url_other_exception(mock_s3, mock_bucket):
    mock_bucket.Object.return_value.load.side_effect = botocore.exceptions.ClientError(
        {
            'Error': {
                'Code': 'boom!'
            }
        }, None
    )

    with pytest.raises(botocore.exceptions.ClientError):
        s3link.get_presigned_url('foo')

    mock_bucket.Object.assert_called_with('foo')
    mock_s3.generate_presigned_url.assert_not_called()


def test_get_presigned_url_key_exists(mock_s3, mock_bucket):
    mock_s3.generate_presigned_url.return_value = 'presigned-url'

    assert s3link.get_presigned_url('foo') == 'presigned-url'

    mock_bucket.Object.assert_called_with('foo')
    mock_bucket.Object.return_value.load.assert_called_with()
    mock_s3.generate_presigned_url.assert_called_with(
        ClientMethod='get_object',
        ExpiresIn=600,
        Params={
            'Bucket': test_constants.BUCKET_NAME,
            'Key': 'foo'
        }
    )
