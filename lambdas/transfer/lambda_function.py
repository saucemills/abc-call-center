import json
import boto3
import logging
from datetime import datetime
from boto3.dynamodb.conditions import Key

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Log the received event
    logger.info("Received event: %s", json.dumps(event))
    
    try:
        # Extract the business line variable from the event
        intent = event['Details']['Parameters']['callerIntent']
        logger.info("Extracted caller intent: %s", intent)
        
        # Initialize a session using Amazon DynamoDB
        dynamodb = boto3.resource('dynamodb')
        
        # Select your DynamoDB table
        table = dynamodb.Table('transfer')
        
        # Query the table for the business line
        response = table.query(
            KeyConditionExpression=Key('callerIntent').eq(intent)
        )
        
        # Check if any items were returned
        if 'Items' in response and len(response['Items']) > 0:
            # Get the first item from the response
            item = response['Items'][0]
            logger.info("Item found: %s", json.dumps(item))

            # Get current day and time
            now = datetime.now()
            current_day = now.strftime("%A")
            current_time = now.strftime("%H:%M:%S")

            # Check hours for the current day
            if current_day in item['hours']:
                start_time = item['hours'][current_day]['start']
                end_time = item['hours'][current_day]['end']
                
                if start_time <= current_time <= end_time:
                    item['queue_status'] = 'open'
                else:
                    item['queue_status'] = 'closed'
            else:
                item['queue_status'] = 'closed'
            logger.info("Current day: %s", current_day)
            logger.info("Current time: %s", current_time)
            logger.info("Logged queue status as %s", item['queue_status'])
            
            # Return all attributes of the item
            item['statusCode'] = 200
            return item
        
        else:
            logger.warning("Transfer item not found for: %s", intent)
            # Return a message if the business line was not found
            return {
                'statusCode': 404,
                'message': 'Transfer item not found'
            }
    except Exception as e:
        logger.error("Error occurred: %s", str(e), exc_info=True)
        # Return an error message
        return {
            'statusCode': 500,
            'message': 'Internal server error'
        }