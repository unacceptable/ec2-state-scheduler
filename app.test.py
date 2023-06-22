
'''
    This file contains the unit tests for the EC2 State Scheduler.
    To run the tests, execute the following command:
        python app.test.py
'''
import unittest
import logging
from unittest.mock import MagicMock, patch
from app import get_instances, compare_time, take_action, validate_time

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

class TestEC2StateScheduler(unittest.TestCase):
    '''
        This class contains the unit tests for the EC2 State Scheduler.
    '''
    def setUp(self):
        '''
            This method is executed before each test.
        '''
        self.instances = [
            {
                'InstanceId': 'i-1234567890abcdef0',
                'Tags': [
                    {
                        'Key': 'start',
                        'Value': '0800'
                    },
                    {
                        'Key': 'restart',
                        'Value': '1200'
                    },
                    {
                        'Key': 'shutdown',
                        'Value': '1800'
                    },
                    {
                        'Key': 'foo',
                        'Value': 'bar'
                    }
                ],
                'Bar': 'baz'
            },
            {
                'InstanceId': 'i-0987654321abcdef0',
                'Tags': [
                    {
                        'Key': 'start',
                        'Value': '0900'
                    },
                    {
                        'Key': 'shutdown',
                        'Value': '1700'
                    },
                    {
                        'Key': 'Name',
                        'Value': 'Something Witty'
                    }
                ],
                'Bar': 'baz'
            }
        ]

        self.instances_simplified = [
            {
                'InstanceId': 'i-1234567890abcdef0',
                'Tags': {
                    'start': '0800',
                    'restart': '1200',
                    'shutdown': '1800'
                }
            },
            {
                'InstanceId': 'i-0987654321abcdef0',
                'Tags': {
                    'start': '0900',
                    'shutdown': '1700'
                }
            }
        ]


    def test_get_instances(self):
        ''' Test the get_instances function. '''
        ec2_mock = MagicMock()
        ec2_mock.describe_instances.return_value = {
            'Reservations': [
                {
                    'Instances': self.instances
                }
            ]
        }

        instances = get_instances(ec2=ec2_mock)

        self.assertEqual(instances, self.instances_simplified)


    def test_compare_time(self):
        ''' Test the compare_time function. '''
        self.assertTrue(compare_time('0800', 800))
        self.assertTrue(compare_time('0800', 814))
        self.assertFalse(compare_time('0800', 815))
        self.assertTrue(compare_time('0800', 815, 16))


    def test_take_action(self):
        ''' Test the take_action function. '''
        ec2_mock = MagicMock()

        ec2_mock.start_instances.return_value = {'start': 'success'}
        ec2_mock.stop_instances.return_value = {'stop': 'success'}
        ec2_mock.reboot_instances.return_value = {'reboot': 'success'}

        with patch('boto3.client', return_value=ec2_mock):
            take_action('start', 'i-1234567890abcdef0', ec2=ec2_mock)
            ec2_mock.start_instances.assert_called_once_with(InstanceIds=['i-1234567890abcdef0'])

            take_action('shutdown', 'i-0987654321abcdef0', ec2=ec2_mock)
            ec2_mock.stop_instances.assert_called_once_with(InstanceIds=['i-0987654321abcdef0'])

            take_action('restart', 'i-1234567890abcdef0', ec2=ec2_mock)
            ec2_mock.reboot_instances.assert_called_once_with(InstanceIds=['i-1234567890abcdef0'])

            with self.assertRaises(ValueError):
                take_action('invalid', 'i-1234567890abcdef0', ec2=ec2_mock)


    def test_validate_time(self):
        ''' Test the validate_time function. '''
        self.assertEqual(validate_time('0800'), 800)
        self.assertEqual(validate_time('0900'), 900)
        self.assertEqual(validate_time('1200'), 1200)
        self.assertEqual(validate_time('1300'), 1300)
        self.assertEqual(validate_time('1800'), 1800)

        with self.assertRaises(ValueError):
            validate_time('800')
            validate_time('08000')
            validate_time('2500')
            validate_time('0860')
            validate_time('asdf')

if __name__ == '__main__':
    unittest.main()
