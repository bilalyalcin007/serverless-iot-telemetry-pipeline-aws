# 🚗📡 IoT Vehicle Telemetry Pipeline on AWS

End-to-end serverless data pipeline for ingesting, storing, and analyzing vehicle telemetry data using AWS.

**Author:** Bilal Yalcin  

---

## 1. Project Overview

This project implements a realistic **IoT-style vehicle telemetry pipeline** on AWS.

A simulated IoT device running on an **EC2 bastion host** sends vehicle telemetry (e.g., `vehicle_id`, `speed`, `battery`, `temperature`) to an **Amazon API Gateway** endpoint. The request triggers an **AWS Lambda** function which:

- Validates and enriches the payload  
- Stores **raw data** in Amazon **S3**  
- Stores **metadata** in Amazon **DynamoDB**

The data is then:

- Discovered and cataloged by an **AWS Glue Crawler**  
- Queried using **Amazon Athena**  
- Monitored using a **CloudWatch Dashboard**

This architecture follows real-world **serverless**, **event-driven**, and **data lake** patterns often used in automotive, IoT, and telemetry platforms.

---

## 2. Architecture

### 2.1 High-Level Diagram

![Architecture](screenshot/architecture.png)

### 2.2 Main Components

- **Networking & Compute**
  - VPC, Subnets, Route Tables, Internet Gateway, Security Group  
  - EC2 bastion host (used as an IoT device simulator via `curl`)

- **Ingestion & Processing**
  - Amazon API Gateway (REST API, `POST /ingest`)  
  - AWS Lambda function (ingests and routes data to storage services)

- **Storage**
  - Amazon S3 (raw + processed telemetry data)  
  - Amazon DynamoDB (telemetry metadata and latest state)

- **Catalog & Analytics**
  - AWS Glue Crawler (schema & partition discovery)  
  - AWS Glue Data Catalog (table definitions)  
  - Amazon Athena (SQL queries over S3 data lake)

- **Monitoring**
  - Amazon CloudWatch Dashboard (Lambda, API Gateway, DynamoDB metrics)

---

## 3. End-to-End Lifecycle (Option 2)

1. **Networking & EC2 Setup**
   - Create a dedicated VPC, subnets, route table, internet gateway, and security group.
   - Launch an EC2 instance inside the VPC as the **IoT simulator**.
   - Connect to EC2 using SSH and send HTTP requests to API Gateway.

2. **Ingestion**
   - Configure **API Gateway** with a `POST /ingest` endpoint.
   - Integrate it with **AWS Lambda** using proxy integration.

3. **Processing**
   - Lambda function:
     - Parses JSON payload from the request body.
     - Validates required fields like `vehicle_id`.
     - Adds `ingest_time` using UTC timestamps.
     - Writes data to S3 and DynamoDB.

4. **Storage**
   - **S3 Raw Bucket**: stores raw or minimally processed JSON.
   - **S3 Processed Bucket**: optionally stores cleaned, partitioned data.
   - **DynamoDB**: stores metadata for fast lookups and dashboards.

5. **Catalog & Analytics**
   - **Glue Crawler** scans S3 and updates the Glue Data Catalog.
   - **Athena** queries the S3 data lake using SQL, including views and aggregations.

6. **Testing & Monitoring**
   - Use **Postman** and **curl** to send sample events.
   - Use **CloudWatch** to monitor Lambda performance, errors, and API Gateway metrics.

---

## 4. Networking & EC2 Setup

### 4.1 VPC and Subnets

A custom VPC is created to host the EC2 bastion host (telemetry simulator):

- VPC with CIDR block (e.g., `10.0.0.0/16`)
- Public subnets for the EC2 instance
- Associated route table with route to an internet gateway
- Security group allowing SSH from a trusted IP

**Screenshots:**

- VPC  
  ![VPC](screenshot/vpc.png)

- Subnets  
  ![Subnets](screenshot/subnets.png)

- Internet Gateway  
  ![Internet Gateway](screenshot/internet-gateway.png)

- Route Table  
  ![Route Table](screenshot/route-tables.png)

- Security Group  
  ![Security Group](screenshot/security-groups.png)

### 4.2 EC2 Bastion Host (IoT Simulator)

An EC2 instance is launched in the VPC and used to simulate IoT devices sending HTTP requests.

**Screenshots:**

- EC2 Instance  
  ![EC2](screenshot/ec2.png)

- SSH Session (connected to EC2)  
  ![SSH](screenshot/ec2-connected-SSH.png)

