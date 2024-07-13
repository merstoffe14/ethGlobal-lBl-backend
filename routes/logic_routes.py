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
    dataset_id = dbUtils.add_dataset(dataset.label_options, dataset.owner_id,dataset.name, dataset.description)
    return {"dataset_id": dataset_id} 





