from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
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
    owner_id = Column(Integer)
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


#--------------------------------------------------------------------------------

engine = create_engine("sqlite:///database.db", echo=True)
Session = sessionmaker(bind=engine)
session = Session()


# Create tables
Base.metadata.create_all(engine)


# add user
# new_user = User(user_id="test")
# session.add(new_user)
# session.commit()   

# add dataset
# new_dataset = Dataset(label_options=["Cat", "Dog", "Fish", "Elephant"], owner_id="test")
# session.add(new_dataset)
# session.commit()

# # add data
# new_data = []
# new_data.append(Data(ipfs_hash="https://source.roboflow.com/hWskdH2GEaN4rhWHC2Is/bgP8B5bsgZee5EzzUP5O/original.jpg", dataset_id=1))
# new_data.append(Data(ipfs_hash="https://as1.ftcdn.net/v2/jpg/01/63/11/70/1000_F_163117064_syJkTuCddASYjvl4WqyRmnuy8cDXpoQY.jpg", dataset_id=1))
# new_data.append(Data(ipfs_hash="https://as1.ftcdn.net/v2/jpg/06/25/48/98/1000_F_625489835_s4zUqUhzKjDp2hkknkt8exhG1l60vsUR.jpg", dataset_id=1))
# new_data.append(Data(ipfs_hash="https://hips.hearstapps.com/goodhousekeeping-uk/main/embedded/31691/dog-main.jpg", dataset_id=1))
# new_data.append(Data(ipfs_hash="https://www.haakaa.co.nz/cdn/shop/articles/25a8814a2f4466f6777af3f2be2bcb9f_1024x.jpg?v=1632199588", dataset_id=1))
# new_data.append(Data(ipfs_hash="https://supertails.com/cdn/shop/articles/1-2-1703948078392.jpg?v=1713875436", dataset_id=1))
# new_data.append(Data(ipfs_hash="https://www.thisiscolossal.com/wp-content/uploads/2016/06/fish-2.jpg", dataset_id=1))
# new_data.append(Data(ipfs_hash="https://www.thisiscolossal.com/wp-content/uploads/2016/06/fish-1.jpg", dataset_id=1))
# new_data.append(Data(ipfs_hash="https://www.seahorseaquariums.com/image/cache/catalog/Categories%20Marine/Marine%20Fish%20Mega%20Menu/Dartfish/Firefish%201-1000x1000.jpg", dataset_id=1))
# new_data.append(Data(ipfs_hash="https://d19d5sz0wkl0lu.cloudfront.net/dims4/default/e03c4dc/2147483647/thumbnail/1000x1000%3E/quality/90/?url=http%3A%2F%2Ffiles.astd.org.s3.amazonaws.com%2FTD-Article-Images%2F2018%2F07%2FKapp_LgFormat.png", dataset_id=1))
# new_data.append(Data(ipfs_hash="https://360view.3dmodels.org/zoom/Animals/African_elephant_1000_0001.jpg", dataset_id=1))
# new_data.append(Data(ipfs_hash="https://as1.ftcdn.net/v2/jpg/05/54/35/74/1000_F_554357462_Lp26FGs6TzOJmD3l9zQJh6I15nJolQl6.jpg", dataset_id=1))

# session.add_all(new_data)
# session.commit()
