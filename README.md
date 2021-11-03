# GC Forms Performance Testing

This utilizes the amazing work done at [invokust](https://github.com/FutureSharks/invokust)

## How it works

The `locust_swarm.py` is launched in a terminal locally and handles the creation and reporting back from multiple lambda's which run the identified test file.

In the AWS there is a lambda called 'LoadTesting' which houses the code found in `./lambda/lambda_locust.py`. This lambda is responsible for running the locust test and returning the results.

The `./test_files` directory contains various test files that can be uploaded along side `lambda_locust.py` to the lambda.
Example lambda structure:
./
... lambda_locust.py
... locust_test_file.py

## Configuration Options

All configurable options are located at the top of the `locust_swarm.py` file.

`test_time`: The length in minutes the complete test should run. This value should be in multiples of 3 because the current runtime of a single lambda in 3 min.

`threads`: The number of lambda's to launch. Each thread replicates 25 users. So to replicate 500 users the threads value should be set to 20. (500 / 25 = 20)

`test_file`: The name of the test file to run. Needs to match one of the files already uploaded into the lambda at the same directory level of the lambda handler code.

## Utility Scripts

`plotter.py`: A work in progress that never really got started. It would create a graph of the results similar to what is seen when running the Locust service locally.
`analysis.py`: Used as a post-processing script to verify if there was any data loss by analyzing failed form submissions and errors's returned vs silently dropped.

- Run locust_swarm.py with a testfile that sends responses to the Vault.
- Download the Vault Dynamodb contents (.sjon files) into a folder named 'dynamodb' at the root of the repo folder.
- Run 'analysis.py' and on completion the results will be printed in the terminal.

## Future Enhancements

-[] Test_files could be loaded into a single test folder/lambda layer or passed through payload from terminal to Lambda call.
