import os
import tempfile
import subprocess
import boto3
from botocore.exceptions import ClientError
from dateutil import parser
from dotenv import load_dotenv

from utils.sockets import (
    send_info_to_user
)

load_dotenv()

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

S3_BUCKET = os.getenv('S3_BUCKET_NAME')


def upload_file_to_s3(file_path, bucket, object_name):
    try:
        s3_client.upload_file(
            Filename=file_path,
            Bucket=bucket,
            Key=object_name,
            ExtraArgs={'ContentType': 'video/mp4'}
        )
        print(f"Uploaded {file_path} to s3://{bucket}/{object_name} with Content-Type: video/mp4")
        return True
    except ClientError as e:
        print(f"Error uploading to S3: {e}")
        return False


def upload_final_output_to_s3(user_id, socketio, local_time_str, video_name_prefix="final_output_"):
    final_output_path = f'static/final_output/user_{user_id}/final_output.mp4'

    if not os.path.exists(final_output_path):
        print(f"Final output video not found at {final_output_path}")
        send_info_to_user(socketio, user_id, "Final output video not found for upload.")
        return False

    if not local_time_str:
        print("No local_time_str provided.")
        send_info_to_user(socketio, user_id, "Local time not provided, upload aborted.")
        return False

    try:
        local_time = parser.isoparse(local_time_str)
    except Exception as e:
        print("Error parsing local time string:", e)
        send_info_to_user(socketio, user_id, "Invalid local time format.")
        return False

    timestamp = local_time.strftime("%Y%m%d_%H%M%S")
    s3_object_name = f"user_{user_id}/{video_name_prefix}_{timestamp}.mp4"

    upload_success = upload_file_to_s3(final_output_path, S3_BUCKET, s3_object_name)
    if upload_success:
        send_info_to_user(socketio, user_id, f"Video uploaded to user storage as {s3_object_name}.")
        return True
    else:
        send_info_to_user(socketio, user_id, "Failed to upload video to user storage.")
        return False


def list_user_videos_sorted_by_date(user_id):
    prefix = f"user_{user_id}/"
    S3_REGION = os.getenv("AWS_REGION")

    video_data = []

    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix)

    for page in pages:
        for obj in page.get('Contents', []):
            key = obj['Key']
            last_modified = obj['LastModified']

            full_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{key}"

            video_data.append({
                'url': full_url,
                'last_modified': last_modified
            })

    video_data.sort(key=lambda x: x['last_modified'], reverse=True)

    return [
        {
            'url': video['url'],
            'last_modified': video['last_modified'].isoformat()
        }
        for video in video_data
    ]


def process_video_on_s3(s3_key):
    bucket = S3_BUCKET
    s3 = s3_client

    fixed_key = s3_key.replace('.mp4', '_download.mp4')
    try:
        s3.head_object(Bucket=bucket, Key=fixed_key)
        print(f"{fixed_key} already exists, skipping processing.")
        return fixed_key
    except ClientError as e:
        if e.response['Error']['Code'] != "404":
            raise

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.mp4")
        output_path = os.path.join(tmpdir, "output.mp4")

        s3.download_file(bucket, s3_key, input_path)
        cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-c:v', 'libx264', '-c:a', 'aac', '-movflags', 'faststart', output_path
        ]
        subprocess.run(cmd, check=True)

        s3.upload_file(
            output_path, bucket, s3_key,
            ExtraArgs={'ContentType': 'video/mp4', 'Metadata': {'processed': 'true'}}
        )
        print(f"Processed and uploaded {fixed_key}")

    return fixed_key


def delete_video_from_s3(s3_key):
    try:
        s3_client.delete_object(Bucket=S3_BUCKET, Key=s3_key)
        print(f"Deleted {s3_key} from S3")
        return True
    except ClientError as e:
        print(f"Failed to delete {s3_key} from S3: {e}")
        return False
