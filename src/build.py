"""Build log processing."""

import re
import boto3

import config
import lambdalogging

LOG = lambdalogging.getLogger(__name__)

CODEBUILD = boto3.client('codebuild')
CW_LOGS = boto3.client('logs')
S3 = boto3.resource('s3')
BUCKET = S3.Bucket(config.BUCKET_NAME)


class Build:
    """Encapsulate logic around CodeBuild builds and copying logs."""

    def __init__(self, build_event):
        """Create new Build helper object."""
        self._build_event = build_event
        self.id = build_event['detail']['build-id']
        self.project_name = build_event['detail']['project-name']
        self.status = build_event['detail']['build-status']

    def get_pr_id(self):
        """If this build was for a PR branch, returns the PR ID, otherwise returns None."""
        matches = re.match(r'^pr\/(\d+)', self._get_build_details()['sourceVersion'])
        if not matches:
            return None
        return int(matches.group(1))

    def is_pr_build(self):
        """Return True if this build is associated with a PR."""
        return self.get_pr_id() is not None

    def copy_logs(self):
        """Copy build logs to app S3 bucket and return a URL."""
        log_info = self._get_build_details()['logs']
        log_group = log_info['groupName']
        log_stream = log_info['streamName']
        paginator = CW_LOGS.get_paginator('filter_log_events')

        iter = paginator.paginate(
            logGroupName=log_group,
            logStreamNames=[log_stream]
        )
        logs_content = ''.join([event['message'] for page in iter for event in page['events']])

        BUCKET.put_object(
            Key=self._get_logs_key(),
            Body=logs_content,
            ContentType='text/plain'
        )

    def get_logs_url(self):
        """Return S3 URL to build logs."""
        return 'https://s3.{}.amazonaws.com/{}/{}'.format(
            config.REGION, config.BUCKET_NAME, self._get_logs_key()
        )

    def _get_logs_key(self):
        log_stream = self._get_build_details()['logs']['streamName']
        return '{}/build.log'.format(log_stream)

    def _get_build_details(self):
        if not hasattr(self, '_build_details'):
            response = CODEBUILD.batch_get_builds(ids=[self.id])
            self._build_details = response['builds'][0]
            LOG.debug('Build %s details: %s', self.id, self._build_details)
        return self._build_details
