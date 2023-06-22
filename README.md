# EC2 State Scheduler

This script checks for instances with tags "start", "shutdown" or "restart" and starts, stops or restarts them based on the time specified in the tag value relative to the past execution.

## Quick Start

1. Build the container `docker build .`
2. Set up the necessary IAM permissions for the script to run. An example IAM policy would be:
    ``` json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "EC2StateSchedulerPermissions",
                "Effect": "Allow",
                "Action": [
                    "ec2:DescribeInstances",
                    "ec2:StartInstances",
                    "ec2:StopInstances",
                    "ec2:RebootInstances"
                ],
                "Resource": "*"
            }
        ]
    }
    ```
3. Schedule the container in your favorite container orchestration platform.
4. Profit

## Local Execution

1. Set up your AWS credentials using one of the methods described in the Boto3 documentation.
2. Install requirements `pip install -r requirements.txt`
2. Run the script: `python app.py`

## License

This project is licensed under the terms of the [LICENSE](./LICENSE) file.

## Testing

Unit tests are located in `app.test.py` and can be executed via `python app.test.py`.
