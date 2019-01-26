"""Generate S3 link for an object."""

import boto3
import botocore

import config
import lambdalogging

LOG = lambdalogging.getLogger(__name__)
S3 = boto3.client('s3')
BUCKET = boto3.resource('s3').Bucket(config.BUCKET_NAME)


def get_presigned_url(key):
    """Generate presigned URL for given object key if it exists."""
    if not key:
        return None

    try:
        BUCKET.Object(key).load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return None
        raise

    return S3.generate_presigned_url(
        ClientMethod='get_object',
        ExpiresIn=600,  # 10 minutes
        Params={
                'Bucket': config.BUCKET_NAME,
                'Key': key
        }
    )
