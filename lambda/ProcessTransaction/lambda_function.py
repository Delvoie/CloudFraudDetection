"""
ProcessTransaction Lambda Function

Triggered by: TransactionQueue (SQS)
Purpose: Receives transaction messages from SQS and starts Step Functions workflow
Runtime: Python 3.11

Environment Variables Required:
- STATE_MACHINE_ARN: ARN of the FraudDetectionWorkflow Step Functions state machine
  Example: arn:aws:states:us-east-1:123456789012:stateMachine:FraudDetectionWorkflow
"""

import os
import json
import boto3

# Initialize AWS Step Functions client
stepfunctions = boto3.client("stepfunctions")

# Get state machine ARN from environment variable
STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]


def lambda_handler(event, context):
    """
    Process incoming SQS messages and start Step Functions execution for each transaction.
    
    Args:
        event: SQS event containing transaction records
        context: Lambda context object
        
    Returns:
        dict: Status message with count of started executions
    """
    started_count = 0
    
    # Process each SQS record
    for record in event.get("Records", []):
        try:
            # Parse transaction from SQS message body
            transaction = json.loads(record["body"])
            
            # Start Step Functions execution
            response = stepfunctions.start_execution(
                stateMachineArn=STATE_MACHINE_ARN,
                input=json.dumps(transaction)
            )
            
            started_count += 1
            
            print(f"Started execution for transaction {transaction.get('transactionId')}: {response['executionArn']}")
            
        except Exception as e:
            print(f"Error processing record: {str(e)}")
            # Continue processing other records even if one fails
            continue
    
    return {
        "statusCode": 200,
        "message": f"Started {started_count} Step Functions execution(s)"
    }
