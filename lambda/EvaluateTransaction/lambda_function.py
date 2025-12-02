"""
EvaluateTransaction Lambda Function

Triggered by: Step Functions (FraudDetectionWorkflow)
Purpose: Analyzes transaction data to determine if it's fraudulent
Runtime: Python 3.11

Environment Variables: None required

Fraud Detection Logic:
- Transactions with amount > 10000 are flagged as fraudulent
- Can be extended with additional rules (velocity checks, geo-location, etc.)
"""


def lambda_handler(event, context):
    """
    Evaluate a transaction for fraud indicators.
    
    Args:
        event: Transaction data
        {
            "transactionId": "TXN-123",
            "amount": 15000,
            "userId": "user-456",
            "merchant": "store-xyz"
        }
        context: Lambda context object
        
    Returns:
        dict: Evaluation result with fraud flag
        {
            "isFraud": true/false,
            "transactionId": "TXN-123",
            "transaction": {...original transaction data...}
        }
    """
    
    # Extract transaction amount
    amount = event.get("amount", 0)
    transaction_id = event.get("transactionId", "unknown")
    
    # Simple fraud detection rule: amount > 10000
    is_fraud = amount > 10000
    
    # Log evaluation result
    if is_fraud:
        print(f"FRAUD DETECTED - Transaction {transaction_id}: Amount ${amount}")
    else:
        print(f"CLEAN TRANSACTION - Transaction {transaction_id}: Amount ${amount}")
    
    # Return evaluation result
    return {
        "isFraud": is_fraud,
        "transactionId": transaction_id,
        "transaction": event
    }
