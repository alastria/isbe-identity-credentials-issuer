
import requests
from requests import Request, Response
from project.settings import TOKENIZATION_SERVICE
from project.settings import (
    TOKENIZATION_ACCOUNT_MNEMONIC,
    TOKENIZATION_ACCOUNT_PATH,
    NETWORK_SERVICE_HOST,
)
from web3 import Web3
from web3.providers.rpc import HTTPProvider
from network_service_client.client import (
    Client as NetworkClient,
    Network as NetworkDTO,
    NetworksNames,
)
from django.conf import settings
from uuid import uuid4

import logging
logger = logging.getLogger('django')

web3 = None
if NETWORK_SERVICE_HOST:
    network_data: NetworkDTO = NetworkClient(
            service_host=NETWORK_SERVICE_HOST
        ).get_network_by_name(NetworksNames.AlastriaDefaultName)
    node = network_data.node["path"]
    logger.info("Alastria Node: " + node)
    web3 = Web3(HTTPProvider(node))
    web3.eth.account.enable_unaudited_hdwallet_features()

class TokenizationService():

    @staticmethod
    def sign_transaction(raw_tx, account):
        map_tx = {
            "from": account.address,
            "to": raw_tx["to"],
            "gas": raw_tx["gasLimit"]["hex"],
            "nonce": web3.eth.getTransactionCount(account.address),
            "chainId": int(raw_tx["chainId"]),
            "data": raw_tx["data"],
            "gasPrice": raw_tx["gasPrice"]["hex"],
        }
        signed_tx = web3.eth.account.sign_transaction(map_tx,  account.privateKey)
        return {"signedTx": signed_tx.rawTransaction.hex()}

    @staticmethod
    def get_nft_group(uri: str, groupid: str) -> dict:
    
        account = web3.eth.account.from_mnemonic(
            TOKENIZATION_ACCOUNT_MNEMONIC, account_path=TOKENIZATION_ACCOUNT_PATH
        )
        mint_data = {
            "to": account.address,
            "uri": uri,
            "groupid": groupid,  
        }
        mint_request: Response = requests.post(f"{TOKENIZATION_SERVICE}/api/group/nfts", data=mint_data)
        if not mint_request.ok:
            raise Exception(mint_request.reason)

        signed_request_data = TokenizationService.sign_transaction(mint_request.json()["unsignedTx"], account)

        params = {"tokenType": "group"}
        signed_request: Response = requests.post(f"{TOKENIZATION_SERVICE}/api/transactions", params=params,data=signed_request_data)
        if not signed_request.ok:
            raise Exception(signed_request.reason)
        
        result =  signed_request.json()
        logger.info("Response transactions: ")
        logger.info(result)

        response = { 
            "tokenId": result['_blockchainDetail']['data']['tokenId'],
            "transactionHash": result['_blockchainDetail']['transactionHash']
        }
        return response

        # Consular el tokenid y obtener la uri registrada
        """
        token_request: Response = requests.get(
            f"{TOKENIZATION_SERVICE}/api/nfts/{signed_request.json()['_blockchainDetail']['data']['tokenId']}"
        )
        if not token_request.ok:
            raise Exception(token_request.reason)
        logger.info("Response api/nfts: ")
        logger.info(token_request.json())
        response = {}
        response["tx_data"] = signed_request.json()["_blockchainDetail"]
        response["token_data"] = token_request.json()
        return response
        """
