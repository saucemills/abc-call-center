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
        # Extract the DNIS from the event
        dnis = event['Details']['Parameters']['dnis']
        logger.info("Extracted DNIS: %s", dnis)
        
        # Initialize a session using Amazon DynamoDB
        dynamodb = boto3.resource('dynamodb')
        
        # Select your DynamoDB table
        table = dynamodb.Table('dnis-config')
        
        # Query the table for the DNIS
        response = table.query(
            KeyConditionExpression=Key('node').eq(dnis)
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
            logger.warning("DNIS not found: %s", dnis)
            # Return a message if the DNIS was not found
            return {
                'statusCode': 404,
                'message': 'DNIS not found'
            }
    except Exception as e:
        logger.error("Error occurred: %s", str(e), exc_info=True)
        # Return an error message
        return {
            'statusCode': 500,
            'message': 'Internal server error'
        }