import pytest
from unittest.mock import MagicMock

import github_proxy
import test_constants

GITHUB_OWNER = 'gh-user'
GITHUB_REPO = 'gh-repo'
GITHUB_LOCATION = 'https://github.com/{}/{}.git'.format(GITHUB_OWNER, GITHUB_REPO)
CODEBUILD_GITHUB_TOKEN = 'shhh!!'
SECRETS_MANAGER_GITHUB_TOKEN = "don't tell!!"
BUILD_STATUS = 'SUCCEEDED'
PR_ID = 5
LOGS_URL = 'https://foo.com'


@pytest.fixture
def mock_config(mocker):
    mocker.patch.object(github_proxy, 'config')
    github_proxy.config.configure_mock(
        PROJECT_NAME=test_constants.PROJECT_NAME,
        EXPIRATION_IN_DAYS=test_constants.EXPIRATION_IN_DAYS,
        GITHUB_OAUTH_TOKEN_SECRET_ARN=''
    )
    return github_proxy.config


@pytest.fixture
def mock_codebuild(mocker):
    mocker.patch.object(github_proxy, 'CODEBUILD')
    github_proxy.CODEBUILD.batch_get_projects.return_value = {
        'projects': [
            {
                'source': {
                    'type': 'GITHUB',
                    'location': GITHUB_LOCATION,
                    'auth': {
                        'type': 'OAUTH',
                        'resource': CODEBUILD_GITHUB_TOKEN
                    }
                }
            }
        ]
    }
    return github_proxy.CODEBUILD


@pytest.fixture
def mock_secretsmanager(mocker):
    mocker.patch.object(github_proxy, 'SECRETS_MANAGER')
    github_proxy.SECRETS_MANAGER.get_secret_value.return_value = {
        'SecretString': SECRETS_MANAGER_GITHUB_TOKEN
    }
    return github_proxy.SECRETS_MANAGER


@pytest.fixture
def mock_github(mocker):
    mocker.patch.object(github_proxy, 'Github')
    return github_proxy.Github.return_value


def test_publish_pr_comment(mocker, mock_config, mock_codebuild, mock_secretsmanager, mock_github):
    build = MagicMock(status=BUILD_STATUS)
    build.get_logs_url.return_value = LOGS_URL
    build.get_pr_id.return_value = PR_ID

    proxy = github_proxy.GithubProxy()
    proxy.publish_pr_comment(build)

    mock_codebuild.batch_get_projects.assert_called_once_with(
        names=[test_constants.PROJECT_NAME]
    )
    mock_secretsmanager.get_secret_value.assert_not_called()
    github_proxy.Github.assert_called_once_with(CODEBUILD_GITHUB_TOKEN)

    mock_github.get_user.assert_called_once_with(GITHUB_OWNER)
    mock_github.get_user.return_value.get_repo.assert_called_once_with(GITHUB_REPO)
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


def test_init_github_info_auth_with_secrets_manager_arn(mocker, mock_config, mock_codebuild, mock_secretsmanager):
    secret_arn = 'arn:secret'
    mock_config.configure_mock(GITHUB_OAUTH_TOKEN_SECRET_ARN=secret_arn)

    proxy = github_proxy.GithubProxy()
    proxy._init_github_info()

    assert proxy._github_token == SECRETS_MANAGER_GITHUB_TOKEN
    mock_secretsmanager.get_secret_value.assert_called_once_with(SecretId=secret_arn)


def test_init_github_info_type_not_github(mocker, mock_config, mock_codebuild, mock_secretsmanager):
    mock_codebuild.batch_get_projects.return_value['projects'][0]['source']['type'] = 'NOT_GITHUB'
    proxy = github_proxy.GithubProxy()
    with pytest.raises(RuntimeError):
        proxy._init_github_info()


def test_init_github_info_auth_type_not_oauth(mocker, mock_config, mock_codebuild, mock_secretsmanager):
    mock_codebuild.batch_get_projects.return_value['projects'][0]['source']['auth']['type'] = 'NOT_OAUTH'
    proxy = github_proxy.GithubProxy()
    with pytest.raises(RuntimeError):
        proxy._init_github_info()


def test_init_github_info_invalid_source_location(mocker, mock_config, mock_codebuild, mock_secretsmanager):
    mock_codebuild.batch_get_projects.return_value['projects'][0]['source']['location'] = 'bad-location'
    proxy = github_proxy.GithubProxy()
    with pytest.raises(RuntimeError):
        proxy._init_github_info()
