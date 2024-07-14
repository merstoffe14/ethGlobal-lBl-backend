import logging
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from database.database import DbUtils
from models.fastapi_models import Label, Dataset
from dataProcessing import DataProcessor
import os
import random

dbUtils = DbUtils()
dataPorcessor = DataProcessor()

router = APIRouter()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

OWNER_KEY = "f926f017717b3e4cc3cfec4ae48367fc90007ea54b56299556fc3fcc74dba8d7"
CONTRACT_ADDRESS = "0x6Efe62FE16CcAAb7e68923C42002308fc0011BC5"
CONTRACT_ABI = [{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"MIN_BOUNTY_AMOUNT","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"MIN_DURATION","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"OWNER_FEES","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"OWNER_FEES_DIVISOR","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_dataset_id","type":"uint256"}],"name":"allowRefund","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balances","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"claim","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_dataset_id","type":"uint256"},{"internalType":"uint256","name":"_bounty_amount","type":"uint256"}],"name":"createDatasetBounty","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"datasetBounties","outputs":[{"internalType":"uint256","name":"dataset_id","type":"uint256"},{"internalType":"uint256","name":"bountyAmount","type":"uint256"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"bool","name":"allowRefund","type":"bool"},{"internalType":"bool","name":"finished","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_dataset_id","type":"uint256"}],"name":"refund","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_dataset_id","type":"uint256"},{"internalType":"address[]","name":"_winners","type":"address[]"},{"internalType":"uint256[]","name":"_shares","type":"uint256[]"}],"name":"releaseBounty","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_owner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"usdc","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"}]
RPC = "https://sepolia.base.org"

import web3
from web3 import Web3

from eth_account import Account
from eth_utils import to_checksum_address




@router.get("/endlabelling/{dataset_id}")
async def end_labelling(dataset_id):
    #done_labels = dbUtils.end_labelling(dataset_id)

    winners = dbUtils.get_winners() # [(address, score), ...]

    addresses = [to_checksum_address(w[0]) for w in winners]
    scores = [int(w[1]) for w in winners]

    if len(addresses) != len(scores):
        raise Exception(f"len addresses {len(addresses)} {len(scores)}")

    if len(scores) == 0:
        raise Exception(f"len is 0")


    w3 = Web3(Web3.HTTPProvider(RPC))
    if not w3.is_connected():
        print("Not connected to RPC")
        raise Exception("Not connected to RPC")

    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

    owner = Account.from_key(OWNER_KEY)


    tx_params = {
            'nonce':    w3.eth.get_transaction_count(owner.address),
            'gasPrice': 20000000000,
            'gas':      300_000,
            'from' :    to_checksum_address(owner.address),
            'value':    0
        }

    releaseBountyFunction = contract.functions.releaseBounty(dataset_id, addresses, scores)

    final_transaction = releaseBountyFunction.build_transaction(tx_params)
    signed_transaction = w3.eth.account.sign_transaction(final_transaction, private_key=owner.key)
    tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

    return {"tx_hash": tx_hash.hex()}

    #return done_labels

@router.get("/checkUser/{user_id}")
async def check_user(user_id):
    if not dbUtils.check_user(user_id):
        dbUtils.add_user(user_id)
        return {"status": "user added"}
    return {"status": "user exists"}

@router.get("/get_datasets_for_user/{user_id}")
async def get_datasets_for_user(user_id):
    datasets = dbUtils.get_datasets_for_user(user_id)
    payload = []
    for dataset in datasets:
        print(dataset)
        thumbnail_hash = dbUtils.get_thumbnail_hash_for_dataset(dataset.dataset_id)
        thumbnail =dataPorcessor.download_flow(thumbnail_hash)
        labels_received = dbUtils.count_labels_for_dataset(dataset.dataset_id)
        accuracy = dbUtils.calculate_dataset_accuracy(dataset.dataset_id)
        payload.append({"dataset_id": dataset.dataset_id, "name": dataset.name, "description": dataset.description, "label_options": dataset.label_options, "accuracy": accuracy, "thumbnail": thumbnail, "labels_received": labels_received})
    return payload

@router.get("/get_feed/{amount}")
async def get_feed(amount):
    randomDatas = dbUtils.get_feed(amount)
    payloads = []
    for randomData in randomDatas:
        print(f"getting {randomData.ipfs_hash}")
        labels = dbUtils.get_labels_for_datapoint(randomData.data_id)
        imgdata = dataPorcessor.download_flow(randomData.ipfs_hash)
        payload = {"url": imgdata,
                "data_id": randomData.data_id,
                "label_options": labels}
        payloads.append(payload)
    return payloads


@router.get('/get_data_point_accuracy/{data_id}')
async def test(data_id):
    return dbUtils.calculate_datapoint_accuracy(data_id)

@router.get('/get_data_set_accuracy/{dataset_id}')
async def test(dataset_id):
    return dbUtils.calculate_dataset_accuracy(dataset_id)

@router.get("/amountofvotesfordataset")
# TODO:

@router.get("/amountofvotesforuser/{user_id}")
async def amount_of_votes_for_user(user_id):
    return dbUtils.count_labels_for_user(user_id)




@router.post("/upload_data")
async def upload_data(dataset_id, file: UploadFile = File(...)):
    # try:
        allowed_types = [".jpg", ".jpeg", ".png"]

        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext not in allowed_types:
            raise HTTPException(status_code=400, detail="File type not allowed. Only .jpg, .jpeg, and .png are accepted.")
        file_content = await file.read()
        
        # upload the file to IPFS
        dataPorcessor.upload_flow(file_content, dataset_id)
        # add the data to the database



    # except Exception as e:
    #     print(f"Error in add_image: {str(e)}")
    #     raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/label")
async def label(labelData: Label):
    print(f"Received Label: {labelData}")
    if not dbUtils.add_label(data_id = labelData.data_id, user_id = labelData.user_id, label = labelData.label):
        raise HTTPException(status_code=404, detail=f"Error with label or with data_id")
    return {"status": "success"}



@router.post("/add_dataset")
async def add_dataset(dataset: Dataset):
    print(dataset)
    dataset_id = dbUtils.add_dataset(dataset.label_options, dataset.owner_id, dataset.name, dataset.description)
    return {"dataset_id": dataset_id} 





