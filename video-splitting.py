import os
import boto3
import json
import subprocess
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

config_path = 'video-splitting_config.json'

with open(config_path) as f:
    config = json.load(f)

region = config.get("AWS_REGION")
input_bucket = config.get("INPUT_BUCKET")
output_bucket = config.get("STAGE1_BUCKET")
timeout = config.get("URL_TIMEOUT")
temp_dir = config.get("TEMP_DIR")
lambda_func = config.get("LAMBDA_TO_INVOKE")

session = boto3.Session(region_name=region)
s3_client = session.client('s3')
lambda_client = session.client('lambda')

# lambda-to-lambda invocation
def invoke_face_recognition(image_file_name):
    try:
        payload_content = {
            'bucket_name':output_bucket,
            'image_file_name':image_file_name
        }

        response = lambda_client.invoke(
            FunctionName = lambda_func,
            InvocationType = 'Event',
            Payload = json.dumps(payload_content)
        )
    except Exception as e:
        print(f"Error invoking lambda invocation : {str(e)}")
        
def video_splitting_cmdline(video_url, image_name):
    outdir = os.path.join(temp_dir, image_name)
    os.makedirs(outdir, exist_ok=True)
    
    split_cmd = f'ffmpeg -i "{video_url}" -vframes 1 "{outdir}/{image_name}.jpg" -y'
    try:
        subprocess.check_call(split_cmd, shell=True)
        return outdir
    except subprocess.CalledProcessError as e:
        print(e.returncode)
        print(e.output)
        return None
    
def generate_presigned_url(key):
    try:
        url = s3_client.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': input_bucket, 'Key': key}, ExpiresIn=timeout)
        return url
    except Exception as e:
        print(f"Error generating presigned url : {str(e)}")

def upload_image_to_s3(output_dir):
    try:
        file_path = os.path.join(output_dir, os.listdir(output_dir)[0])
        s3_key = os.path.basename(file_path)
        s3_client.put_object(Bucket=output_bucket, Key=s3_key, Body=open(file_path, 'rb'))
        print(f"Uploaded {file_path} to s3://{output_bucket}/{s3_key}")
    except Exception as e:
        print(f"Error uploading frames to S3: {str(e)}")
        
def process_video(video_key):
    try:
        video_url = generate_presigned_url(video_key)
        img_name = os.path.splitext(os.path.basename(video_key))[0]
        output_dir = video_splitting_cmdline(video_url, img_name)
        if output_dir:
            upload_image_to_s3(output_dir)
            img_file_name = img_name+'.jpg'
            invoke_face_recognition(img_file_name)
        print(f"Video '{video_key}' processed successfully")
    except Exception as e:
        print(f"Error processing video '{video_key}': {str(e)}")

def process_objects():
    try:
        response = s3_client.list_objects_v2(Bucket=input_bucket)
        for obj in response.get('Contents', []):
            video_key = obj['Key']
            process_video(video_key)
    except Exception as e:
        print("Unable to get bucket objects")

def handler(event, context):
    try:
        # process_objects()
        video_key = event['Records'][0]['s3']['object']['key']
        process_video(video_key)
        return {
            'statusCode': 200,
            'body': 'Function executed successfully'
        }
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        return {
            'statusCode': 500,
            'body': 'Error processing video'
        }