"""Lambda function handler for processing build events."""

# must be the first import in files with lambda function handlers
import lambdainit  # noqa: F401

import json
from urllib.parse import unquote_plus

import lambdalogging
import s3link

LOG = lambdalogging.getLogger(__name__)


def handler(api_event, context):
    """Handle GET /buildlogs request.

    Redirects to pre-signed URL to build logs.
    """
    LOG.debug('Received event: %s', api_event)
    log_key = api_event.get('queryStringParameters', {}).get('key')

    if not log_key:
        return _bad_request('missing expected query parameter: key')

    redirect_link = s3link.get_presigned_url(unquote_plus(log_key))
    LOG.debug('redirect_link: %s', redirect_link)

    if redirect_link:
        return _redirect(redirect_link)
    else:
        return _not_found()


def _bad_request(message):
    return _response(
        status_code=400,
        body=json.dumps({'error': message})
    )


def _not_found():
    return _response(status_code=404)


def _redirect(redirect_link):
    return _response(
        status_code=307,
        headers={
            'Location': redirect_link
        }
    )


def _response(status_code=200, headers={}, body=None):
    response = {
        'statusCode': status_code,
        'headers': headers,
        'body': body
    }
    LOG.debug('response: %s', response)
    return response
