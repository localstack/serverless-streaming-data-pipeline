# LocalStack Streaming Data Pipeline Demo

A serverless ETL for demonstrating streaming structured analytics events from Lambda to Tinybird using CloudWatch and Kinesis.

## Requirements
* LocalStack Pro
* AWS [CDK](https://aws.amazon.com/cdk/)
* [cdklocal](https://github.com/localstack/aws-cdk-local)
* Python 3


## Running Locally

### Deploy Under LocalStack

1. Start LocalStack Pro: `LOCALSTACK_API_KEY="your_key" localstack start -d`
2. Install python dependencies: `make install`
3. Deploy locally: `make deploy-local`

### Testing
After following the local deployments steps above, you can run the sample integration test with `make test-integration`.
Alternatively, you can test end-to-end manually:
* Start the local Tinybird server mock with `make start-request-recorder`
* Emit an event by invoking the logger Lambda: `make invoke-test-logger-local`
* Observe the event payload arrive in the mock server output.