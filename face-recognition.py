from boto3 import client as boto3_client

def handler(event, context):
	return {
		'statusCode': 200,
		'body': 'Lambda function executed'
	}