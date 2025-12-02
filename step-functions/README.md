# FraudDetectionWorkflow State Machine Definition

## Overview
This JSON file defines the AWS Step Functions state machine that orchestrates the fraud detection workflow.

## Configuration Instructions

**BEFORE USING:** Replace the following placeholders in `FraudDetectionWorkflow.json`:

1. **REGION** - Your AWS region (e.g., `us-east-1`)
2. **ACCOUNT_ID** - Your AWS account ID (12-digit number)

## How to Find Your Values

### Find Your AWS Region
- Look at the top-right corner of the AWS Console
- Common values: `us-east-1`, `us-west-2`, `eu-west-1`

### Find Your Account ID
1. Click your username in the top-right corner of AWS Console
2. Your account ID is shown in the dropdown
3. Or run this AWS CLI command: `aws sts get-caller-identity --query Account --output text`

## Example Replacement

**Before:**
```json
"Resource": "arn:aws:lambda:REGION:ACCOUNT_ID:function:EvaluateTransaction"
```

**After:**
```json
"Resource": "arn:aws:lambda:us-east-1:905418114457:function:EvaluateTransaction"
```

## State Machine Flow

1. **EvaluateTransaction** - Analyzes transaction for fraud
2. **FraudCheck** - Decision point based on `isFraud` flag
3. **SendAlert** - If fraud detected → SNS notification
4. **Clean** - If clean → Send to storage queue

## Usage in AWS Console

1. Go to **AWS Step Functions** → **Create state machine**
2. Choose **Author with code snippets**
3. Select **Standard** workflow type
4. Paste the updated JSON
5. Name it: `FraudDetectionWorkflow`
6. Choose **Create new role** (AWS Academy auto-creates it)
7. Click **Create state machine**

## State Machine ARN Format

After creation, your state machine ARN will be:
```
arn:aws:states:REGION:ACCOUNT_ID:stateMachine:FraudDetectionWorkflow
```

This ARN is needed for the `ProcessTransaction` Lambda environment variable `STATE_MACHINE_ARN`.
