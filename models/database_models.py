from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json



Base = declarative_base()
class Data(Base):
    __tablename__ = "data"

    data_id = Column(Integer, primary_key=True, index=True)
    ipfs_hash = Column(String)
    dataset_id = Column(Integer)

class Dataset(Base):
    __tablename__ = "datasets"

    dataset_id = Column(Integer, primary_key=True, index=True)
    label_options = Column(JSON)
    owner_id = Column(String)
    name = Column(String)
    description = Column(String)
    thumbnail = Column(String)

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True)

class Label(Base):
    __tablename__ = "labels"

    label_id = Column(Integer, primary_key=True, index=True)
    data_id = Column(Integer)
    label = Column(String)
    user_id = Column(Integer) # Who labelled it?



