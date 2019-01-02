import pytest
from unittest.mock import MagicMock

import github_proxy
import test_constants

GITHUB_TOKEN = "shhh!!"
BUILD_STATUS = 'SUCCEEDED'
PR_ID = 5
LOGS_URL = 'https://foo.com'


@pytest.fixture
def mock_ssm(mocker):
    mocker.patch.object(github_proxy, 'SSM')
    github_proxy.SSM.get_parameters.return_value = {
        'Parameters': [
            {
                'Name': '/{}/github_token'.format(test_constants.GITHUB_TOKEN_SSM_PARAMETER_PREFIX),
                'Value': GITHUB_TOKEN
            }
        ],
        'InvalidParameters': []
    }
    return github_proxy.SSM


@pytest.fixture
def mock_github(mocker):
    mocker.patch.object(github_proxy, 'Github')
    return github_proxy.Github.return_value


def test_publish_pr_comment(mocker, mock_ssm, mock_github):
    build = MagicMock(status=BUILD_STATUS)
    build.get_logs_url.return_value = LOGS_URL
    build.get_pr_id.return_value = PR_ID

    proxy = github_proxy.GithubProxy()
    proxy.publish_pr_comment(build)

    mock_ssm.get_parameters.assert_called_once_with(
        Names=['/{}/github_token'.format(test_constants.GITHUB_TOKEN_SSM_PARAMETER_PREFIX)],
        WithDecryption=True
    )
    github_proxy.Github.assert_called_once_with(GITHUB_TOKEN)

    mock_github.get_user.assert_called_once_with(test_constants.GITHUB_OWNER)
    mock_github.get_user.return_value.get_repo.assert_called_once_with(test_constants.GITHUB_REPO)
    mock_repo = mock_github.get_user.return_value.get_repo.return_value
    mock_repo.get_pull.assert_called_once_with(PR_ID)
    mock_pr = mock_repo.get_pull.return_value

    expected_comment = github_proxy.PR_COMMENT_TEMPLATE.format(
        BUILD_STATUS,
        LOGS_URL,
        test_constants.EXPIRATION_IN_DAYS,
        github_proxy.SAR_APP_URL,
        github_proxy.SAR_HOMEPAGE
    )
    mock_pr.create_issue_comment.assert_called_once_with(expected_comment)
