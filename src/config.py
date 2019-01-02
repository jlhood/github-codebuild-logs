"""Environment configuration values used by lambda functions."""

import os

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
BUCKET_NAME = os.getenv('BUILD_LOGS_BUCKET_NAME')
PROJECT_NAME = os.getenv('CODEBUILD_PROJECT_NAME')
EXPIRATION_IN_DAYS = os.getenv('EXPIRATION_IN_DAYS')
REGION = os.getenv('AWS_DEFAULT_REGION')
