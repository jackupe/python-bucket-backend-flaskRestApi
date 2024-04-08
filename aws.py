"""


"""
import logging
import boto3
import os
from botocore.exceptions import ClientError


class AwsHandler(object):
    user_name = "user-flask-rest-api"
    bucket_name = "bucket-flask-rest-api"
    region = "eu-north-1"

    def __init__(self):
        self.iam = boto3.client('iam')

        self.clear_acc_key()

        acc_key = self.__create_iam_user_keys()
        logging.info(acc_key)

        self.AccessKeyId = acc_key['AccessKeyId']
        self.SecretAccessKey = acc_key['SecretAccessKey']

        session = boto3.Session(aws_access_key_id=self.AccessKeyId,
                                aws_secret_access_key=self.SecretAccessKey,
                                region_name=self.region)
        self.s3client = session.client("s3")

    def clear_acc_key(self):
        for acc_key in self.__list_iam_user_keys():
            self.__delete_iam_user_keys(access_key_id=acc_key["AccessKeyId"])

    def __list_iam_user_keys(self):
        # List access keys through the pagination interface.
        paginator = self.iam.get_paginator('list_access_keys')
        responses = paginator.paginate(UserName=AwsHandler.user_name)
        user_name, access_key_id, status = ([], [], [])
        for response in responses:
            user_name = [key["UserName"] for key in response['AccessKeyMetadata']]
            access_key_id = [key["AccessKeyId"] for key in response['AccessKeyMetadata']]
            status = [key["Status"] for key in response['AccessKeyMetadata']]

        return [{"UserName": un, "AccessKeyId": aki, "Status": s} for un, aki, s in
                zip(user_name, access_key_id, status)]

    def __create_iam_user_keys(self):
        # Create an access key
        response = self.iam.create_access_key(UserName=AwsHandler.user_name)
        logging.info(response)
        return response['AccessKey']

    def __set_status_iam_user_access_key(self, access_key_id, status='Active'):
        # Update access key to be active
        self.iam.update_access_key(
            AccessKeyId=access_key_id,
            Status=status,
            UserName=AwsHandler.user_name
        )

    def __delete_iam_user_keys(self, access_key_id):
        # Create an access key
        self.iam.delete_access_key(
            AccessKeyId=access_key_id,
            UserName=AwsHandler.user_name
        )

    def create_bucket(self):
        """Create an S3 bucket in a specified region

        If a region is not specified, the bucket is created in the S3 default
        region (us-east-1).

        :param bucket_name: Bucket to create
        :param region: String region to create bucket in, e.g., 'us-west-2'
        :return: True if bucket created, else False
        """

        # Create bucket
        try:
            if AwsHandler.region is None:

                self.s3client.create_bucket(Bucket=AwsHandler.bucket_name)
            else:
                location = {'LocationConstraint': AwsHandler.region}
                self.s3client.create_bucket(Bucket=AwsHandler.bucket_name,
                                            CreateBucketConfiguration=location)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def upload_file(self, file_name, object_name=None):
        """Upload a file to an S3 bucket

        :param file_name: File to upload
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)

        try:
            response = self.s3client.upload_file(file_name, AwsHandler.bucket_name, object_name)
            logging.info(response)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def display_bucket(self):
        print('\tDisplay Amazon S3 Bucket objects/files:')
        s3_bucket = s3_resource.Bucket(bucket['Name'])
        for upl_file in s3_bucket.objects.all():
            print(f'\t-- {upl_file.key}')

    def clear_bucket(self):
        print('\tClearing Amazon S3 Bucket objects/files:')
        s3_bucket = s3_resource.Bucket(bucket['Name'])
        for upl_file in s3_bucket.objects.all():
            print(f'\t-- {upl_file.key}')
            s3_resource.Object(bucket['Name'], upl_file.key).delete()


if __name__ == '__main__':
    session = boto3.Session()
    # session = boto3.Session(profile_name=AwsHandler.user_name)
    s3_client = session.client("s3")
    s3_resource = session.resource("s3")

    response = s3_client.list_buckets()
    print("Listing Amazon S3 Buckets:")
    for bucket in response['Buckets']:
        print(f"-- {bucket['Name']}")
        print('\tListing Amazon S3 Bucket objects/files:')
        s3_bucket = s3_resource.Bucket(bucket['Name'])
        for upl_file in s3_bucket.objects.all():
            print(f'\t-- {upl_file.key}')

    #aws = AwsHandler()
    #aws.clear_acc_key()
    #aws.clear_bucket()

