This repository contains steps and key notes to develop a serverless dsitributed video processing application using Lambda, S3, ECR, and Docker. <br>
The application consists of : <br>
* S3: To store user video uploads (input), processed video frames (stage-1), and face recognition result (output).
* Lambda: To process user videos to generate images and to process images to recognize faces.
* ECR and Docker: To containerize lambda function images and deploy the functions on AWS.

## Step 1: Create S3 Buckets
The input, stage-1, and output S3 buckets can be created by running the 'createS3.py' script. <br>

## Step 2: Create Lambda function for video splitting
The video splitting function requires the ffmpeg library. The steps to create ffmpeg layer are loosely based on [this](https://virkud-sarvesh.medium.com/building-ffmpeg-layer-for-a-lambda-function-a206f36d3edc) medium article and [this](https://aws.amazon.com/blogs/media/processing-user-generated-content-using-aws-lambda-and-ffmpeg/) aws guide. <br>

### Create FFmpeg zip
Create the ffmpeg zip using the 'install_ffmpeg.sh' script in AWS Cloudshell or any linux environment. <br>
Make the script executable using the command:
```
chmod +x install_ffmpeg.sh
```
Then execute the script using the command:
```
./install_ffmpeg.sh
```
Once script has finished execution, look for ffmpeg.zip file and download it. <br>

### Create FFmpeg layer
Create the layer by uploading the zip file from where you downloaded it (S3 or local). <br>
Add the runtime of your lambda function in compatible runtimes. <br>
Finally, add the input S3 bucket as trigger for the function. <br>

### Attach FFmpeg layer
Add the layer in the lambda function whenever you need to use the library. <br>

### Create Lambda function
The code for lambda function can be found in 'video-splitting.py'. <br>
The code also makes use of 'video-splitting_config.json' file for reading configurations. <br>
Make sure the ffmpeg layer is attached. <br>

### Attach S3 trigger
Attach the S3 event creation trigger so that the function is triggered every time object is put into S3. <br>

## Step 3: Create Lambda function for face recognition
The face recognition function makes use of pytorch libraries and facenet models. Since there are lot of libraries involved, using docker images is the ideal way. The steps to create and use docker image are loosely based on [this](https://repost.aws/knowledge-center/lambda-container-images) aws guide.

### Create Dockerfile
The Dockerfile present in the project contains the necessary code for the docker image. <br>
It is very important to understand where to install dependencies and files required by the function as the incorrectly configured image would still run locally but fail on cloud. <br>

You can check the directory structure of the function environment by using the following command: <br>
```
docker exec -t -i {container-name} /bin/bash
```

Run the above command on a different terminal while the docker container is running. <br>

### Create Lambda function
The code for lambda function can be found in 'face-recognition.py'. <br>
The code also makes use of 'face-recognition_config.json' file for reading configurations. <br>

### Build and Test locally
Build using the following command: <br>
```
docker build -t {image-name}:{version-name} .
```

Run container from the image using the following command [local testing only]: <br>
```
docker run -p 9000:8080 -e AWS_ACCESS_KEY_ID={your aws key id} -e AWS_SECRET_ACCESS_KEY={your aws secrey key} {image-name}:{version-name}
```
<b> Note: The lambda function needs credentials to create AWS clients. While credentials are not required in AWS environment, you will have to pass them when you test the application locally. <br> </b>

<b> Note: When testing locally, you will need to create AWS clients directly (without creating session client).You can add the code to create session client once you are done testing. <br> </b>

Test the function using the following command:
```
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
```

<b> Note: For initial testing, instead of event-based trigger, processed all objects present in the bucket (for convenience). Once everything works correctly on AWS environment, update code to process only event objects. <br> </b>

### Upload to ECR
Once you are satisfied with testing the application locally, it is time to deploy the application on AWS environment. For this, we will make use of ECR. <br>

First, create your AWS ECR registry. <br>

<b> Note: You must create private registry as AWS currently only supports creation of Lambda functions from private ECR registries. <br> </b>

Once ECR registry is created, the commands to push image to ECR are present in the ECR registry under the 'view push commands' section. <br>

<b> Note: For Windows users, there might be an issue with authenticating Docker CLI to AWS ECR registry causing the following error message: <br>
"docker login: error storing credentials `The stub received bad data.`"

To resolve this issue, I followed [this](https://stackoverflow.com/questions/60807697/docker-login-error-storing-credentials-the-stub-received-bad-data) stackoverflow post. The steps are: <br>
* Remove C:\Program Files\Docker\Docker\resources\bin\docker-credential-wincred.exe
* Remove "credsStore": "desktop" in C:\Users\XXXX\.docker\config.json file
</b>

### Create Lambda function using ECR
Once the image is successfully psuhed to ECr repository, you can create the lambda function by selecting 'Container image' option and using the Image ECR URI. <br>

<b> Note: You cannot view or modify the lamda function creating using the 'Container Image' method. <br> </b>

## Step 4: Test with Workload Generator
Workload Generator simulates a client side and uploads files to the input bucket. <br>

Command to upload videos:
```
python ./Resources/workload_generator/workload_generator_p2.py --access_key {your access key} --secret_key {your secret key} --asu_id 1225380117 --testcase_folder ./Resources/dataset/test_case_2/
```

More information on workload generator can be found in the associated readme.

## Step 5: Test with grading script
The grading script validates the result by matching input and output objects. <br>
The execution time of the functions can be improved by increasing the memory and ephemeral memory. <br>
Command to test:
```
python grader_script_p2_v2.py --access_key {your access key} --secret_key {your secret key} --asu_id 1225380117
```
More information on grading script can be found in the associated readme.

## Architecture Choices
The project can be developed in multiple ways. This section will discuss how to work with two major ways. <br>

The first way (more preferred) is event-driven and the other is lambda-to-lambda invocation. <br>
Both ways have been implemented and tested on the project. <br>

### Event-Driven Architecture:
In this approach, each lambda function is triggered by putting objects in S3. <br>
Therefore, you will have to add respective triggers in the lambda functions. <br>
This approach ensures low coupling between the lambda functions. <br>

### Lambda-to-Lambda Invocation:
In this approach, the face-recognition function is triggered by video-splitting function. <br>
Therefore, you will only need to add trigger for the first function. The video-splitting function will invoke the face-recognition function with specific parameters once its own process is complete. The face-recognition function will respond to the invocation and use the specified parameters for processing. <br>
Additionally, you will have to add the required invoking permission to the lambda-role for invocation. <br>
This approach tightly couples the lambda functions which is not preferred. <br>