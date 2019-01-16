# github-codebuild-logs

![Build Status](https://codebuild.us-east-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoicDlvblNsMkl0Y1hLelczd2EwZVRaVjd2eSs0ejVRWHlJTGtPSng0RDdFOGpsa0Z1YU1nMFNMd3RZbDBBaVZaR1lVMkVRNEFBM2x1NzdsTy9WdFFqeWlrPSIsIml2UGFyYW1ldGVyU3BlYyI6Ik13ZGZtcUVNTWZadnpvaGYiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)

This serverless app solves a common complaint when using AWS CodeBuild as a CI solution: PR contributors don't have access to the build logs if the CI build fails on their PR branch. The app creates publicly accessible links to PR build logs for a given AWS CodeBuild project and posts them as a comment on the corresponding GitHub PR.

Here is an example GitHub PR comment:

![Screenshot](https://github.com/jlhood/github-codebuild-logs/raw/master/images/screenshot.png)

## App Architecture

![App Architecture](https://github.com/jlhood/github-codebuild-logs/raw/master/images/app-architecture.png)

1. Contributors create or update a PR.
1. Assuming AWS CodeBuild is already setup as the CI solution for this repo, the PR triggers a new CI build.
1. Once the CI build completes (success or failure), a CloudWatch Event triggers the ProcessBuildEvents AWS Lambda function.
1. If the event is for a PR build, the ProcessBuildEvents function
    1. copies the build log to an S3 bucket. Note, the build log auto-expires after a configurable number of days (default: 30).
    1. publishes a comment on the GitHub PR with a publicly accessible link to the logs. Note, the app uses the CodeBuild project's GitHub OAUTH token to post the comment.

## Installation Instructions

To attach this app to an existing AWS CodeBuild project in your AWS account,

1. Go to the app's page on the [Serverless Application Repository](https://serverlessrepo.aws.amazon.com/applications/arn:aws:serverlessrepo:us-east-1:277187709615:applications~github-codebuild-logs) and click "Deploy"
1. Provide the CodeBuild project name and any other parameters (see parameter details below) and click "Deploy"

Alternatively, if your CodeBuild project is defined in an AWS SAM template, this app can be embedded as a nested app inside that SAM template. To do this, visit the [app's page on the AWS Lambda Console](https://console.aws.amazon.com/lambda/home#/create/app?applicationId=arn:aws:serverlessrepo:us-east-1:277187709615:applications/github-codebuild-logs). Click the "Copy as SAM Resource" button and paste the copied YAML into your SAM template.

## App Parameters

1. `CodeBuildProjectName` (required) - Name of CodeBuild project this app is posting logs for.
1. `ExpirationInDays` (optional) - Number of days before a build's log page expires. Default: 30
1. `LogLevel` (optional) - Log level for Lambda function logging, e.g., ERROR, INFO, DEBUG, etc. Default: INFO

## App Outputs

1. `ProcessBuildEventsFunctionName` - ProcessBuildEvents Lambda function name.
1. `ProcessBuildEventsFunctionArn` - ProcessBuildEvents Lambda function ARN.
1. `BuildLogsBucketName` - Build logs S3 bucket name.
1. `BuildLogsBucketArn` - Build logs S3 bucket ARN.

## License Summary

This code is made available under the MIT license. See the LICENSE file.
