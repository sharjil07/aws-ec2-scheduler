# AWS Serverless Cost Optimization: Auto Start/Stop EC2 Instances

This project implements a serverless automation solution on AWS to manage the lifecycle of EC2 instances, significantly reducing cloud costs by stopping instances during non-business hours and starting them again when needed. This is a common and highly effective cost-saving strategy in many organizations.

The solution is event-driven, scalable, and secure, leveraging AWS Lambda, Amazon EventBridge, IAM, and resource tagging.

## Key Features

-   **Cost Reduction:** Achieves up to 60-70% cost savings on development/staging EC2 resources by ensuring they only run when necessary.
-   **Serverless Architecture:** No servers to manage for the automation itself. It's cost-effective, running only when triggered.
-   **Scalable & Maintainable:** Uses AWS resource tags to identify target instances. New instances can be added to the schedule simply by adding a tag, with no code changes required.
-   **Secure by Design:** Follows the Principle of Least Privilege with a narrowly-scoped IAM role, ensuring the function has only the permissions it needs.
-   **Reliable & Monitored:** Utilizes Amazon EventBridge for reliable cron-based scheduling and CloudWatch Logs for execution monitoring and debugging.

## Architecture

The architecture is simple yet powerful. Two EventBridge schedules are configured to trigger the "start" and "stop" Lambda functions at the appropriate times. The Lambda function then uses the AWS API to act on any EC2 instances with the correct tag (`Auto-Start-Stop: True`).

```mermaid
graph TD
    subgraph "Scheduler (EventBridge)"
        A[Schedule: Start Instances<br>cron(0 9 ? * MON-FRI *)]
        B[Schedule: Stop Instances<br>cron(30 17 ? * MON-FRI *)]
    end

    subgraph "Compute & Logic"
        C[Lambda: start-ec2-instances]
        D[Lambda: stop-ec2-instances]
        E[IAM Role<br>Permissions: ec2:Start, ec2:Stop, ec2:Describe]
    end

    subgraph "Target Resources"
        F[EC2 Instances<br>Tag: Auto-Start-Stop=True]
    end

    subgraph "Monitoring"
        G[CloudWatch Logs]
    end

    A --triggers--> C
    B --triggers--> D
    C --uses permissions from--> E
    D --uses permissions from--> E
    C --starts--> F
    D --stops--> F
    C --writes logs to--> G
    D --writes logs to--> G
```

## Technology Stack

-   **Compute:** AWS Lambda
-   **Orchestration & Scheduling:** Amazon EventBridge Scheduler
-   **Scripting:** Python 3.9+ with Boto3 SDK
-   **Security:** AWS IAM (Identity and Access Management)
-   **Monitoring:** Amazon CloudWatch Logs

## Deployment & Configuration

This guide assumes deployment via the AWS Management Console.

1.  **IAM Role & Policy:** Create an IAM role for Lambda with a policy granting permissions for `logs:*`, `ec2:DescribeInstances`, `ec2:StartInstances`, and `ec2:StopInstances`.
2.  **Lambda Functions:** Deploy the two Python scripts from the `src/` directory as separate Lambda functions (`start_instances` and `stop_instances`), attaching the IAM role created in the previous step.
3.  **EventBridge Schedules:** Create two recurring, cron-based schedules in EventBridge Scheduler, one for starting and one for stopping. Target the respective Lambda functions.
4.  **EC2 Instance Tagging:** To include an EC2 instance in this automation, simply add the following tag to it:
    -   **Key:** `Auto-Start-Stop`
    -   **Value:** `True`

The system is now fully configured.

## Troubleshooting

A common issue during setup is the Lambda function reporting "No instances found" even when instances are running. This is almost always caused by one of two issues:
1.  **Tag Mismatch:** The tag key or value on the EC2 instance does not exactly match what the script is looking for (e.g., typos, case sensitivity).
2.  **Region Mismatch:** The Lambda function and the EC2 instance are in different AWS regions.

This can be debugged by examining the CloudWatch logs for the Lambda function, which will show the exact filters being used in the search.
