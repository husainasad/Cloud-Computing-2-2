import json

def handler(event, context):
    try:
        print("Received event: " + json.dumps(event))
        return {
            'statusCode': 200,
            'body': 'Function executed successfully'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': 'Error executing lambda'
        }