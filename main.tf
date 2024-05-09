provider "aws" {
    region = var.region
}

resource "aws_s3_bucket" "input_bucket" {
    bucket = var.input-bucket
}

resource "aws_s3_bucket" "stage1_bucket" {
    bucket = var.stage1-bucket
}

resource "aws_s3_bucket" "output_bucket" {
    bucket = var.output-bucket
}

resource "aws_lambda_function" "vs_lambda" {
    function_name = var.vs-lambda
    role = var.lambda-role
    package_type = "Image"
    image_uri = var.vs-uri
    memory_size = var.lambda-memory
    ephemeral_storage {
        size = var.lambda-ephemeral
    }
    timeout = var.lambda-timeout
}

resource "aws_lambda_function" "ml_lambda" {
    function_name = var.ml-lambda
    role = var.lambda-role
    package_type = "Image"
    image_uri = var.ml-uri
    memory_size = var.lambda-memory
    ephemeral_storage {
        size = var.lambda-ephemeral
    }
    timeout = var.lambda-timeout
}

resource "aws_lambda_permission" "input_bucket_lambda_permission" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.vs_lambda.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.input_bucket.arn
}

resource "aws_lambda_permission" "strage1_bucket_lambda_permission" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ml_lambda.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.stage1_bucket.arn
}

resource "aws_s3_bucket_notification" "input_bucket_trigger" {
    bucket = var.input-bucket

    lambda_function {
        lambda_function_arn = aws_lambda_function.vs_lambda.arn
        events = ["s3:ObjectCreated:*"]
    }
}

resource "aws_s3_bucket_notification" "stage1_bucket_trigger" {
    bucket = var.stage1-bucket

    lambda_function {
        lambda_function_arn = aws_lambda_function.ml_lambda.arn
        events = ["s3:ObjectCreated:*"]
    }
}