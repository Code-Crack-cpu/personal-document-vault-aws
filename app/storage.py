import boto3
from flask import current_app


def _client():
    return boto3.client("s3", region_name=current_app.config["AWS_REGION"])


def upload_file(file_object, object_key, content_type):
    _client().upload_fileobj(
        file_object,
        current_app.config["S3_BUCKET_NAME"],
        object_key,
        ExtraArgs={"ContentType": content_type},
    )


def create_download_url(object_key):
    return _client().generate_presigned_url(
        "get_object",
        Params={
            "Bucket": current_app.config["S3_BUCKET_NAME"],
            "Key": object_key,
        },
        ExpiresIn=300,
    )


def delete_file(object_key):
    _client().delete_object(
        Bucket=current_app.config["S3_BUCKET_NAME"],
        Key=object_key,
    )
