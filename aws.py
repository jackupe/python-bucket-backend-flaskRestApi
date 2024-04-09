"""

Class to handle interactions ith AWS account/bucket etc

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
        """
        Initialize base aws objects, if there is any error then functionality is skipped.

        """
        try:
            self.iam_client = boto3.client('iam')

            self.clear_acc_key()

            acc_key = self.__create_iam_user_keys()
            if acc_key is None:
                raise ClientError({"Error": {"Code": "ParameterNotFound",
                                             "Message": "Access Key was not created"}},
                                  'create_iam_user_keys')

            logging.info(acc_key)

            self.AccessKeyId = acc_key['AccessKeyId']
            self.SecretAccessKey = acc_key['SecretAccessKey']

            session = boto3.Session(aws_access_key_id=self.AccessKeyId,
                                    aws_secret_access_key=self.SecretAccessKey,
                                    region_name=self.region)
            self.s3client = session.client("s3")
            self.s3_resource = session.resource("s3")
        except ClientError as e:
            logging.warning("Problem with AWS backup backend happened. %s" % e)
            self.iam_client = None
            self.s3client = None
            self.s3_resource = None
            self.AccessKeyId = None
            self.SecretAccessKey = None

    def clear_acc_key(self):
        """
        Remove all secret keys

        Returns: True if ias user access key removed, else False

        """
        for acc_key in self.__list_iam_user_keys():
            self.__delete_iam_user_keys(access_key_id=acc_key["AccessKeyId"])

    def __list_iam_user_keys(self):
        """
        List access keys through the pagination interface.

        Returns: All IAM user access keys, else empty List

        """

        if self.iam_client:
            try:
                paginator = self.iam_client.get_paginator('list_access_keys')
                responses = paginator.paginate(UserName=AwsHandler.user_name)
                user_name, access_key_id, status = ([], [], [])
                for response in responses:
                    user_name = [key["UserName"] for key in response['AccessKeyMetadata']]
                    access_key_id = [key["AccessKeyId"] for key in response['AccessKeyMetadata']]
                    status = [key["Status"] for key in response['AccessKeyMetadata']]

                return [{"UserName": un, "AccessKeyId": aki, "Status": s} for un, aki, s in
                        zip(user_name, access_key_id, status)]
            except ClientError as e:
                logging.error(e)
                return []
        else:
            return []

    def __create_iam_user_keys(self):
        """
        Create an access key and return it, otherwise None

        Returns: New access key, else None

        """
        if self.iam_client:
            try:
                response = self.iam_client.create_access_key(UserName=AwsHandler.user_name)
                return response['AccessKey']
            except ClientError as e:
                logging.error(e)
                return None
        else:
            return None

    def __set_status_iam_user_access_key(self, access_key_id, status='Active'):
        """
            Update access key to defined state
        Args:
            access_key_id: access key id
            status: new status

        Returns: True if acces key status updated, else False
        """

        if self.iam_client:
            try:
                self.iam_client.update_access_key(
                    AccessKeyId=access_key_id,
                    Status=status,
                    UserName=AwsHandler.user_name
                )
            except ClientError as e:
                logging.error(e)
                return False
            return True

    def __delete_iam_user_keys(self, access_key_id):
        """
        Delete specified access key

        Args:
            access_key_id: key id to remove

        Returns: True if iam user key deleted, else False

        """

        if self.iam_client:
            try:
                self.iam_client.delete_access_key(
                    AccessKeyId=access_key_id,
                    UserName=AwsHandler.user_name
                )
                return True
            except ClientError as e:
                logging.error(e)
                return False
        else:
            return False

    def create_bucket(self):
        """Create an S3 bucket in a specified region

        If a region is not specified, the bucket is created in the S3 default
        region (us-east-1).

        Returns: True if bucket created, else False
        """

        if self.s3client:
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
        else:
            return False

    def upload_file(self, file_name, object_name=None):
        """Upload a file to an S3 bucket

        Args:
            file_name: File to upload
            object_name: S3 object name. If not specified then file_name is used
        Returns: True if bucket created, else False
        """

        if self.s3client:
            if object_name is None:
                object_name = os.path.basename(file_name)

            try:
                response = self.s3client.upload_file(file_name, AwsHandler.bucket_name, object_name)
                logging.info(response)
            except ClientError as e:
                logging.error(e)
                return False

            return True
        else:
            return False

    def display_bucket(self):
        """
        Display whole bucket objects.

        Returns: True if bucket created, else False

        """
        if self.s3_resource:
            print('\tDisplay Amazon S3 Bucket objects/files:')
            try:
                s3_bucket = self.s3_resource.Bucket(bucket['Name'])
                for upl_file in s3_bucket.objects.all():
                    print(f'\t-- {upl_file.key}')
            except ClientError as e:
                logging.error(e)
                return False

            return True
        else:
            print('\tNo Aws resource - nothing to do')
            return False

    def clear_bucket(self):
        """
        Get whole bucket objects and clear them.

        Returns: True if bucket cleared, else False

        """
        if self.s3_resource:
            print('\tClearing Amazon S3 Bucket objects/files:')
            try:
                s3_bucket = self.s3_resource.Bucket(bucket['Name'])
                for upl_file in s3_bucket.objects.all():
                    print(f'\t-- {upl_file.key}')
                    self.s3_resource.Object(bucket['Name'], upl_file.key).delete()
            except ClientError as e:
                logging.error(e)
                return False

            return True
        else:
            print('\tNo Aws resource - nothing to do')
            return False


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

    # aws = AwsHandler()
    # aws.clear_acc_key()
    # aws.clear_bucket()
