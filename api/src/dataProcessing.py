import base64
from cryptography.fernet import Fernet
from PIL import Image 
import os
import requests
from database.database import DbUtils 
import random






class DataProcessor:
    def __init__(self):
        
        self.FERNET_KEY = os.getenv('FERNET_KEY')
        self.BUCKET_SECRET_KEY = os.getenv('BUCKET_SECRET_KEY')
        self.BUCKET_KEY_ID = os.getenv('BUCKET_KEY_ID')
        self.BUCKET_ID = os.getenv('BUCKET_ID')
        self.BUCKET_NAME = os.getenv('BUCKET_NAME')
        self.fernet = Fernet('F-seNZf8l9rB5EIVAdivwuZZrcC6g_WOh_Wksyt-K7g=')
        self.dbUtils = DbUtils()


    def upload_flow(self, data, dataset_id):
        data = self.encrypt_data(data)
        cid = self.upload_data(data)
        self.dbUtils.add_data(dataset_id=dataset_id, ipfs_hash=cid)

        
    def download_flow(self, cid):
        data = self.download_data(cid)
        data = self.decrypt_data(data)
        url = self.img_to_b64(data)
        return url

    def upload_data(self, data, path = "/"):
        url = f"https://api.chainsafe.io/api/v1/bucket/{self.BUCKET_ID}/upload"
        headers = {
            "Authorization": f"Bearer {self.BUCKET_SECRET_KEY}"
        }
        files = {
            "file": (f"blob_{random.randint(0, 100000000)}",data)
        }
        data = {
            "path": path
        }

        response = requests.post(url, headers=headers, files=files, data=data)

        print(response.status_code)
        respodata = response.json()
        print(respodata)
        cid = respodata['files_details'][0]['cid']
        return cid
    
    def download_data(self, cid):

        url = f"https://ipfs.chainsafe.io/ipfs/{cid}"

        response = requests.get(url)

        if response.status_code == 200:
            with open("downloaded_file", "wb") as f:  # You can specify the file extension if known
                return response.content
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
            print(response.text)


    def encrypt_data(self, data):
        print("Encrypting data")
        encrypted_data = self.fernet.encrypt(data)
        return encrypted_data
    
    def decrypt_data(self, data):
        print("Decrypting data")
        decrypted_data = self.fernet.decrypt(data)
        return decrypted_data

    def img_to_b64(self, data) -> str:
        print("Converting image to base64")
        encoded_string = base64.b64encode(data)
        return encoded_string.decode('utf-8')

    def thumbnail(self, data):
        Image(data).thumbnail((1000,100))