'''
    This script will check for instances with tags "start", "shutdown" or "restart"
    and will start, stop or restart them based on the time specified in the tag value
    relative to the past execution.
'''

import json
import logging
import time
import boto3

ec2 = boto3.client('ec2')

SUPPORTED_ACTIONS = ["start", "shutdown", "restart"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# pylint: disable=redefined-outer-name
#   - for unit tests mocking
def get_instances(ec2=ec2):
    '''
        Get all instances with tags "start", "shutdown" or "restart"
        and return a list of dictionaries with the instance id and the tags like the following:
        [
            {
                'InstanceId': 'i-1234567890abcdef0',
                'Tags': {
                    'start': '0800',
                    'restart': '1200',
                    'shutdown': '1800'
                }
            },
            ...
        ]
    '''
    instances = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag-key',
                'Values': SUPPORTED_ACTIONS
            }
        ]
    )['Reservations'][0]['Instances']

    simplified_list = [
        {
            'InstanceId': instance['InstanceId'],
            'Tags': {
                # pylint: disable=line-too-long
                tag['Key']: tag['Value'] for tag in instance['Tags'] if tag['Key'] in SUPPORTED_ACTIONS
            }
        } for instance in instances
    ]

    logging.info(json.dumps(simplified_list, indent=2))

    return simplified_list


def validate_time(tag_time):
    '''
        Validate the time format and values
    '''
    if len(str(tag_time)) != 4:
        logging.error("Time format is not valid")
        raise ValueError("Time format is not valid")

    if int(str(tag_time)[0:2]) > 24:
        logging.error("Hour value is not valid")
        raise ValueError("Hour value is not valid")

    if int(str(tag_time)[2:4]) > 60:
        logging.error("Minute value is not valid")
        raise ValueError("Minute value is not valid")

    return int(tag_time)


def compare_time(tag_time, current_time, execution_interval=15):
    '''
        Compare the current time with the time specified in the tag value
        and return True if the current time is between the tag time and
        the tag time + execution interval
    '''
    tag_time = validate_time(tag_time)

    logging.info(
        "Current time: %s | Tag time: %s | Execution interval: %s",
        current_time,
        tag_time,
        execution_interval
    )

    return current_time >= tag_time and current_time < tag_time + execution_interval


def take_action(action, instance_id, ec2=ec2):
    '''
        Execute the action for the instance
    '''
    logging.info("Executing action: %s for instance: %s", action, instance_id)

    if action == "start":
        ec2.start_instances(InstanceIds=[instance_id])
    elif action == "shutdown":
        ec2.stop_instances(InstanceIds=[instance_id])
    elif action == "restart":
        ec2.reboot_instances(InstanceIds=[instance_id])
    else:
        raise ValueError("Action not supported")


def main():
    '''
        Main function
    '''
    instances = get_instances()

    current_time = int(time.strftime("%H%M", time.localtime()))


    for instance in instances:
        for action in SUPPORTED_ACTIONS:
            logging.info("Checking for action: %s", action)

            if action in instance['Tags'].keys():
                logging.info("'%s' tag found for instance %s", action, instance['InstanceId'])

                if compare_time(instance['Tags'][action], current_time):
                    take_action(action, instance['InstanceId'])
                else:
                    logging.info("Nothing to do.")


def lambda_handler(event, context):
    '''
        Lambda handler
    '''
    logging.info('Loading function')
    logging.info(event)
    logging.info(context)
    main()


if __name__ == "__main__":
    main()
