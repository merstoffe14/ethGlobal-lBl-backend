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
        self.BUCKET_SECRET_KEY = "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MjA4NTg3NTcsImNuZiI6eyJqa3UiOiIvY2VydHMiLCJraWQiOiI5aHE4bnlVUWdMb29ER2l6VnI5SEJtOFIxVEwxS0JKSFlNRUtTRXh4eGtLcCJ9LCJ0eXBlIjoiYXBpX3NlY3JldCIsImlkIjoxNTk5NywidXVpZCI6IjYxOTcxZTU5LTJkNmMtNGZmYS04ZDU4LTdjZTljOTExYWE4NiIsInBlcm0iOnsiYmlsbGluZyI6IioiLCJzZWFyY2giOiIqIiwic3RvcmFnZSI6IioiLCJ1c2VyIjoiKiJ9LCJhcGlfa2V5IjoiS1FMUlZIUVFJQ0lIR0xPSkpXRkgiLCJzZXJ2aWNlIjoic3RvcmFnZSIsInByb3ZpZGVyIjoiIn0.37fqQmHCN_gKE1p3dg8NEVUf-S09CP6yVsiBu-2mJKYnAr7q0TvnCJ-ZVfrm8ldfh8XE8ZYzHQjM8r3HZjDZZw"
        self.BUCKET_KEY_ID = os.getenv('BUCKET_KEY_ID')
        self.BUCKET_ID = "dcc169d5-76c4-4ed1-866e-50c734147b94"
        self.BUCKET_NAME = os.getenv('BUCKET_NAME')
        self.fernet = Fernet('F-seNZf8l9rB5EIVAdivwuZZrcC6g_WOh_Wksyt-K7g=')
        self.dbUtils = DbUtils()
        self.LIGHTHOUSE_KEY = "221bdb55.faca2018dccc4e5e88bcef63e8ebb5ef"
        self.LIGHTHOUSE_KEY_NAME = "ethGlobal-key"


    def upload_flow(self, data, dataset_id):
        data = self.encrypt_data(data)
        cid = self.upload_data(data)
        self.dbUtils.add_data(dataset_id=dataset_id, ipfs_hash=cid)

        
    def download_flow(self, cid):
        print(f"start download {cid}")
        data = self.download_data(cid)
        print("download complete")
        data = self.decrypt_data(data)
        url = self.img_to_b64(data)
        return url

    def upload_data(self, data, path = "/"):
        print("Upload data running")
      
        url = f"https://node.lighthouse.storage/api/v0/add"
        headers = {
            "Authorization": f"Bearer {self.LIGHTHOUSE_KEY}"
        }
        files = {
            "file": (f"blob_{random.randint(0, 100000000)}",data)
        }
        

        response = requests.post(url, headers=headers, files=files)
        print(response.status_code)
    
        respodata = response.json()
        print(respodata)
        cid = respodata['Hash']
        return cid
    
    def download_data(self, cid):

        url = f"https://gateway.lighthouse.storage/ipfs/{cid}"

        response = requests.get(url)

        if response.status_code == 200:
            with open("downloaded_file", "wb") as f:  # You can specify the file extension if known
                return response.content
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
            print(response.text)
    
    # def upload_data(self, data, path = "/"):
    #     print("Upload data running")
    #     # print(self.BUCKET_ID)
    #     # print(self.BUCKET_SECRET_KEY)
    #     url = f"https://api.chainsafe.io/api/v1/bucket/{self.BUCKET_ID}/upload"
    #     headers = {
    #         "Authorization": f"Bearer {self.BUCKET_SECRET_KEY}"
    #     }
    #     files = {
    #         "file": (f"blob_{random.randint(0, 100000000)}",data)
    #     }
    #     data = {
    #         "path": path
    #     }

    #     response = requests.post(url, headers=headers, files=files, data=data)
    #     print(response.status_code)
    
    #     respodata = response.json()
    #     # print(respodata)
    #     cid = respodata['files_details'][0]['cid']
    #     return cid
    
    # def download_data(self, cid):

    #     url = f"https://ipfs.chainsafe.io/ipfs/{cid}"

    #     response = requests.get(url)

    #     if response.status_code == 200:
    #         with open("downloaded_file", "wb") as f:  # You can specify the file extension if known
    #             return response.content
    #     else:
    #         print(f"Failed to download file. Status code: {response.status_code}")
    #         print(response.text)


    def encrypt_data(self, data):
        print("Encrypting data")
        encrypted_data = self.fernet.encrypt(data)
        print("Encryption done")
        return encrypted_data
    
    def decrypt_data(self, data):
        print("Decrypting data")
        decrypted_data = self.fernet.decrypt(data)
        print("Decrypting Done")

        return decrypted_data

    def img_to_b64(self, data) -> str:
        print("Converting image to base64")
        encoded_string = base64.b64encode(data)
        return encoded_string.decode('utf-8')

    def thumbnail(self, data):
        Image(data).thumbnail((1000,100))