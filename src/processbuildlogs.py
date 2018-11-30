"""Lambda function handler."""

# must be the first import in files with lambda function handlers
import lambdainit  # noqa: F401

import re
import boto3

import config
import lambdalogging

SAR_APP_URL = 'TODO'
SAR_HOMEPAGE = 'https://aws.amazon.com/serverless/serverlessrepo/'

LOG = lambdalogging.getLogger(__name__)
CODEBUILD = boto3.client('codebuild')
CW_LOGS = boto3.client('logs')
S3 = boto3.resource('s3')
BUCKET = S3.Bucket(config.BUCKET_NAME)


def handler(build_event, context):
    """Process build events.

    If the build event is for the CodeBuild project this app is managing and it's specifically triggered by a PR, pull
    logs for the build, copy them to the build logs S3 bucket, and post a link to the logs as a comment on the GitHub
    PR.
    """
    LOG.debug('Received event: %s', build_event)

    if build_event['detail']['project-name'] != config.PROJECT_NAME:
        LOG.debug('Not our codebuild project')
        return False

    build_id = build_event['detail']['build-id']
    build_details = _get_build(build_id)
    LOG.debug('Build %s details: %s', build_id, build_details)
    if not _is_pr_build(build_details):
        LOG.debug('Not a PR build')
        return

    build_logs_url = _copy_build_logs(build_details)
    _publish_pr_comment(build_details, build_logs_url)


def _get_build(build_id):
    response = CODEBUILD.batch_get_builds(ids=[build_id])
    return response['builds'][0]


def _is_pr_build(build_details):
    return re.match(r'^pr\/\d+', build_details['sourceVersion'])


def _copy_build_logs(build_details):
    log_group = build_details['logs']['groupName']
    log_stream = build_details['logs']['streamName']
    paginator = CW_LOGS.get_paginator('filter_log_events')

    iter = paginator.paginate(
        logGroupName=log_group,
        logStreamNames=[log_stream]
    )
    logs_content = ''.join([event['message'] for page in iter for event in page['events']])

    key = '{}/build.log'.format(log_stream)
    BUCKET.put_object(
        Key=key,
        Body=logs_content,
        ContentType='text/plain'
    )

    return 'https://s3.{}.amazonaws.com/{}/{}'.format(
        config.REGION, config.BUCKET_NAME, key
    )


def _publish_pr_comment(build_details, build_logs_url):
    pr_comment = """### AWS CodeBuild CI Report

    * Result: {}
    * [Build Logs]({}) (available for {} days)

    *Powered by [github-codebuild-logs]({}), available on the [AWS Serverless Application Repository]({})*
    """.format(
        build_details['buildStatus'],
        build_logs_url,
        config.EXPIRATION_IN_DAYS,
        SAR_APP_URL,
        SAR_HOMEPAGE
    )
    LOG.debug('PR Comment: {}'.format(pr_comment))

    # TODO: actually publish the PR comment to GitHub
