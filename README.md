# github-codebuild-logs

![Build Status](https://codebuild.us-east-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoicDlvblNsMkl0Y1hLelczd2EwZVRaVjd2eSs0ejVRWHlJTGtPSng0RDdFOGpsa0Z1YU1nMFNMd3RZbDBBaVZaR1lVMkVRNEFBM2x1NzdsTy9WdFFqeWlrPSIsIml2UGFyYW1ldGVyU3BlYyI6Ik13ZGZtcUVNTWZadnpvaGYiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)

This serverless app solves a common complaint when using AWS CodeBuild as a CI solution: PR contributors don't have access to the build logs if the CI build fails on their PR branch. The app creates publicly accessible links to PR build logs for a given AWS CodeBuild project and posts them as a comment on the corresponding GitHub PR.

Here is an example GitHub PR comment:

![Screenshot](https://github.com/jlhood/github-codebuild-logs/raw/master/images/screenshot.png)

## App Architecture

![App Architecture](https://github.com/jlhood/github-codebuild-logs/raw/master/images/app-architecture.png)

1. Contributors create or update a PR.
1. Assuming AWS CodeBuild is already setup as the CI solution for this repo, the PR triggers a new CI build.
1. Once the CI build completes (success or failure), a CloudWatch Event triggers an AWS Lambda function.
1. If the event is for a PR build, the Lambda function
    1. copies the build log to an S3 bucket. Note, the build log auto-expires after a configurable number of days (default: 30).
    1. publishes a comment on the GitHub PR with a publicly accessible link to the logs. Note, the app uses the CodeBuild project's GitHub OAUTH token to post the comment.
1. The logs link goes to an API Gateway endpoint, which redirects to a pre-signed URL for the build logs in the S3 bucket.

## Installation Instructions

To attach this app to an existing AWS CodeBuild project in your AWS account,

1. Go to the app's page on the [Serverless Application Repository](https://serverlessrepo.aws.amazon.com/applications/arn:aws:serverlessrepo:us-east-1:277187709615:applications~github-codebuild-logs) and click "Deploy"
1. Provide the CodeBuild project name and any other parameters (see parameter details below) and click "Deploy"

Alternatively, if your CodeBuild project is defined in an AWS SAM template, this app can be embedded as a nested app inside that SAM template. To do this, visit the [app's page on the AWS Lambda Console](https://console.aws.amazon.com/lambda/home#/create/app?applicationId=arn:aws:serverlessrepo:us-east-1:277187709615:applications/github-codebuild-logs). Click the "Copy as SAM Resource" button and paste the copied YAML into your SAM template.

If you are an AWS CDK user, you can use the [aws-serverless.CfnApplication](https://awslabs.github.io/aws-cdk/refs/_aws-cdk_aws-serverless.html#cfnapplication) construct to embed this app in your CDK application. Here is a TypeScript example:

```typescript
import serverless = require('@aws-cdk/aws-sam');

new serverless.CfnApplication(this, 'GitHubCodeBuildLogsSAR', {
  location: {
    applicationId: 'arn:aws:serverlessrepo:us-east-1:277187709615:applications/github-codebuild-logs',
    semanticVersion: '1.1.0'
  },
  parameters: {
    CodeBuildProjectName: project.projectName
  }
});
```

## App Parameters

1. `CodeBuildProjectName` (required) - Name of CodeBuild project this app is posting logs for.
1. `ExpirationInDays` (optional) - Number of days before a build's log page expires. Default: 30
1. `CodeBuildProjectCustomLogGroupName` (optional) - If the CodeBuild Project has a custom log group name, you can specify it here. If not provided, the app will assume the CodeBuild default log group name format of `/aws/codebuild/<project name>`.
1. `GitHubOAuthToken` (optional) - OAuth token used for writing comments to GitHub PRs. If not provided, the app will attempt to pull an OAuth token from the CodeBuild project. Note, if your CodeBuild project does not have a GitHub OAuth token, e.g., it is being used to build a public GitHub repo, then this parameter will be required for the app to function properly.

1. `LogLevel` (optional) - Log level for Lambda function logging, e.g., ERROR, INFO, DEBUG, etc. Default: INFO

## App Outputs

1. `ProcessBuildEventsFunctionName` - ProcessBuildEvents Lambda function name.
1. `ProcessBuildEventsFunctionArn` - ProcessBuildEvents Lambda function ARN.
1. `BuildLogsBucketName` - Build logs S3 bucket name.
1. `BuildLogsBucketArn` - Build logs S3 bucket ARN.

## Security Considerations

The following precautions are taken when the `GitHubOAuthToken` parameter is provided since it's sensitive data:

1. The NoEcho option is used on the parameter so the value will never be shown by CloudFormation.
1. The app stores the value in [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/).

## License Summary

This code is made available under the MIT license. See the LICENSE file.
