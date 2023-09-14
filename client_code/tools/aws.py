import anvil.js
from anvil.js.window import AWS  # Assuming AWS is the global variable that holds the AWS SDK bundle
import time


class AmazonAccess:
    def __init__(self, region, identity_pool_id):
        self.region = region
        self.identity_pool_id = identity_pool_id
        self.cognito_client = AWS.CognitoIdentity.CognitoIdentityClient({'region': self.region})
        self.credentials = AWS.fromCognitoIdentityPool.fromCognitoIdentityPool({
            'client': self.cognito_client,
            'clientConfig': {'region': self.region},
            'identityPoolId': self.identity_pool_id,
        })()
        print(f"Initialized Cognito Credentials: {self.credentials.accessKeyId}, {self.credentials.secretAccessKey}")

        def resolve(error, data):
            if not error:
                # Do something with the credentials
                self.cognito_id = data['IdentityId']
                print(f"Received Cognito ID: {self.cognito_id}")
            else:
                print(f"Error receiving Cognito ID: {error}")

        # self.cognito_client = anvil.js.new(AWS.CognitoIdentity.CognitoIdentityClient, {'region': self.region})
        # print(f"Initialized Cognito Client: {self.cognito_client}")
        # command = AWS.CognitoIdentity.GetIdCommand({
        #     'IdentityPoolId': self.identity_pool_id
        # })
        # send_result = self.cognito_client.send(command, resolve)
        # time.sleep(5)
        # print(f"Sent GetIdCommand: {command}, result: {send_result}")
        # print(f"Received Cognito ID: {self.cognito_id}")

    # def get_credentials(self):
    #     command = AWS.CognitoIdentity.GetIdCommand({
    #         'IdentityPoolId': self.identity_pool_id
    #     })
    #
    #     # Assuming you have a callback to handle the credentials
    #     def resolve(error, data):
    #         if not error:
    #             # Do something with the credentials
    #             self.cognito_id = data['IdentityId']
    #             print(f"Received Cognito ID: {self.cognito_id}")
    #         else:
    #             print(f"Error receiving Cognito ID: {error}")
    #
    #     self.cognito_client.send(command, resolve)


class AmazonS3:
    def __init__(self, region, credentials, bucket_name):
        self.region = region
        self.bucket_name = bucket_name
        # self.s3_client = AWS.S3Client.new({'region': self.region})
        self.s3_client = anvil.js.new(
            AWS.S3Client.S3Client,
            {
                'region': self.region,
                'credentials': credentials,
            },
        )
        print(f"Initialized S3 Client: {self.s3_client}")

        command = AWS.S3Client.ListObjectsCommand({'Bucket': self.bucket_name})
        print(f"Sending ListObjectsCommand: {command}")
        result = self.s3_client.send(command)
        # print(f"Sent ListBucketsCommand: {command}, {result}")
        time.sleep(3)
        print(f"Result? {result}")

    def resolve(self, error, data):
        if not error:
            print('data: ', data)
        else:
            print('error:', error)

    def upload_file(self, file_body, file_name):
        command = AWS.S3Client.PutObjectCommand({
            'Bucket': self.bucket_name,
            'Key': file_name,
            'Body': file_body
        })

        # Assuming you have a callback to handle the upload result
        def resolve(error, data):
            if not error:
                print('Upload successful')
            else:
                print(f'Upload failed: {error}')

        self.s3_client.send(command, resolve)


# Initial Python code for the home page to instantiate AWS objects
def initialize_aws():
    aws_access = AmazonAccess('us-east-1', 'us-east-1:759bd02e-0d9f-49ff-8270-1b94a37af8a2')
    # aws_access.get_credentials()

    aws_s3 = AmazonS3('us-east-1', aws_access.credentials, 'practice-manager-storage')
    print(f"Successfully initialized AWS Access and S3 objects.")
