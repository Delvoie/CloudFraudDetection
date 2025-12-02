# Troubleshooting Guide

Common issues and solutions for the Cloud Fraud Detection system in AWS Academy.

---

## Table of Contents

1. [Lambda Function Issues](#lambda-function-issues)
2. [Step Functions Issues](#step-functions-issues)
3. [SQS Issues](#sqs-issues)
4. [SNS Issues](#sns-issues)
5. [Environment Variable Issues](#environment-variable-issues)
6. [CloudWatch Logs Issues](#cloudwatch-logs-issues)

---

## Lambda Function Issues

### ❌ ProcessTransaction has no CloudWatch logs

**Symptoms**: No log entries when sending messages to TransactionQueue

**Causes & Solutions**:

1. **SQS Trigger Not Attached**
   - Go to Lambda → ProcessTransaction → Configuration → Triggers
   - If no trigger, click Add trigger → SQS → TransactionQueue
   - Batch size: 1

2. **Lambda is Disabled**
   - Check Lambda status in console
   - Ensure it's not throttled or disabled

3. **Wrong Queue Selected**
   - Verify trigger is on TransactionQueue (not CleanTransactionsQueue)

---

### ❌ Error: "An error occurred (InvalidAddress) when calling the SendMessage operation"

**Full Error**:
```
The address arn:aws:sqs:us-east-1:123456789012:CleanTransactionsQueue is not valid for this endpoint.
```

**Cause**: Using Queue ARN instead of Queue URL

**Solution**:
1. Go to SQS → CleanTransactionsQueue → Details
2. Copy **Queue URL** (not ARN):
   - ✅ Correct: `https://sqs.us-east-1.amazonaws.com/123456789012/CleanTransactionsQueue`
   - ❌ Wrong: `arn:aws:sqs:us-east-1:123456789012:CleanTransactionsQueue`
3. Update SendToCleanQueue Lambda environment variable `CLEAN_QUEUE_URL`

---

### ❌ Lambda timeout errors

**Symptoms**: Task timed out after X seconds

**Solutions**:
1. Increase timeout:
   - Go to Lambda → Configuration → General configuration
   - Increase timeout to 30 seconds (ProcessTransaction) or 10 seconds (others)
2. Check for infinite loops in code
3. Verify external API calls are responding

---

## Step Functions Issues

### ❌ ExecutionFailed: Lambda returned error

**Symptoms**: Step Functions execution shows red (failed) state

**Solutions**:

1. **Click on the failed state** to see error details
2. Check the "Exception" field for error message
3. Common causes:
   - Missing environment variable in Lambda
   - Lambda code error (check CloudWatch Logs)
   - Wrong ARN in Step Functions definition

---

### ❌ Step Functions can't invoke Lambda

**Error**: `Lambda.SdkClientException` or `AccessDeniedException`

**Cause**: Step Functions role lacks permission

**Solution**:
1. AWS Academy should auto-create this, but verify:
   - Go to IAM → Roles → Search for "StepFunctions"
   - Check policy includes `lambda:InvokeFunction`
2. If issue persists:
   - Delete and recreate state machine
   - Choose "Create new role" option

---

### ❌ Wrong Lambda invoked or wrong path taken

**Symptoms**: Fraudulent transaction goes to Clean path (or vice versa)

**Solution**:
1. Check Step Functions execution details
2. Look at EvaluateTransaction output:
   ```json
   {
     "evaluation": {
       "isFraud": true,  <-- Should be true for amount > 10000
       "transactionId": "TXN-001"
     }
   }
   ```
3. Verify Choice state condition:
   ```json
   "Variable": "$.evaluation.isFraud",
   "BooleanEquals": true
   ```
4. Check transaction amount is actually > 10000

---

## SQS Issues

### ❌ Messages not triggering Lambda

**Symptoms**: Send message to TransactionQueue, but Lambda doesn't run

**Solutions**:

1. **Verify Trigger**:
   - Lambda → ProcessTransaction → Configuration → Triggers
   - Should show TransactionQueue with status "Enabled"

2. **Check Message Format**:
   - Message must be valid JSON
   - ❌ Bad: `TXN-001, 5000, user-1` (not JSON)
   - ✅ Good: `{"transactionId": "TXN-001", "amount": 5000}`

3. **Check Queue Visibility Timeout**:
   - Should be at least 6x Lambda timeout
   - Lambda timeout: 30s → Queue visibility: 30s (OK)

---

### ❌ Messages stuck in queue

**Symptoms**: Messages remain in TransactionQueue without processing

**Solutions**:

1. **Check Approximate Age of Messages** in SQS console
2. If very old, Lambda may be failing:
   - Check CloudWatch Logs for errors
   - Verify Lambda has correct environment variables

3. **Purge Queue** (testing only):
   - SQS → TransactionQueue → Purge queue
   - Removes all messages (use carefully!)

---

## SNS Issues

### ❌ No email received after fraud detection

**Symptoms**: Step Functions shows SendAlert succeeded, but no email

**Solutions**:

1. **Check Subscription Status**:
   - SNS → Topics → FraudAlertsTopic → Subscriptions
   - Status must be **Confirmed** (not Pending)
   - If Pending: Check email for confirmation link (including spam)

2. **Check Spam Folder**:
   - AWS emails often land in spam
   - Add `no-reply@sns.amazonaws.com` to safe senders

3. **Verify SNS_TOPIC_ARN**:
   - Go to SendAlert Lambda → Configuration → Environment variables
   - `SNS_TOPIC_ARN` should be: `arn:aws:sns:REGION:ACCOUNT:FraudAlertsTopic`
   - Must match your actual topic ARN

4. **Check CloudWatch Logs**:
   - `/aws/lambda/SendAlert`
   - Look for successful SNS publish:
     ```
     Alert sent for transaction TXN-001. MessageId: abc123...
     ```

---

### ❌ SNS publish fails with AccessDenied

**Error**: `User: ... is not authorized to perform: SNS:Publish`

**Solution**:
- AWS Academy should auto-grant this permission
- Delete and recreate SendAlert Lambda
- Ensure you're using the default execution role (don't select custom role)

---

## Environment Variable Issues

### ❌ KeyError: 'SNS_TOPIC_ARN' or 'CLEAN_QUEUE_URL'

**Cause**: Environment variable not set in Lambda

**Solution**:
1. Go to Lambda → Configuration → Environment variables
2. Click Edit
3. Add missing variable:

| Lambda | Variable | Value Format | Example |
|--------|----------|--------------|---------|
| SendAlert | `SNS_TOPIC_ARN` | ARN | `arn:aws:sns:us-east-1:123:FraudAlertsTopic` |
| SendToCleanQueue | `CLEAN_QUEUE_URL` | URL | `https://sqs.us-east-1.amazonaws.com/123/CleanTransactionsQueue` |
| ProcessTransaction | `STATE_MACHINE_ARN` | ARN | `arn:aws:states:us-east-1:123:stateMachine:FraudDetectionWorkflow` |

---

### ❌ Wrong ARN format or region mismatch

**Symptoms**: `InvalidParameter` or `ResourceNotFound` errors

**Solution**:
1. Verify your AWS region (top-right of console)
2. All ARNs must use same region
3. Check account ID is correct (12 digits)

**Example ARN Anatomy**:
```
arn:aws:sns:us-east-1:905418114457:FraudAlertsTopic
      │    │      │          │             │
      │    │      │          │             └─ Resource name
      │    │      │          └─────────────── Account ID
      │    │      └────────────────────────── Region
      │    └───────────────────────────────── Service
      └────────────────────────────────────── AWS partition
```

---

## CloudWatch Logs Issues

### ❌ No logs appearing for Lambda function

**Symptoms**: Can't find logs in CloudWatch

**Solutions**:

1. **Wait a few seconds**: Logs can take 10-30 seconds to appear

2. **Check Log Group Name**:
   - Must be: `/aws/lambda/[FunctionName]`
   - Example: `/aws/lambda/ProcessTransaction`

3. **Check Lambda Execution Role**:
   - AWS Academy should auto-grant CloudWatch permissions
   - If missing, recreate Lambda function

4. **Ensure Lambda Actually Ran**:
   - Check Lambda → Monitor → Invocations graph
   - If no invocations, trigger wasn't hit

---

### ❌ Logs show REPORT but no custom print statements

**Example**:
```
START RequestId: abc-123
END RequestId: abc-123
REPORT RequestId: abc-123 Duration: 275.30 ms
```

**Cause**: Lambda executed but your print statements may not be captured

**Solution**:
1. Ensure you're using `print()` in Python (not `console.log`)
2. Check you're looking at the correct log stream (most recent)
3. Click "Expand all" to see full log details

---

## General Debugging Steps

### Step-by-Step Debugging Process

1. **Identify Where Failure Occurs**:
   - SQS → Lambda? (Check CloudWatch Logs)
   - Lambda → Step Functions? (Check Step Functions executions)
   - Step Functions → SNS? (Check SendAlert logs)

2. **Check CloudWatch Logs** for each component:
   ```
   /aws/lambda/ProcessTransaction
   /aws/lambda/EvaluateTransaction
   /aws/lambda/SendAlert
   /aws/lambda/SendToCleanQueue
   ```

3. **Verify Environment Variables**:
   - All ARNs/URLs correct?
   - Copied from correct resource?
   - No extra spaces or typos?

4. **Test Components Individually**:
   - Use Lambda Test feature with sample events
   - Start Step Functions manually
   - Send test message to SQS

5. **Check Resource Names Match**:
   - Lambda function names match ARNs in Step Functions?
   - Queue names correct?
   - Topic name correct?

---

## Quick Diagnostic Checklist

Run through this list systematically:

### SQS
- [ ] TransactionQueue exists
- [ ] CleanTransactionsQueue exists
- [ ] Messages are valid JSON

### SNS
- [ ] FraudAlertsTopic exists
- [ ] Email subscription is **Confirmed**
- [ ] Checked spam folder

### Lambda Functions
- [ ] All 4 functions deployed
- [ ] All using Python 3.11
- [ ] Code pasted correctly
- [ ] Environment variables set

### Step Functions
- [ ] State machine created
- [ ] ARNs in JSON match Lambda functions
- [ ] REGION and ACCOUNT_ID replaced

### Triggers
- [ ] ProcessTransaction has SQS trigger
- [ ] Trigger is on TransactionQueue
- [ ] Trigger is Enabled

### End-to-End
- [ ] Can send message to TransactionQueue
- [ ] ProcessTransaction CloudWatch logs appear
- [ ] Step Functions execution starts
- [ ] Fraud email received OR Clean queue has message

---

## Getting Help

### Information to Collect Before Asking for Help

1. **Error Message** (exact text)
2. **CloudWatch Logs** (copy full log output)
3. **Step Functions Execution Details** (screenshot of failed state)
4. **Environment Variables** (values you set)
5. **AWS Region** (where you deployed)
6. **Test Data** (JSON you sent to SQS)

### AWS Academy Support

- Lab support through your instructor
- AWS documentation: https://docs.aws.amazon.com
- This project's GitHub Issues (if available)

---

## Common Error Messages Reference

| Error Message | Component | Likely Cause | Fix |
|---------------|-----------|--------------|-----|
| `InvalidAddress` | SendToCleanQueue | Using ARN instead of URL | Use Queue URL |
| `KeyError: 'SNS_TOPIC_ARN'` | SendAlert | Missing env variable | Add environment variable |
| `AccessDenied` | Any | IAM permission issue | Recreate resource with default role |
| `ResourceNotFound` | Step Functions | Wrong ARN | Verify ARN matches actual resource |
| `Task timed out` | Lambda | Function too slow | Increase timeout or optimize code |
| `No logs` | Lambda | Never executed | Check trigger is attached |

---

## Still Stuck?

1. **Start Fresh**: Sometimes easiest to delete and recreate one component
2. **Compare with Working Example**: Use test events in Lambda to isolate issue
3. **Check AWS Service Health**: Rarely, AWS services have outages
4. **Review TESTING_GUIDE.md**: Step-by-step verification process

---

**Last Updated**: December 2, 2025
