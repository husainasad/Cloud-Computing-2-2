output "input_s3_bucket" {
    value = aws_s3_bucket.input_bucket.arn
}

output "stage1_s3_bucket" {
    value = aws_s3_bucket.stage1_bucket.arn
}

output "output_s3_bucket" {
    value = aws_s3_bucket.output_bucket.arn
}

output "vs_lambda_function" {
    value = aws_lambda_function.vs_lambda.arn
}

output "ml_lambda_function" {
    value = aws_lambda_function.ml_lambda.arn
}