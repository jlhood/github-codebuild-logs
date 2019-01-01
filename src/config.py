"""Environment configuration values used by lambda functions."""

import os

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
BUCKET_NAME = os.getenv('BUILD_LOGS_BUCKET_NAME')
PROJECT_NAME = os.getenv('CODEBUILD_PROJECT_NAME')
EXPIRATION_IN_DAYS = os.getenv('EXPIRATION_IN_DAYS')
GITHUB_OWNER = os.getenv('GITHUB_OWNER')
GITHUB_REPO = os.getenv('GITHUB_REPO')
GITHUB_TOKEN_PARAMETER_NAME = '/{}/github_token'.format(os.getenv('GITHUB_TOKEN_SSM_PARAMETER_PREFIX'))
REGION = os.getenv('AWS_DEFAULT_REGION')
