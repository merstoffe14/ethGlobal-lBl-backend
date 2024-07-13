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


@router.get("/get_data/{data_id}")
async def get_data(data_id):
    labels = dbUtils.get_labels_for_datapoint(data_id)
    ipfs_hash = dbUtils.get_ipfs_hash_for_datapoint(data_id)
    imgdata = dataPorcessor.download_flow(ipfs_hash)
    payload = {"url": imgdata,
                "data_id": data_id,
                "label_options": labels}
    return payload

@router.get("/get_dataset/{dataset_id}") 
async def get_dataset(dataset_id):
    dataset = dbUtils.get_dataset(dataset_id)
    return dataset
