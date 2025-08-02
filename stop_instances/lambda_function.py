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
    This function stops EC2 instances that have a specific tag and are in a 'running' state.
    It includes enhanced logging to help with debugging tag or region mismatches.
    """
    logger.info("Starting function to stop EC2 instances...")

    # Define a filter to find instances with our specific tag and that are currently running
    filters = [
        {
            'Name': f'tag:{TAG_KEY}',
            'Values': ['True', 'true']
        },
        {
            'Name': 'instance-state-name',
            'Values': ['running']
        }
    ]

   
    # It prints the exact filter being used to the logs.
    logger.info(f"Searching for instances with these filters: {filters}")
    # -------------------------------------

    try:
        # Find all instances that match the filter
        reservations = ec2.describe_instances(Filters=filters)

        instances_to_stop = []
        # Iterate through the reservations and instances to get their IDs
        for reservation in reservations['Reservations']:
            for instance in reservation['Instances']:
                instances_to_stop.append(instance['InstanceId'])

        if not instances_to_stop:
            logger.info("No running instances found matching the filters. Please check your instance tags and region.")
            return {'statusCode': 200, 'body': 'No instances to stop.'}
        
        logger.info(f"Found instances to stop: {', '.join(instances_to_stop)}")
        
        # Stop the instances
        ec2.stop_instances(InstanceIds=instances_to_stop)
        
        success_message = f"Successfully sent stop command for instances: {', '.join(instances_to_stop)}"
        logger.info(success_message)
        
        return {
            'statusCode': 200,
            'body': success_message
        }

    except ClientError as e:
        logger.error(f"An AWS API error occurred: {e}")
        return {'statusCode': 500, 'body': f"Error stopping instances: {e}"}
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return {'statusCode': 500, 'body': f"An unexpected error occurred: {e}"}