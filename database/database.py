from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models.database_models import Data, Dataset, User, Label
from sqlalchemy import select
import json


class DbUtils:

    def __init__(self) -> None:

        self.engine = create_engine("sqlite:///database.db", echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()


    def add_user(self, user_id):
        new_user = User(user_id=user_id)
        self.session.add(new_user)
        self.session.commit()    
    
    def check_user(self, user_id):
        stmt = select(User).where(User.user_id.in_([user_id]))
        row = self.session.scalar(stmt)
        if row == None:
            return False
        return True
    
    def get_datasets_for_user(self,user_id):
        stmt = select(Dataset).where(Dataset.owner_id.in_([user_id]))
        return self.session.scalars(stmt).all()
    
    def get_feed(self, amount):
        random_entries = self.session.query(Data).order_by(func.random()).limit(amount).all()
        return random_entries
    
    def add_data(self, dataset_id, ipfs_hash):
        new_data = Data(dataset_id= dataset_id, ipfs_hash= ipfs_hash)
        self.session.add(new_data)
        self.session.commit()
        return new_data.data_id

    def add_dataset(self, label_options, owner_id, name, description):
        new_dataset = Dataset(label_options= label_options, owner_id= owner_id, name= name, description= description)
        self.session.add(new_dataset)
        self.session.commit()
        return new_dataset.dataset_id

    def get_dataset(self, dataset_id):
        stmt = select(Dataset).where(Dataset.dataset_id.in_([dataset_id]))
        return self.session.scalar(stmt)

    def add_label(self, data_id, user_id, label):
        
        new_label = Label(data_id= data_id, user_id= user_id, label = label)

        # Check if datapoints exists
        if not self.check_if_data_id_exists(data_id= data_id):
            return False
        print("Data exists")
        # Check if label in datapoint enum
        if not self.check_label_for_datapoint(data_id, label):
            return False
        print("Label exists")
        self.session.add(new_label)
        self.session.commit() 
        return True

    def calculate_datapoint_accuracy(self, data_id):
        stmt = (
            select(Label.label)
            .where(Label.data_id == data_id)
        )
        
        labels = [label for label in self.session.scalars(stmt)]
        
        if len(labels) == 0:
            return {"label" : "", "confidence" : 0}
        
        entries = len(labels)
        scoreList = {}
        for label in labels:
            if label in scoreList:
                scoreList[label] += 1
            else:
                scoreList[label] = 1
      
        maxScore = max(scoreList.values())
        maxLabel = [key for key in scoreList if scoreList[key] == maxScore]

        return {"label" : maxLabel[0], "confidence" : maxScore / entries}
        
    def calculate_dataset_accuracy(self, dataset_id):
        # Sum amount of labels for each datapoint
        stmt = (
            select(Label.label)
            .select_from(Label)
            .join(Data, Label.data_id == Data.data_id)
            .where(Data.dataset_id == dataset_id)
        )

        labels = [label for label in self.session.scalars(stmt)]
        if len(labels) == 0:
            return 0
        
        entries = len(labels)
        scoreList = {}
        for label in labels:
            if label in scoreList:
                scoreList[label] += 1
            else:
                scoreList[label] = 1
        
        maxScore = max(scoreList.values())
        maxLabel = [key for key in scoreList if scoreList[key] == maxScore]

        return {"label" : maxLabel[0], "confidence" : maxScore / entries}

    def count_labels_for_dataset(self, dataset_id):
        print(f"counting labels for {dataset_id}")
        stmt = (
            select(Label.label)
            .select_from(Label)
            .join(Data, Label.data_id == Data.data_id)
            .where(Data.dataset_id == dataset_id)
        )

        labels = [label for label in self.session.scalars(stmt)]
        # print(labels)
        return len(labels)
        
    
    def get_thumbnail_hash_for_dataset(self, dataset_id):
        stmt = (
            select(Data.ipfs_hash)
            .where(Data.dataset_id == dataset_id)
        )
        
        return self.session.scalars(stmt).first()
        

    ############################################################################################################
    
    def check_if_data_id_exists(self, data_id):
        stmt = select(Data).where(Data.data_id.in_([data_id]))
      
        row = self.session.scalar(stmt)
        if row == None:
            return False
       
        return True
    
    def check_label_for_datapoint(self, data_id, label):
        stmt = (
            select(Dataset.label_options)
            .select_from(Data)
            .join(Dataset, Data.dataset_id == Dataset.dataset_id)
            .where(Data.data_id == data_id)
        )
        
        dataset_label_options = self.session.scalars(stmt).first()
        print(dataset_label_options)
        print(label)
        return label in dataset_label_options
        
        
    def get_labels_for_datapoint(self, data_id):
        stmt = (
            select(Dataset.label_options)
            .select_from(Data)
            .join(Dataset, Data.dataset_id == Dataset.dataset_id)
            .where(Data.data_id == data_id)
        )
        
        return self.session.scalars(stmt).first()

    def get_ipfs_hash_for_datapoint(self, data_id):
        stmt = (
            select(Data.ipfs_hash)
            .where(Data.data_id == data_id)
        )
        
        return self.session.scalars(stmt).first()