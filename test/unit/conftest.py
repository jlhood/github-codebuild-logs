"""Setup unit test environment."""

import sys
import os

import test_constants

# make sure tests can import the app code
my_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, my_path + '/../../src/')

# set expected config environment variables to test constants
os.environ['BUILD_LOGS_BUCKET_NAME'] = test_constants.BUCKET_NAME
os.environ['CODEBUILD_PROJECT_NAME'] = test_constants.PROJECT_NAME
os.environ['EXPIRATION_IN_DAYS'] = test_constants.EXPIRATION_IN_DAYS
os.environ['GITHUB_OWNER'] = test_constants.GITHUB_OWNER
os.environ['GITHUB_REPO'] = test_constants.GITHUB_REPO
os.environ['GITHUB_TOKEN_SSM_PARAMETER_PREFIX'] = test_constants.GITHUB_TOKEN_SSM_PARAMETER_PREFIX
os.environ['AWS_DEFAULT_REGION'] = test_constants.REGION
