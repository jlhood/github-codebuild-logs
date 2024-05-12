# Development

## Commands

1. `pipenv update --dev` - Updates dependencies, including dev dependencies.
1. `make` - lints template, runs unit tests, prepares for packaging.
1. `PACKAGE_BUCKET=<bucket> PROFILE=<aws creds profile> make package` - builds and packages template for deployment.
1. `PACKAGE_BUCKET=<bucket> PROFILE=<aws creds profile> make publish` - builds, packages, and publishes to Serverless Application Repository.
    1. **Important:** Prior to publishing, you should test the app via the `github-codebuild-logs-test` repo (see README in that repo).

## Releases

To release a new version:

1. Bump version by updating README and template (2 places in the template). Example: [https://github.com/jlhood/github-codebuild-logs/pull/30](https://github.com/jlhood/github-codebuild-logs/pull/30).
1. Tag new version commit `git tag <version>`
1. Push tag `git push --tags`
1. Publish (see make command above)
1. Go to [Releases](https://github.com/jlhood/github-codebuild-logs/releases) page, add release notes for new tag.
