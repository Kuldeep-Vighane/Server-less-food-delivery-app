# 🍕 Food Delivery App - Serverless AWS

A complete serverless food delivery application built with AWS cloud services and Terraform infrastructure as code.

## 📋 Project Overview

This is a showcase project demonstrating a full-stack serverless application with:
- **Frontend**: HTML/CSS/JavaScript web interface
- **Backend**: AWS Lambda with Python
- **Database**: DynamoDB for order management
- **Infrastructure**: Terraform for IaC
- **Architecture**: 100% serverless

## 🏗️ Architecture
Client → API Gateway → Lambda Function → DynamoDB


### Technology Stack
- **Compute**: AWS Lambda (Python 3.9)
- **API Layer**: AWS API Gateway HTTP API
- **Database**: Amazon DynamoDB
- **Infrastructure**: Terraform
- **Frontend**: Vanilla HTML, CSS, JavaScript

## ✨ Features

- **Order Management**: Place, track, and cancel food orders
- **Real-time Tracking**: Monitor order status updates
- **RESTful API**: Complete CRUD operations
- **Serverless**: Auto-scaling and cost-effective
- **Infrastructure as Code**: Reproducible deployments

## 📁 Project Structure
food-delivery-app/
├── terraform/
│ ├── main.tf 
│ ├── variables.tf
│ └── outputs.tf


├── app/
│ ├── app.py # Lambda function code
│ ├── requirements.txt
│ ├── template.yaml
│ └── build.sh

└── README.md

## 🚀 Quick Start

### Prerequisites
- AWS Account
- Terraform installed
- AWS CLI configured

### Deployment
cd terraform
terraform init
terraform plan
terraform apply
Local Development
bash
cd app
sam local start-api --port 8000
# Access: http://localhost:8000
🔧 API Endpoints
Method	Endpoint	Description
GET	/	Landing page
GET	/purchase	Order form
POST	/order	Create order
GET	/track/{order_id}	Track order
PUT	/order/{order_id}/cancel	Cancel order
💡 Key Features Demonstrated
Serverless Architecture: Lambda + API Gateway + DynamoDB

Infrastructure as Code: Complete Terraform setup

REST API Design: Proper HTTP methods and status codes

Error Handling: Comprehensive error management

Database Design: DynamoDB schema and queries

Local Development: SAM CLI for testing

🎯 Learning Outcomes
This project demonstrates:

AWS serverless services integration

Terraform for cloud infrastructure

Python Lambda development

DynamoDB data modeling

REST API design principles

CI/CD-ready infrastructure

📊 Project Highlights
Cost Effective: ~$1.50/month for 1000 orders

Scalable: Handles traffic spikes automatically

Maintainable: Clean code and documentation

Production Ready: Error handling and monitoring

🤝 Contributing
Feel free to fork this project and submit pull requests for any improvements.



- **Highlights skills** - Shows AWS, Terraform, serverless expertise
- **Easy to understand** - Clear architecture and features
- **Showcase-focused** - Emphasizes learning outcomes and highlights
- **Ready to use** - Just paste into your GitHub repository

It presents your project as a professional demonstration of cloud development skills without the live deployment context.
