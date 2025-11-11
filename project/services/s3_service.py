import logging
import os

import boto3
from django.conf import settings


class S3Service:
    def __init__(self):
        self.session = self.init_session()

    def init_session(self):
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
        )

        return session.client("s3")

    def upload_file_to_s3(self, file_path, file_name):
        try:
            self.session.upload_file(
                Filename=file_path,
                Bucket=settings.AWS_BUCKET,
                Key=file_name,
            )
            if self.exists_s3_file(file_name):
                s3 = boto3.resource(
                    "s3",
                    aws_access_key_id=settings.AWS_ACCESS_KEY,
                    aws_secret_access_key=settings.AWS_SECRET_KEY,
                )
                object_acl = s3.ObjectAcl(settings.AWS_BUCKET, file_name)
                response = object_acl.put(ACL="public-read")
                self.delete_local_file(file_path)
                return self.get_file_link(file_name)
            else:
                return False
        except Exception as e:
            logging.info(e)
            return

    def exists_s3_file(self, file_key):
        try:
            self.session.head_object(Bucket=settings.AWS_BUCKET, Key=file_key)
            return True
        except Exception as e:
            logging.info(e)
        return False

    @staticmethod
    def delete_file(file_url):
        file_key = S3Service.get_file_key(file_url)
        logging.info(f"\n ==> DELETE in S3. URL: {file_url} | KEY: {file_key}\n")
        s3 = boto3.resource(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
        )
        s3.Object(settings.AWS_BUCKET, file_key).delete()

    def delete_local_file(self, file_path):
        if os.path.exists(f"{file_path}"):
            os.remove(f"{file_path}")
            return True
        return False

    @staticmethod
    def get_file_key(file_url: str):
        if "amazonaws.com" not in file_url:
            return file_url
        return file_url.split("amazonaws.com/")[1]

    def get_file_link(self, file_name):
        return f"https://{settings.AWS_BUCKET}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file_name}"
