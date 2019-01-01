"""Lambda function handler for processing build events."""

# must be the first import in files with lambda function handlers
import lambdainit  # noqa: F401

from build import Build
import config
from github_proxy import GithubProxy
import lambdalogging

LOG = lambdalogging.getLogger(__name__)

GITHUB = GithubProxy()


def handler(build_event, context):
    """Process build events.

    If the build event is for the CodeBuild project this app is managing and it's specifically triggered by a PR, copy
    copy the build logs to the app S3 bucket and post a link to the logs as a comment on the GitHub PR.
    """
    LOG.debug('Received event: %s', build_event)

    build = Build(build_event)
    if build.project_name != config.PROJECT_NAME:
        LOG.debug('Not our codebuild project')
        return

    if not build.is_pr_build():
        LOG.debug('Not a PR build')
        return

    LOG.info('Copying build logs for PR build: project=%s, pr_id=%s, build_logs_url=%s',
             build.project_name, build.get_pr_id(), build.get_logs_url())
    build.copy_logs()

    GITHUB.publish_pr_comment(build)
