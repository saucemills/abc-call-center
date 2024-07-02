import json
import boto3
import logging
from boto3.dynamodb.conditions import Key

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Log the received event
    logger.info("Received event: %s", json.dumps(event))
    
    try:
        # Extract the business line variable from the event
        business_line = event['Details']['Parameters']['businessLine']
        logger.info("Extracted business line: %s", business_line)
        
        # Initialize a session using Amazon DynamoDB
        dynamodb = boto3.resource('dynamodb')
        
        # Select your DynamoDB table
        table = dynamodb.Table('dnis-prompt')
        
        # Query the table for the business line
        response = table.query(
            KeyConditionExpression=Key('businessLine').eq(business_line)
        )
        
        # Check if any items were returned
        if 'Items' in response and len(response['Items']) > 0:
            # Get the first item from the response
            item = response['Items'][0]
            logger.info("Item found: %s", json.dumps(item))
            
            # Return all attributes of the item
            item['statusCode'] = 200
            return item
        
        else:
            logger.warning("Promps not found for business line: %s", business_line)
            # Return a message if the business line was not found
            return {
                'statusCode': 404,
                'message': 'Business line not found not found'
            }
    except Exception as e:
        logger.error("Error occurred: %s", str(e), exc_info=True)
        # Return an error message
        return {
            'statusCode': 500,
            'message': 'Internal server error'
        }