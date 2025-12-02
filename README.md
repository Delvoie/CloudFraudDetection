# Cloud Fraud Detection System

AWS Academy demonstration project for financial fraud detection using AWS serverless services.

## Architecture Overview

This project demonstrates a serverless fraud detection workflow using:

- **Amazon SQS** - Message queuing for transaction processing
- **Amazon SNS** - Notifications for fraud alerts
- **AWS Lambda** - Serverless compute for transaction processing
- **AWS Step Functions** - Workflow orchestration

## System Flow

```
Transaction → TransactionQueue (SQS)
                    ↓
            ProcessTransaction (Lambda)
                    ↓
         FraudDetectionWorkflow (Step Functions)
                    ↓
            EvaluateTransaction (Lambda)
                    ↓
              [Decision Point]
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
  [Fraud Detected]        [Clean Transaction]
        ↓                       ↓
  SendAlert (Lambda)    SendToCleanQueue (Lambda)
        ↓                       ↓
  FraudAlertsTopic      CleanTransactionsQueue
      (SNS)                   (SQS)
```

## Components

### SQS Queues
1. **TransactionQueue** - Receives incoming transactions for processing
2. **CleanTransactionsQueue** - Stores cleared (non-fraudulent) transactions

### SNS Topics
- **FraudAlertsTopic** - Sends email alerts for detected fraud

### Lambda Functions
1. **ProcessTransaction** - Triggered by SQS, starts Step Functions workflow
2. **EvaluateTransaction** - Analyzes transaction for fraud indicators
3. **SendAlert** - Publishes fraud alerts to SNS
4. **SendToCleanQueue** - Sends clean transactions to storage queue

### Step Functions
- **FraudDetectionWorkflow** - Orchestrates the fraud detection logic

## Fraud Detection Logic

Simple rule-based detection:
- Transactions with `amount > 10000` are flagged as fraudulent
- Fraudulent transactions trigger email alerts
- Clean transactions are stored for record-keeping

## Project Structure

```
CloudFraudDetection/
├── README.md
├── DEPLOYMENT_GUIDE.md
├── TESTING_GUIDE.md
├── lambda/
│   ├── ProcessTransaction/
│   │   └── lambda_function.py
│   ├── EvaluateTransaction/
│   │   └── lambda_function.py
│   ├── SendAlert/
│   │   └── lambda_function.py
│   └── SendToCleanQueue/
│       └── lambda_function.py
├── step-functions/
│   └── FraudDetectionWorkflow.json
├── sqs/
│   ├── TransactionQueue.json
│   └── CleanTransactionsQueue.json
├── sns/
│   └── FraudAlertsTopic.json
├── docs/
│   ├── ARCHITECTURE.md
│   └── TROUBLESHOOTING.md
└── test-data/
    ├── fraudulent-transaction.json
    └── clean-transaction.json
```

## Prerequisites

- AWS Academy Learner Lab access
- Python 3.11 runtime support
- Email address for SNS notifications

## Quick Start

1. Follow the **DEPLOYMENT_GUIDE.md** for step-by-step setup
2. Use **TESTING_GUIDE.md** to verify your deployment
3. Refer to **docs/TROUBLESHOOTING.md** if you encounter issues

## Requirements Met

✅ SQS queues for message handling  
✅ SNS topics for notifications  
✅ Step Functions for orchestration  
✅ Lambda functions for key tasks  
✅ JSON configurations included  
✅ Complete documentation  
✅ Message flow diagram  

## Important Notes for AWS Academy

- This project is designed for AWS Academy Learner Labs
- IAM roles are automatically created by AWS Academy
- Use Python 3.11 runtime (Node.js 18.x not available)
- All environment variables must use correct ARNs/URLs
- SQS requires **Queue URL** (not ARN) for send_message operations

## License

Educational project for AWS Academy coursework.
