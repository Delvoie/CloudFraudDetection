"""
SendAlert Lambda Function

Triggered by: Step Functions (FraudDetectionWorkflow) - when fraud is detected
Purpose: Publishes fraud alerts to SNS topic for email notifications
Runtime: Python 3.11

Environment Variables Required:
- SNS_TOPIC_ARN: ARN of the FraudAlertsTopic SNS topic
  Example: arn:aws:sns:us-east-1:123456789012:FraudAlertsTopic
"""

import os
import json
import boto3

# Initialize AWS SNS client
sns = boto3.client("sns")

# Get SNS topic ARN from environment variable
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]


def lambda_handler(event, context):
    """
    Publish fraud alert to SNS topic.
    
    Args:
        event: Transaction data from Step Functions
        {
            "transaction": {
                "transactionId": "TXN-123",
                "amount": 15000,
                "userId": "user-456"
            }
        }
        context: Lambda context object
        
    Returns:
        dict: Status message
    """
    
    # Extract transaction details
    transaction = event.get("transaction", event)
    transaction_id = transaction.get("transactionId", "unknown")
    amount = transaction.get("amount", 0)
    user_id = transaction.get("userId", "unknown")
    merchant = transaction.get("merchant", "unknown")
    
    # Create detailed alert message
    alert_message = f"""
🚨 FRAUD ALERT 🚨

Transaction ID: {transaction_id}
User ID: {user_id}
Amount: ${amount:,.2f}
Merchant: {merchant}

This transaction has been flagged as potentially fraudulent based on amount threshold (>$10,000).

Full transaction details:
{json.dumps(transaction, indent=2)}
"""
    
    # Publish to SNS
    try:
        response = sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=alert_message,
            Subject=f"🚨 Fraud Alert: Transaction {transaction_id}"
        )
        
        print(f"Alert sent for transaction {transaction_id}. MessageId: {response['MessageId']}")
        
        return {
            "statusCode": 200,
            "status": "Alert Sent",
            "messageId": response["MessageId"],
            "transactionId": transaction_id
        }
        
    except Exception as e:
        print(f"Error sending alert: {str(e)}")
        raise