From this instance you can run `curl` commands to test the API Gateway endpoint.

---

## 5. Ingestion Layer – API Gateway & Lambda

### 5.1 Amazon API Gateway

The ingestion entry point is a REST API with a `POST /ingest` endpoint.

- Accepts JSON payload representing telemetry from a vehicle.
- Uses Lambda proxy integration to forward full event to Lambda.

**Screenshot:**

- API Gateway Configuration  
  ![API Gateway](screenshot/api-gateway.png)

---

### 5.2 AWS Lambda – Telemetry Ingestion

The Lambda function is responsible for:

- Parsing `event["body"]` from API Gateway.
- Validating a minimum set of fields (e.g. `vehicle_id`).
- Generating an `ingest_time` timestamp.
- Writing data to:
  - S3 (raw / processed)
  - DynamoDB (metadata record)

Environment variables are used to make the function configurable:

- `RAW_BUCKET`
- `PROCESSED_BUCKET`
- `DDB_TABLE`

**Screenshots:**

- Lambda Overview  
  ![Lambda](screenshot/lambda.png)

- Lambda Configuration / Code View  
  ![Lambda Code 2](screenshot/lambda1.png)

- Lambda Additional View  
  ![Lambda Code 3](screenshot/lambda2.png)

- Lambda Environment Variables  
  ![Lambda Env Vars](screenshot/lambda-env-var.png)

> The full Python source code is stored in this repository as:  
> `iot_lambda_function.py`

---

## 6. Storage Layer – S3 & DynamoDB

### 6.1 Amazon S3 – Raw & Processed Telemetry

Two main S3 buckets are used:

- **Raw bucket** – to store the original or minimally processed telemetry data.
- **Processed bucket** – to store cleaned, partitioned, and analytics-ready data (if used in this version of the pipeline).

**Screenshots:**

- S3 Buckets Overview  
  ![S3 Buckets](screenshot/s3-buckets.png)

- Raw Telemetry Data  
  ![Raw Data](screenshot/s3-raw-data.png)

- Processed Telemetry Data  
  ![Processed Data](screenshot/s3-processed-data.png)

---

### 6.2 Amazon DynamoDB – Metadata Table

DynamoDB is used as a metadata and state store for each vehicle. Typical fields might include:

- `vehicle_id`
- `speed`
- `battery`
- `temperature`
- `ingest_time`

**Screenshot:**

- DynamoDB Tables  
  ![DynamoDB](screenshot/dynamoDB-table.png)

---

## 7. Catalog & Analytics – Glue Crawler & Athena

### 7.1 AWS Glue Crawler

A Glue Crawler is configured to scan the S3 location that holds telemetry data so that:

- Partitions (e.g. `year`, `month`, `day`) can be discovered automatically.
- A table is created/updated in the **Glue Data Catalog**.

**Screenshot:**

- Glue Crawler   
  ![Glue Crawler](screenshot/glue-crawler.png)

---

### 7.2 Amazon Athena – Queries & Views

Athena is used to run analytical queries over the data stored in S3 via external tables defined in the Glue Data Catalog.

Common tasks include:

- Repairing table partitions:
  ![Athena Repair](screenshot/athena-Q1.png)

- Basic queries to inspect data:
  ![Athena Q1](screenshot/athena-Q2.png)

- Aggregation queries (e.g., average speed over time):
  ![Athena Q2](screenshot/athena-Q3.png)

- Creating a summary view:
  ![Athena Create View](screenshot/athena-Q4.png)

- Querying the summary view or final dataset:
  ![Athena Q3](screenshot/athena-Q5.png)

These queries demonstrate how to go from raw ingestion to analytics and reporting.

---

## 8. Testing & Monitoring

### 8.1 Functional Testing – Postman

Postman is used to verify that:

- The API Gateway endpoint accepts requests.
- The Lambda function processes and returns a valid response.
- The pipeline is properly wired end-to-end.

**Screenshot:**

- Postman 200 OK Response  
  ![Postman 200 OK](screenshot/postman-test.png)

---

### 8.2 Observability – CloudWatch Dashboard

A custom **CloudWatch Dashboard** monitors:

- Lambda invocations and errors  
- API Gateway latency and status codes  
- DynamoDB read/write metrics  

**Screenshot:**

- CloudWatch Dashboard  
  ![CloudWatch Dashboard](screenshot/cloudwatch-dashboard.png)

---

## 9. Repository Structure

A suggested repository layout for this project:

```bash
