# Food Delivery App - Terraform & AWS Lambda

A serverless food delivery web application with REST API backend built with Terraform and AWS Lambda.

## Architecture

- **Frontend**: HTML/CSS/JavaScript served via API Gateway
- **Backend**: Python Lambda functions with Flask-like routing
- **Database**: DynamoDB for order storage
- **Infrastructure**: Terraform for IaC

## Prerequisites

- AWS CLI configured with appropriate permissions
- Terraform installed
- Python 3.9+
- AWS SAM CLI (for local testing)

## Deployment

### 1. Initialize Terraform

```bash
cd terraform
terraform init
terraform apply -auto-approve
