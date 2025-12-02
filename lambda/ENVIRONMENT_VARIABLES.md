# Lambda Function Environment Variables Reference

Quick reference for all environment variables needed for each Lambda function.

---

## ProcessTransaction

**Location**: Lambda → ProcessTransaction → Configuration → Environment variables

| Key | Value Type | Description | Example |
|-----|------------|-------------|---------|
| `STATE_MACHINE_ARN` | ARN | Step Functions state machine ARN | `arn:aws:states:us-east-1:905418114457:stateMachine:FraudDetectionWorkflow` |

**How to Get Value**:
1. Go to Step Functions → State machines
2. Click on FraudDetectionWorkflow
3. Copy ARN from details section

---

## EvaluateTransaction

**No environment variables required** ✅

This function only evaluates transaction data and returns a result. No external resources needed.

---

## SendAlert

**Location**: Lambda → SendAlert → Configuration → Environment variables

| Key | Value Type | Description | Example |
|-----|------------|-------------|---------|
| `SNS_TOPIC_ARN` | ARN | SNS topic for fraud alerts | `arn:aws:sns:us-east-1:905418114457:FraudAlertsTopic` |

**How to Get Value**:
1. Go to SNS → Topics
2. Click on FraudAlertsTopic
3. Copy ARN from details section

---

## SendToCleanQueue

**Location**: Lambda → SendToCleanQueue → Configuration → Environment variables

| Key | Value Type | Description | Example |
|-----|------------|-------------|---------|
| `CLEAN_QUEUE_URL` | **URL** (not ARN!) | SQS queue URL for clean transactions | `https://sqs.us-east-1.amazonaws.com/905418114457/CleanTransactionsQueue` |

**How to Get Value**:
1. Go to SQS → Queues
2. Click on CleanTransactionsQueue
3. Copy **Queue URL** from details (under Details tab, not ARN!)

⚠️ **IMPORTANT**: Must use Queue URL, not ARN. SQS send_message requires URL format.

---

## Common Mistakes

### ❌ Using ARN instead of URL for SQS
**Wrong**: `arn:aws:sqs:us-east-1:905418114457:CleanTransactionsQueue`  
**Correct**: `https://sqs.us-east-1.amazonaws.com/905418114457/CleanTransactionsQueue`

### ❌ Wrong Region
All ARNs must use the same region as your resources (usually `us-east-1` in AWS Academy).

### ❌ Copy-Paste Errors
- Extra spaces before/after ARN
- Missing parts of the ARN
- Wrong account ID

---

## Quick Copy Template

Replace `REGION` and `ACCOUNT_ID` with your values:

```bash
# ProcessTransaction
STATE_MACHINE_ARN=arn:aws:states:REGION:ACCOUNT_ID:stateMachine:FraudDetectionWorkflow

# SendAlert
SNS_TOPIC_ARN=arn:aws:sns:REGION:ACCOUNT_ID:FraudAlertsTopic

# SendToCleanQueue
CLEAN_QUEUE_URL=https://sqs.REGION.amazonaws.com/ACCOUNT_ID/CleanTransactionsQueue
```

**Example with actual values**:
```bash
# ProcessTransaction
STATE_MACHINE_ARN=arn:aws:states:us-east-1:905418114457:stateMachine:FraudDetectionWorkflow

# SendAlert
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:905418114457:FraudAlertsTopic

# SendToCleanQueue
CLEAN_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/905418114457/CleanTransactionsQueue
```

---

## Verification

After setting all environment variables, verify in AWS Console:

1. **ProcessTransaction** → Configuration → Environment variables → Should show 1 variable
2. **EvaluateTransaction** → Configuration → Environment variables → Should show 0 variables
3. **SendAlert** → Configuration → Environment variables → Should show 1 variable
4. **SendToCleanQueue** → Configuration → Environment variables → Should show 1 variable

---

## Finding Your Account ID

**Method 1**: AWS Console
1. Click your username in top-right corner
2. Account ID shown in dropdown

**Method 2**: AWS CloudShell
```bash
aws sts get-caller-identity --query Account --output text
```

**Method 3**: Look at any existing ARN
```
arn:aws:sns:us-east-1:905418114457:SomeTopic
                       ^^^^^^^^^^^^
                       This is your Account ID
```

---

## Troubleshooting Environment Variables

See **docs/TROUBLESHOOTING.md** for detailed error messages and solutions.
