
import json
import os
from project.settings import CERTIFICATIONS_SERVICE_PATH, IPFS_GATEWAY
import requests

import logging
logger = logging.getLogger('django')


class IPFSService:

    def upload_file(certification_file_path) -> str:
        if not os.path.exists(certification_file_path):
            raise Exception(f"File does not exists: {certification_file_path}")

        split = certification_file_path.split("/")
        filename = split[-1]

        files = [("file", (filename, open(certification_file_path, "rb")))]

        try:
            logger.info("CERTIFICATIONS_SERVICE_PATH : " + CERTIFICATIONS_SERVICE_PATH)
            response = requests.request("POST", CERTIFICATIONS_SERVICE_PATH + "/ipfs"  , headers={}, data={}, files=files)
            logger.info("IPFS response:")
            logger.info(response)
        except Exception as e:
            logger.error(e)
            raise Exception(e)

        if response.status_code == 200:
            content = json.loads(response.content.decode("utf-8"))
            return IPFS_GATEWAY + content["IpfsHash"]

        return None

    def unpin_file(ipfs_hash) -> dict:
        if not (ipfs_hash):
            raise Exception("Ipfs cid does not find")
        ipfs_hash = str(ipfs_hash.replace(IPFS_GATEWAY , ""))
        url = f"{CERTIFICATIONS_SERVICE_PATH}/ipfs/{ipfs_hash}"
        print(f" - unpin_file delete url ipfs: {url}")
        try:
            response = requests.request("DELETE", url, headers={}, data={})
        except Exception as e:
            raise Exception(e)

        logger.info(" - unpin_file response: ")
        logger.info(response)
        if response.status_code == 200:
            logger.info(" - unpin_file response: ")
            logger.info(json.loads(response.content.decode("utf-8")))
            content = json.loads(response.content.decode("utf-8"))
            return {"status_code": response.status_code, "content": content}

        return {"status_code": response.status_code}
