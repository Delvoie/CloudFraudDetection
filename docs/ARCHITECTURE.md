# Architecture Documentation

## System Architecture Overview

The Cloud Fraud Detection system is a serverless, event-driven architecture built on AWS services. It demonstrates enterprise patterns for transaction processing, fraud detection, and real-time alerting.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CLOUD FRAUD DETECTION SYSTEM                      │
└─────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   External   │
    │   System /   │
    │   Test Data  │
    └──────┬───────┘
           │
           │ (1) Send Transaction
           ▼
    ┌──────────────────────┐
    │  TransactionQueue    │
    │       (SQS)          │
    └──────┬───────────────┘
           │
           │ (2) Trigger
           ▼
    ┌──────────────────────────┐
    │  ProcessTransaction      │
    │      (Lambda)            │
    │  - Receives SQS msg      │
    │  - Starts workflow       │
    └──────┬───────────────────┘
           │
           │ (3) StartExecution
           ▼
    ┌────────────────────────────────────────────────────┐
    │         FraudDetectionWorkflow (Step Functions)    │
    │                                                    │
    │  ┌──────────────────────┐                         │
    │  │ EvaluateTransaction  │                         │
    │  │      (Lambda)        │                         │
    │  │  - Check amount      │                         │
    │  │  - Return isFraud    │                         │
    │  └──────┬───────────────┘                         │
    │         │                                          │
    │         │ (4) Decision                            │
    │         ▼                                          │
    │  ┌──────────────┐                                 │
    │  │  FraudCheck  │                                 │
    │  │  (Choice)    │                                 │
    │  └──┬────────┬──┘                                 │
    │     │        │                                     │
    │     │        └─────────────────────┐              │
    │     │ isFraud=true                 │ isFraud=false│
    │     ▼                               ▼              │
    │  ┌─────────────┐           ┌────────────────┐    │
    │  │  SendAlert  │           │ SendToCleanQueue│   │
    │  │  (Lambda)   │           │    (Lambda)     │   │
    │  └─────┬───────┘           └────────┬───────┘    │
    │        │                             │             │
    └────────┼─────────────────────────────┼────────────┘
             │ (5) Publish                 │ (6) Send
             ▼                              ▼
    ┌─────────────────┐          ┌──────────────────────┐
    │ FraudAlertsTopic│          │CleanTransactionsQueue│
    │      (SNS)      │          │       (SQS)          │
    └────────┬────────┘          └──────────────────────┘
             │
             │ (7) Email Notification
             ▼
    ┌─────────────────┐
    │  Email Inbox    │
    │  (Subscriber)   │
    └─────────────────┘
