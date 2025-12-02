"""
SendToCleanQueue Lambda Function

Triggered by: Step Functions (FraudDetectionWorkflow) - when transaction is clean
Purpose: Sends cleared transactions to CleanTransactionsQueue for storage
Runtime: Python 3.11

Environment Variables Required:
- CLEAN_QUEUE_URL: URL (not ARN!) of the CleanTransactionsQueue
  Example: https://sqs.us-east-1.amazonaws.com/123456789012/CleanTransactionsQueue
  
IMPORTANT: Must be Queue URL, NOT ARN. SQS send_message requires the URL format.
"""

import os
import json
import boto3

# Initialize AWS SQS client
sqs = boto3.client("sqs")

# Get SQS queue URL from environment variable
CLEAN_QUEUE_URL = os.environ["CLEAN_QUEUE_URL"]


def lambda_handler(event, context):
    """
    Send clean transaction to CleanTransactionsQueue.
    
    Args:
        event: Transaction data from Step Functions
        Can be either:
        - Full evaluation result: {"evaluation": {...}, "transaction": {...}}
        - Just transaction: {"transactionId": "TXN-123", "amount": 100}
        context: Lambda context object
        
    Returns:
        dict: Status message with SQS message ID
    """
    
    # Extract transaction data
    # Handle both formats (with or without evaluation wrapper)
    if "transaction" in event:
        transaction = event["transaction"]
    else:
        transaction = event
    
    transaction_id = transaction.get("transactionId", "unknown")
    amount = transaction.get("amount", 0)
    
    # Send to SQS queue
    try:
        response = sqs.send_message(
            QueueUrl=CLEAN_QUEUE_URL,
            MessageBody=json.dumps(transaction, indent=2)
        )
        
        print(f"Clean transaction {transaction_id} (${amount}) sent to queue. MessageId: {response['MessageId']}")
        
        return {
            "statusCode": 200,
            "status": "Sent to Clean Queue",
            "messageId": response["MessageId"],
            "transactionId": transaction_id
        }
        
    except Exception as e:
        print(f"Error sending to queue: {str(e)}")
        print(f"Queue URL: {CLEAN_QUEUE_URL}")
        raise
