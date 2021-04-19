import os
import boto3
from botocore.exceptions import ClientError


def get_s3_client():
    """Get AWS S3 Client."""
    aws_session = boto3.session.Session()
    s3_client = aws_session.client('s3')
    return s3_client

def get_s3_resource():
    """Get AWS S3 Client."""
    aws_session = boto3.session.Session()
    s3_client = aws_session.resource('s3')
    return s3_client


def get_all_bucket_list():
    """Enumerates all available s3 buckets for the given aws credentials (Passive Recon)."""
    client = get_s3_client()
    buckets = []
    print('Enumerating buckets...')
    try:
        response = client.list_buckets()
    except ClientError as error:
        code = error.response['Error']['Code']
        if code == 'AccessDenied':
            print('  FAILURE: MISSING AWS PERMISSIONS')
        else:
            print(code)
        return {}

    for bucket in response['Buckets']:
        buckets.append(bucket['Name'])
        print(f"Found bucket: {bucket['Name']}")
    return buckets

def enumerate_bucket(bucket):
    """Enumerate all the objects in a given bucket."""
    client = get_s3_client()
    paginator = client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket)

    print(f'Starting enumerating objects in bucket {bucket}...')
    objects = []
    try:
        for page in page_iterator:
            if 'Contents' in page:
                keys = [key['Key'] for key in page['Contents']]
                objects.extend(keys)
    except ClientError as error:
        print('  Unable to read bucket')
        code = error.response['Error']['Code']
        print(code)
    
    return objects

def download_s3_file(key, bucket):
    """Download an s3 object, given its key.
    Key is the full filename path of an object in s3
    """
    base_directory = f's3_downloads/{bucket}/'
    directory = base_directory

    key_split = key.split('/')
    offset_directory = key_split[:-1]
    filename = key_split[-1]
    if offset_directory:
        directory += '/'.join(offset_directory)
    if not os.path.exists(directory):
        os.makedirs(directory)

    s3 = get_s3_client()


    try:
        s3.download_file(bucket, key, f'{directory}/{filename}')
    except Exception as error:
        print(error)
        return False
    return True

def enumerate_and_download_all_buckets():
    """Download all objects from all buckets that the current user have access to."""
    bucket_list = get_all_bucket_list()

    for bucket in bucket_list:
        objects = enumerate_bucket(bucket)
        for key in objects:
            print(f'Downloading {key}')
            download_s3_file(key, bucket)

enumerate_and_download_all_buckets()