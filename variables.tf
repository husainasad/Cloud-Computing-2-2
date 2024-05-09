variable "region" {
    default = "us-east-1"
}

variable "input-bucket" {
    default = "1225380117-input"
}

variable "stage1-bucket" {
    default = "1225380117-stage-1"
}

variable "output-bucket" {
    default = "1225380117-output"
}

variable "vs-lambda" {
    default = "video-splitting"
}

variable "vs-uri" {
    default = "223420481310.dkr.ecr.us-east-1.amazonaws.com/video-splitting-image:v1"
}

variable "ml-lambda" {
    default = "face-recognition"
}

variable "ml-uri" {
    default = "223420481310.dkr.ecr.us-east-1.amazonaws.com/face-recognizer-image:v4"
}

variable "lambda-role" {
    default = "arn:aws:iam::223420481310:role/service-role/video-splitting-role-6fis1y1e"
}

variable "lambda-memory" {
    default = 2048
}

variable "lambda-ephemeral" {
    default = 2048
}

variable "lambda-timeout" {
    default = 600
}