import pytest

import processbuildevents
import test_constants


@pytest.fixture
def mock_build(mocker):
    mocker.patch.object(processbuildevents, 'Build')
    mock_build = processbuildevents.Build.return_value
    mock_build.project_name = test_constants.PROJECT_NAME
    mock_build.is_pr_build.return_value = True
    return mock_build


@pytest.fixture
def mock_github(mocker):
    mocker.patch.object(processbuildevents, 'GITHUB')
    return processbuildevents.GITHUB


def test_handler(mocker, mock_build, mock_github):
    build_event = _mock_build_event()
    processbuildevents.handler(build_event, None)

    processbuildevents.Build.assert_called_once_with(build_event)
    mock_build.copy_logs.assert_called_once()
    mock_github.publish_pr_comment.assert_called_once_with(mock_build)
    mock_github.delete_previous_comments.assert_not_called()


def test_handler_different_project_name(mocker, mock_build, mock_github):
    mock_build.project_name = 'different-project'

    processbuildevents.handler(_mock_build_event(), None)

    mock_build.copy_logs.assert_not_called()
    mock_github.publish_pr_comment.assert_not_called()
    mock_github.delete_previous_comments.assert_not_called()


def test_handler_not_pr_build(mocker, mock_build, mock_github):
    mock_build.is_pr_build.return_value = False

    processbuildevents.handler(_mock_build_event(), None)

    mock_build.copy_logs.assert_not_called()
    mock_github.publish_pr_comment.assert_not_called()
    mock_github.delete_previous_comments.assert_not_called()

def test_handler_delete_previous_commments(mocker, mock_build, mock_github):
    processbuildevents.config.DELETE_PREVIOUS_COMMENTS = True

    build_event = _mock_build_event()
    processbuildevents.handler(build_event, None)

    mock_github.delete_previous_comments.assert_called_once_with(mock_build)


def _mock_build_event():
    return {
        'detail': {
            'build-id': 'some-build'
        }
    }
