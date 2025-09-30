output "api_url" {
  description = "API Gateway URL"
  value       = aws_apigatewayv2_api.food_delivery_api.api_endpoint
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.food_delivery_app.function_name
}

output "dynamodb_table_name" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.food_orders.name
}