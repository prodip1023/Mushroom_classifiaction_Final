from mushroom.entity.config_entity import DataIngestionConfig
from mushroom.exception import MushroomException
from mushroom.logger import logging
from mushroom.entity.artifact_entity import DataIngestionArtifact
from mushroom.config.configuration import Configuration 
import sys,os
import zipfile
import gdown

import pandas as pd
from sklearn.model_selection import train_test_split

class DataIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try:
            logging.info(f"{'>>'*20}Data Ingestion log started.{'<<'*20}")
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise MushroomException(e,sys) 
    def download_mushroom_data(self,) -> str:
        try:
            # extraction remote url
            download_url = self.data_ingestion_config.dataset_download_url

            # folder location to download
            tgz_download_dir = self.data_ingestion_config.tgz_download_dir
            
            if os.path.exists(tgz_download_dir):
                os.remove(tgz_download_dir)

            os.makedirs(tgz_download_dir,exist_ok=True)

            # filename
            mushroom_file_name = os.path.basename(download_url)

            tgz_file_path = os.path.join(tgz_download_dir,mushroom_file_name)

            logging.info(f"Downloaded file from :[{download_url}] into : [{tgz_file_path}]")

            # Download File
            
            file_id = download_url.split("/")[-2]
            prefix = 'https://drive.google.com/uc?/export=download&id='
            gdown.download(prefix+file_id,tgz_file_path)

            #gdown.download(download_url, tgz_file_path, quiet=False)
            

            logging.info(f"File :[{tgz_file_path}] has been downloaded successfully.")

            return tgz_file_path
        except Exception as e:
            raise MushroomException(e,sys) from e
       
    def extract_tgz_file(self,tgz_file_path:str):
        try:
            raw_data_dir = self.data_ingestion_config.raw_data_dir
            if os.path.exists(raw_data_dir):
                os.remove(raw_data_dir)

            os.makedirs(raw_data_dir,exist_ok=True)
            

            logging.info(f"Extracting tgz file:[{tgz_file_path}] into dir:[{raw_data_dir}]")
            # extracting zip file
            with zipfile.ZipFile(tgz_file_path,'r') as tgz_file_obj:
                tgz_file_obj.extractall(path=raw_data_dir)


            logging.info(f"Extraction completed")

        except Exception as e:
            raise MushroomException(e,sys) from e

    def split_data_as_train_test(self) -> DataIngestionArtifact:
        try:
            raw_data_dir = self.data_ingestion_config.raw_data_dir
            file_name = os.listdir(raw_data_dir)[0]
            mushroom_file_path = os.path.join(raw_data_dir,file_name)

            logging.info(f"Reading csv file: [{mushroom_file_path}]")
            mushroom_data_frame = pd.read_csv(mushroom_file_path)

            mushroom_data_frame["class"] = mushroom_data_frame["class"].map({'p': 0, 'e': 1})
            
            logging.info(f"Train test split initiated")
            train_set,test_set = train_test_split(mushroom_data_frame,test_size=0.2,random_state=42)

            train_file_path = os.path.join(self.data_ingestion_config.ingested_train_dir,
            file_name)
            test_file_path = os.path.join(self.data_ingestion_config.ingested_test_dir,
            file_name)

            if train_set is not None:
                os.makedirs(self.data_ingestion_config.ingested_train_dir,exist_ok=True)
                logging.info(f"Exporting train array into file: [{train_file_path}]")
                train_set.to_csv(train_file_path,index=False)
            
            if test_set is not None:
                os.makedirs(self.data_ingestion_config.ingested_test_dir,exist_ok=True)
                logging.info(f"Exporting test array into file: [{test_file_path}]")
                test_set.to_csv(test_file_path,index=False)

            data_ingestion_artifact = DataIngestionArtifact(train_file_path=train_file_path,
            test_file_path=test_file_path,
            is_ingested=True,
            message="Data ingestion completed successfully.")
            logging.info(f"Data ingestion artifact: [{data_ingestion_artifact}]")
            return data_ingestion_artifact
        except Exception as e:
            raise MushroomException(e,sys) from e
    
    def initiate_data_ingestion(self)->DataIngestionArtifact:
        try:
           tgz_file_path = self.download_mushroom_data()

           self.extract_tgz_file(tgz_file_path=tgz_file_path)

           return self.split_data_as_train_test()

        except Exception as e:
            raise MushroomException(e,sys) from e
        
    # Deleted the garbage collected objects
    def __del__(self):
        logging.info(f"{'>>'*20}Data Ingestion log completed.{'<<'*20} \n\n")