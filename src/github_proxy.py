"""Proxy for interacting with Github."""

import boto3
from github import Github

import config
import lambdalogging

LOG = lambdalogging.getLogger(__name__)

SAR_APP_URL = 'TODO'
SAR_HOMEPAGE = 'https://aws.amazon.com/serverless/serverlessrepo/'

PR_COMMENT_TEMPLATE = """
### AWS CodeBuild CI Report

* Result: {}
* [Build Logs]({}) (available for {} days)

*Powered by [github-codebuild-logs]({}), available on the [AWS Serverless Application Repository]({})*
"""

SSM = boto3.client('ssm')


class GithubProxy:
    """Encapsulate interactions with Github."""

    def __init__(self):
        """Initialize proxy."""
        pass

    def publish_pr_comment(self, build):
        """Publish PR comment with link to build logs."""
        pr_comment = PR_COMMENT_TEMPLATE.format(
            build.status,
            build.get_logs_url(),
            config.EXPIRATION_IN_DAYS,
            SAR_APP_URL,
            SAR_HOMEPAGE
        )
        LOG.debug('Publishing PR Comment: repo=%s/%s, pr_id=%s, comment=%s',
                  config.GITHUB_OWNER, config.GITHUB_REPO, build.get_pr_id(), pr_comment)

        repo = self._get_client().get_user(config.GITHUB_OWNER).get_repo(config.GITHUB_REPO)
        repo.get_pull(build.get_pr_id()).create_issue_comment(pr_comment)

    def _get_client(self):
        if not hasattr(self, '_client'):
            self._init_client()
        return self._client

    def _init_client(self):
        param_name = config.GITHUB_TOKEN_PARAMETER_NAME
        response = SSM.get_parameters(
            Names=[param_name],
            WithDecryption=True
        )
        if response['InvalidParameters']:
            raise RuntimeError(
                'Could not find expected SSM parameters containing Github token: {}'.format(param_name))

        github_token = response['Parameters'][0]['Value']
        self._client = Github(github_token)
