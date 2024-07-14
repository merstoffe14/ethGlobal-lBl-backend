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

    # Returns the {label: , confidence: , b64: } for the dataset
    def end_labelling(self, dataset_id):
        # Returns the {label: , confidence: , b64: } for the dataset
        stmt = (
            select(Data.data_id)
            .where(Data.dataset_id == dataset_id)
        )

        data_ids = [data_id for data_id in self.session.scalars(stmt)]
        labelled = []
        for data_id in data_ids:
            score = self.calculate_datapoint_accuracy(data_id)
            label = score["label"]
            confidence = score["confidence"]
            ipfs_hash = self.get_ipfs_hash_for_datapoint(data_id)
            b64 = self.dataProcessor.download_flow(ipfs_hash)
            labelled.append({"label": label, "confidence": confidence, "b64": b64})


        return labelled

    def get_winners(self, dataset_id):
        # Query to get all labels for the given dataset
        stmt = (
            select(Label.user_id, Label.label, Data.data_id)
            .join(Data, Label.data_id == Data.data_id)
            .where(Data.dataset_id == dataset_id)
        )
        
        labels = self.session.execute(stmt).all()
        
        # Dictionary to store correct labels count for each user
        user_correct_labels = {}
        
        # Iterate through all labels
        for user_id, label, data_id in labels:
            # Calculate the correct label for this data point
            correct_label = self.calculate_datapoint_accuracy(data_id)['label']
            
            # If the user's label matches the correct label, increment their count
            if label == correct_label:
                user_correct_labels[user_id] = user_correct_labels.get(user_id, 0) + 1
        
        # Convert the dictionary to a list of tuples, including only users with > 0 correct labels
        winners = [(user_id, count) for user_id, count in user_correct_labels.items() if count > 0]
        
        # Sort the list by count in descending order
        winners.sort(key=lambda x: x[1], reverse=True)
        
        return winners


    def count_labels_for_user(self, user_id):
        stmt = (
            select(Label.label)
            .where(Label.user_id == user_id)
        )

        labels = [label for label in self.session.scalars(stmt)]
        return len(labels)


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
        stmt = (
            select(Data.data_id)
            .where(Data.dataset_id == dataset_id)
        )
         
        data_ids = [data_id for data_id in self.session.scalars(stmt)]
        
        if len(data_ids) == 0:
            return 0
        
        total_score = 0
        for data_id in data_ids:
            score = self.calculate_datapoint_accuracy(data_id)
            total_score += score["confidence"]
        return total_score / len(data_ids)

    
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