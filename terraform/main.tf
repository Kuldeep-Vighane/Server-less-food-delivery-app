terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# DynamoDB Table
resource "aws_dynamodb_table" "food_orders" {
  name           = "FoodOrders"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "order_id"

  attribute {
    name = "order_id"
    type = "S"
  }

  tags = {
    Name = "FoodOrders"
  }
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "food_delivery_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda
resource "aws_iam_role_policy" "lambda_policy" {
  name = "food_delivery_lambda_policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Scan",
          "dynamodb:Query"
        ]
        Resource = aws_dynamodb_table.food_orders.arn
      }
    ]
  })
}

# Create ZIP package for Lambda
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "../app"
  output_path = "../app/lambda_function.zip"
  
  depends_on = [null_resource.build_dependencies]
}

# Build dependencies before creating ZIP
resource "null_resource" "build_dependencies" {
  triggers = {
    always_run = timestamp()
  }
  
  provisioner "local-exec" {
    command = "cd ../app && chmod +x build.sh && ./build.sh"
  }
}

# Lambda Function
resource "aws_lambda_function" "food_delivery_app" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "food-delivery-app"
  role            = aws_iam_role.lambda_role.arn
  handler         = "app.handler"
  runtime         = "python3.9"
  timeout         = 30
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.food_orders.name
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_policy,
    data.archive_file.lambda_zip
  ]
}

# API Gateway
resource "aws_apigatewayv2_api" "food_delivery_api" {
  name          = "food-delivery-api"
  protocol_type = "HTTP"
}

# Lambda Integration
resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.food_delivery_api.id
  integration_type = "AWS_PROXY"

  integration_method = "POST"
  integration_uri    = aws_lambda_function.food_delivery_app.invoke_arn
}

# Routes
resource "aws_apigatewayv2_route" "root" {
  api_id    = aws_apigatewayv2_api.food_delivery_api.id
  route_key = "GET /"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_route" "purchase" {
  api_id    = aws_apigatewayv2_api.food_delivery_api.id
  route_key = "GET /purchase"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_route" "create_order" {
  api_id    = aws_apigatewayv2_api.food_delivery_api.id
  route_key = "POST /order"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_route" "track_order" {
  api_id    = aws_apigatewayv2_api.food_delivery_api.id
  route_key = "GET /track/{order_id}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_route" "cancel_order" {
  api_id    = aws_apigatewayv2_api.food_delivery_api.id
  route_key = "PUT /order/{order_id}/cancel"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_route" "default" {
  api_id    = aws_apigatewayv2_api.food_delivery_api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# Stage
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.food_delivery_api.id
  name        = "$default"
  auto_deploy = true
}

# Lambda Permission
resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.food_delivery_app.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.food_delivery_api.execution_arn}/*/*"
}