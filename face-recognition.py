import os
import boto3
import cv2
import json
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

config_path = 'lambda_config.json'
data_path = 'data.pt'
os.environ['TORCH_HOME'] = '/tmp/'

with open(config_path, 'r') as f:
    config = json.load(f)

saved_data = torch.load(data_path)

region = config.get("AWS_REGION")
input_bucket = config.get("STAGE1_BUCKET")
output_bucket = config.get("OUTPUT_BUCKET")

session = boto3.Session(region_name=region)
s3_client = session.client('s3')

mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20)
resnet = InceptionResnetV1(pretrained='vggface2').eval()

def read_image(img_key):
	try:
		img_dir = os.path.join('/tmp', img_key)
		s3_client.download_file(input_bucket, img_key, img_dir)
		return cv2.imread(img_dir, cv2.IMREAD_COLOR), img_dir
	except Exception as e:
		logger.error("Unable to download and read image: %s", e)
		return None


def recognize_image(face):
	try:
		emb = resnet(face.unsqueeze(0)).detach()
		embedding_list = saved_data[0]
		name_list = saved_data[1]
		dist_list = []
		for idx, emb_db in enumerate(embedding_list):
			dist = torch.dist(emb, emb_db).item()
			dist_list.append(dist)
		idx_min = dist_list.index(min(dist_list))
		return name_list[idx_min]
	except Exception as e:
		logger.error("Unable to recognize image: %s", e)
		return None

def upload_to_output(result, filename, bucket_name=output_bucket):
	try:
		result_text = result.encode('utf-8')
		result_key = f"{filename}.txt"
		s3_client.put_object(Bucket=bucket_name, Key=result_key, Body=result_text)
		logger.info(f"Result file '{result_key}' uploaded to '{bucket_name}'")
	except Exception as e:
		logger.error("Unable to upload image: %s", e)

def process_image(img_key):
	try:
		img, img_dir = read_image(img_key)
		if img is None:
			return
		# boxes, _ = mtcnn.detect(img)
  
		img_name = os.path.splitext(img_key)[0]
		img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
		face, prob = mtcnn(img, return_prob=True, save_path=None)

		if face != None:
			name = recognize_image(face)
			upload_to_output(name, img_name)
			logger.info(f"{img_key}' processed successfully")
		else:
			logger.info(f"No face is detected in {img_key}")
	except Exception as e:
		logger.error("Unable to process image: %s", e)
	finally:
		if os.path.exists(img_dir):
			os.remove(img_dir)

def process_request():
	try:
		response = s3_client.list_objects_v2(Bucket=input_bucket)
		for obj in response.get('Contents', []):
			# print(obj['Key'])
			process_image(obj['Key'])
	except Exception as e:
		logger.error("Unable to get bucket images: %s", e)

def handler(event, context):
	try:
		# process_request()
		image_key = event['Records'][0]['s3']['object']['key']
		process_image(image_key) 
		return {
			'statusCode': 200,
			'body': 'Lambda function executed successfully'
		}
	except Exception as e:
		logger.error(e)
		return {
			'statusCode': 500,
			'body': 'Lambda function unable to execute'
		}	