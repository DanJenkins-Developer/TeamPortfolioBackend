
import boto3
from botocore.config import Config

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# AWS Connection
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")


# Bucket details
bucket_name = 'team-profile-pictures'
region_name = 'us-east-2'
endpoint_url = 'https://s3.us-east-2.amazonaws.com'


access_point_url = 'https://accesspoint1-dso6gt5myao37djcz38u3kksnyrbguse2a-s3alias.s3-accesspoint.us-east-2.amazonaws.com'


# Client configuration
s3_config = Config(region_name=region_name)

# Initialize a session using the config
session = boto3.session.Session()

s3_client = session.client(
    service_name='s3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    endpoint_url=access_point_url,  # If using an S3 Access Point
    config=s3_config
)
