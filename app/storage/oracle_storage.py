from datetime import datetime, timedelta
import uuid
from pathlib import Path

import oci

from app.storage.storage import Storage
from app.core.oracle import get_oracle_client


class OracleStorage(Storage):

    def __init__(self):
        self.client = get_oracle_client()

    def create_upload_url(self, filename):
        namespace = self.client.get_namespace().data
        bucket_name = "acmoveis-bucket"

        extension = Path(filename).suffix.lower()

        allowed_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        }

        if extension not in allowed_extensions:
            raise ValueError(
                f"Formato de imagem não permitido: {extension}"
            )

        object_name = f"produtos/{uuid.uuid4()}{extension}"

        expiration = datetime.utcnow() + timedelta(minutes=10)

        details = oci.object_storage.models.CreatePreauthenticatedRequestDetails(
            name=f"upload-{uuid.uuid4()}",
            access_type="ObjectWrite",
            object_name=object_name,
            time_expires=expiration,
        )

        response = self.client.create_preauthenticated_request(
            namespace_name=namespace,
            bucket_name=bucket_name,
            create_preauthenticated_request_details=details,
        )

        access_uri = response.data.access_uri

        region = self.client.base_client.config["region"]

        upload_url = (
            f"https://objectstorage.{region}.oraclecloud.com"
            f"{access_uri}"
        )

        return {
            "upload_url": upload_url,
            "object_key": object_name,
        }


    def create_read_url(self, object_name):
        namespace = self.client.get_namespace().data
        bucket_name = "acmoveis-bucket"

        expiration = datetime.utcnow() + timedelta(minutes=10)

        details = oci.object_storage.models.CreatePreauthenticatedRequestDetails(
            name=f"read-{uuid.uuid4()}",
            access_type="ObjectRead",
            object_name=object_name,
            time_expires=expiration,
        )

        response = self.client.create_preauthenticated_request(
            namespace_name=namespace,
            bucket_name=bucket_name,
            create_preauthenticated_request_details=details,
        )

        access_uri = response.data.access_uri
        region = self.client.base_client.config["region"]

        image_url = (
            f"https://objectstorage.{region}.oraclecloud.com"
            f"{access_uri}"
        )

        return image_url