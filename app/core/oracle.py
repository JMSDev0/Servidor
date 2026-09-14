import os
import oci


def get_oracle_client():
    auth_mode = os.getenv("OCI_AUTH_MODE", "local")
    region = os.getenv("OCI_REGION", "sa-saopaulo-1")

    if auth_mode == "instance":
        # Produção: Oracle Cloud VM
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()

        config = {
            "region": region
        }

        client = oci.object_storage.ObjectStorageClient(
            config,
            signer=signer
        )

    else:
        # Desenvolvimento: máquina local
        config = oci.config.from_file()

        client = oci.object_storage.ObjectStorageClient(
            config
        )

    return client