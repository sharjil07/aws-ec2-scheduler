import boto3
import os
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2 = boto3.client('ec2')

# Environment variable for the tag key to filter instances
TAG_KEY = os.environ.get('TAG_KEY', 'Auto-Start-Stop')

def lambda_handler(event, context):
    """
    This function starts EC2 instances that have a specific tag and are in a 'stopped' state.
    It's designed to be robust, configurable, and have professional logging.
    """
    logger.info("Starting function to start EC2 instances...")

    # Define a filter to find instances with our specific tag and that are currently stopped
    filters = [
        {
            'Name': f'tag:{TAG_KEY}',
            'Values': ['True', 'true']
        },
        {
            'Name': 'instance-state-name',
            'Values': ['stopped']
        }
    ]

    try:
        # Find all instances that match the filter
        reservations = ec2.describe_instances(Filters=filters)

        instances_to_start = []
        # Iterate through the reservations and instances to get their IDs
        for reservation in reservations['Reservations']:
            for instance in reservation['Instances']:
                instances_to_start.append(instance['InstanceId'])

        if not instances_to_start:
            logger.info("No stopped instances found with the specified tag. No action taken.")
            return {'statusCode': 200, 'body': 'No instances to start.'}
        
        logger.info(f"Found instances to start: {', '.join(instances_to_start)}")
        
        # Start the instances
        ec2.start_instances(InstanceIds=instances_to_start)
        
        success_message = f"Successfully sent start command for instances: {', '.join(instances_to_start)}"
        logger.info(success_message)
        
        return {
            'statusCode': 200,
            'body': success_message
        }

    except ClientError as e:
        # Log the error for debugging
        logger.error(f"An AWS API error occurred: {e}")
        # Return an error response
        return {
            'statusCode': 500,
            'body': f"Error starting instances: {e}"
        }
    except Exception as e:
        # Catch any other unexpected errors
        logger.error(f"An unexpected error occurred: {e}")
        return {
            'statusCode': 500,
            'body': f"An unexpected error occurred: {e}"
        }