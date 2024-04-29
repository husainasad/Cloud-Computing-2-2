This readmefile provides a general guide on using CloudFormation templates to create Lambda functions. <br>
It goes without saying that the AWS Documentation is the best guide for using AWS resources. <br>
This guide loosely follows [this](https://www.techtarget.com/searchcloudcomputing/tutorial/How-to-Create-an-AWS-Lambda-Function-with-CloudFormation) blog article and [this](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html) AWS documentation. <br>

There are different ways to create Lambda functions using CloudFormation templates such as:
* Including the function code within the template (not discussed in this guide)
* Storing the function zip file in S3 bucket and then adding to the template
* Creating docker image of the function, uploading to ECR and adding image uri to the template

## Using Function Zip File
* Write the lambda function
* Zip the function and upload the zip file to S3
* Create the yaml file for lambda function (explained below)
* Upload the template to CF stack

### CloudFormation Template for Lambda function
Refer to 'lambdafunc.yaml' for reference. <br>
There are two mandatory fields in the template which are:
* Code: Specifies the location of the code
* Role: Specifies the function's execution role

<b> Note: Runtime is also an important property that should be specified. <br> </b>

Apart from the above properties, you can specify other properties for more control over the function such as defining memory storage, ephemeral storage, timeout, etc. <br>

## Testing
After the template is uploaded to CloudFormation stack, the entire process of creating and configuring the function is automated.<br>
Once the stack execution is successful, head over to lambda console where the newly created function is available. <br>
Test the function to make sure the code runs correctly.

## Using DockerFile and ECR
* Create the lambda function, Dockerfile, requirements, and build the image
* Push the image to ECR
* Create the yaml file for lambda function
* Upload the template to CF stack

<b> Note: The YAML for using Images differs from using Zip files in terms of property attributes. When using image uri, you must remove 'handler' and 'Runtime' properties, and modify 'PackageType' to be 'Image' <br> <b>