```

---

## Data Flow Sequence

### Fraudulent Transaction Flow

1. **Transaction Submission** → External system sends transaction to `TransactionQueue`
2. **Lambda Trigger** → `ProcessTransaction` Lambda automatically invoked by SQS
3. **Workflow Start** → Lambda starts `FraudDetectionWorkflow` Step Functions execution
4. **Evaluation** → `EvaluateTransaction` Lambda analyzes transaction
   - Input: `{"transactionId": "TXN-001", "amount": 25000}`
   - Output: `{"isFraud": true, "transaction": {...}}`
5. **Decision** → Step Functions `Choice` state routes based on `isFraud`
6. **Alert** → `SendAlert` Lambda publishes to SNS
7. **Notification** → SNS sends email to subscribed addresses

### Clean Transaction Flow

1. **Transaction Submission** → Same as above
2. **Lambda Trigger** → Same as above
3. **Workflow Start** → Same as above
4. **Evaluation** → `EvaluateTransaction` Lambda analyzes transaction
   - Input: `{"transactionId": "TXN-002", "amount": 150}`
   - Output: `{"isFraud": false, "transaction": {...}}`
5. **Decision** → Step Functions routes to Clean path
6. **Storage** → `SendToCleanQueue` Lambda sends to `CleanTransactionsQueue`
7. **Archive** → Transaction stored for record-keeping

---

## Component Details

### 1. SQS Queues

#### TransactionQueue
- **Purpose**: Entry point for all transactions
- **Type**: Standard queue
- **Retention**: 4 days (default)
- **Visibility Timeout**: 30 seconds
- **Trigger**: ProcessTransaction Lambda

#### CleanTransactionsQueue
- **Purpose**: Storage for cleared transactions
- **Type**: Standard queue
- **Pattern**: Acts as a simple data lake for non-fraudulent transactions
- **Future Use**: Could feed analytics/reporting system

### 2. SNS Topic

#### FraudAlertsTopic
- **Purpose**: Real-time fraud notifications
- **Protocol**: Email (can extend to SMS, HTTP, SQS)
- **Subscribers**: Operations team, fraud analysts
- **Message Format**: JSON with transaction details

### 3. Lambda Functions

| Function | Runtime | Trigger | Purpose | Timeout |
|----------|---------|---------|---------|---------|
| ProcessTransaction | Python 3.11 | SQS (TransactionQueue) | Orchestration entry point | 30s |
| EvaluateTransaction | Python 3.11 | Step Functions | Fraud detection logic | 10s |
| SendAlert | Python 3.11 | Step Functions | SNS notification | 10s |
| SendToCleanQueue | Python 3.11 | Step Functions | Storage routing | 10s |

### 4. Step Functions State Machine

**Type**: Standard workflow  
**States**: 4 (Task, Task, Choice, 2x Task endpoints)  
**Pattern**: Orchestration with conditional routing  

**State Definitions**:

1. **EvaluateTransaction** (Task)
   - Invokes Lambda
   - Stores result in `$.evaluation`

2. **FraudCheck** (Choice)
   - Condition: `$.evaluation.isFraud == true`
   - True → SendAlert
   - False → Clean

3. **SendAlert** (Task)
   - Invokes SNS Lambda
   - Terminates (End: true)

4. **Clean** (Task)
   - Invokes storage Lambda
   - Terminates (End: true)

---

## Design Patterns

### 1. Event-Driven Architecture
- **Decoupling**: SQS decouples producers from consumers
- **Async Processing**: Step Functions enables async orchestration
- **Scalability**: Each component scales independently

### 2. Serverless Pattern
- **No Infrastructure Management**: All compute is Lambda/Step Functions
- **Pay-per-Use**: Charged only for executions
- **Auto-Scaling**: AWS handles all scaling automatically

### 3. Orchestration vs Choreography
- **Orchestration**: Step Functions centrally controls workflow
- **Benefits**: Clear workflow visibility, easy to modify logic, audit trail

### 4. Fan-Out Notification
- **SNS**: Single publish can notify multiple subscribers
- **Extensibility**: Easy to add Slack, PagerDuty, etc.

---

## Fraud Detection Logic

### Current Rule
```python
is_fraud = amount > 10000
```

### Extensibility Points

The `EvaluateTransaction` Lambda can be extended with:

1. **Velocity Checks**
   ```python
   if transaction_count_last_hour > 10:
       is_fraud = True
   ```

2. **Geolocation Analysis**
   ```python
   if user_location != typical_location:
       fraud_score += 30
   ```

3. **Merchant Risk**
   ```python
   if merchant in high_risk_list:
       fraud_score += 20
   ```

4. **Machine Learning Integration**
   ```python
   fraud_probability = sagemaker_endpoint.predict(features)
   is_fraud = fraud_probability > 0.75
   ```

---

## Scalability & Performance

### Throughput Capacity

| Component | Max Throughput | Bottleneck |
|-----------|----------------|------------|
| SQS Queue | 3,000 msg/sec (standard) | N/A |
| Lambda (concurrent) | 1,000 concurrent executions | Account limit |
| Step Functions | 2,000 executions/sec | N/A |
| SNS | 30,000 msg/sec | N/A |

### Expected Latency

**End-to-End (SQS → Email)**: ~2-5 seconds

- SQS → Lambda trigger: ~10-50ms
- ProcessTransaction: ~200-300ms
- Step Functions start: ~50ms
- EvaluateTransaction: ~100ms
- SendAlert: ~100ms
- SNS publish: ~50ms
- Email delivery: 1-3 seconds

---

## Cost Estimation (AWS Academy - Free Tier)

All services used fall within AWS Free Tier:

| Service | Free Tier | Demo Usage | Cost |
|---------|-----------|------------|------|
| Lambda | 1M requests/month | ~100 requests | $0 |
| Step Functions | 4,000 state transitions | ~400 transitions | $0 |
| SQS | 1M requests | ~100 requests | $0 |
| SNS | 1,000 emails | ~50 emails | $0 |

**Total Demo Cost**: $0 (within free tier)

---

## Security Considerations

### IAM Roles (Auto-Managed in AWS Academy)

1. **Lambda Execution Role**
   - `sqs:ReceiveMessage`, `sqs:DeleteMessage` (TransactionQueue)
   - `sqs:SendMessage` (CleanTransactionsQueue)
   - `states:StartExecution` (Step Functions)
   - `sns:Publish` (SNS Topic)
   - `logs:CreateLogGroup`, `logs:PutLogEvents` (CloudWatch)

2. **Step Functions Role**
   - `lambda:InvokeFunction` (all 3 Lambdas)

### Data Protection

- **Encryption at Rest**: SQS/SNS encrypted by default (AWS-managed keys)
- **Encryption in Transit**: All AWS API calls use TLS 1.2+
- **No PII Storage**: Transaction data not persisted (only in queues/logs)

### Best Practices Implemented

✅ Least privilege IAM roles  
✅ Environment variable for configuration (not hardcoded)  
✅ Error handling in Lambda functions  
✅ CloudWatch logging enabled  
✅ No secrets in code  

---

## Monitoring & Observability

### CloudWatch Metrics

**Lambda**:
- Invocations
- Duration
- Errors
- Throttles

**Step Functions**:
- ExecutionsStarted
- ExecutionsSucceeded
- ExecutionsFailed
- ExecutionTime

**SQS**:
- NumberOfMessagesSent
- NumberOfMessagesReceived
- ApproximateAgeOfOldestMessage

### CloudWatch Logs

Each Lambda function has log group:
- `/aws/lambda/ProcessTransaction`
- `/aws/lambda/EvaluateTransaction`
- `/aws/lambda/SendAlert`
- `/aws/lambda/SendToCleanQueue`

### Step Functions Visual Workflow

Real-time execution visualization shows:
- Current state
- State transitions
- Input/output for each state
- Execution duration
- Error details (if any)

---

## Disaster Recovery

### Fault Tolerance

- **SQS**: Messages retained for 4 days
- **Lambda**: Automatic retry on failure (SQS trigger)
- **Step Functions**: Automatic retry can be configured per state
- **SNS**: Delivery retry with exponential backoff

### Dead Letter Queue (Future Enhancement)

```json
{
  "RedrivePolicy": {
    "deadLetterTargetArn": "arn:aws:sqs:region:account:fraud-dlq",
    "maxReceiveCount": 3
  }
}
```

---

## Future Enhancements

1. **DynamoDB Integration**
   - Store transaction history
   - Track user patterns
   - Enable ML training

2. **Machine Learning**
   - SageMaker endpoint for fraud scoring
   - Real-time model inference

3. **API Gateway**
   - REST API for transaction submission
   - Webhook for external systems

4. **EventBridge Rules**
   - Monitor Step Functions failures
   - Automated incident response

5. **X-Ray Tracing**
   - End-to-end distributed tracing
   - Performance bottleneck identification

---

## References

- [AWS Step Functions Documentation](https://docs.aws.amazon.com/step-functions/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Amazon States Language](https://docs.aws.amazon.com/step-functions/latest/dg/concepts-amazon-states-language.html)
- [SQS Standard Queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues.html)

---

**Document Version**: 1.0  
**Last Updated**: December 2, 2025  
**Author**: AWS Academy Student Project
