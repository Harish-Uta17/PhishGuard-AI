"""Legacy training entrypoint.

The production API now lives in app.main. This script is retained so the
original training workflow can still be launched manually.
"""

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer
from networksecurity.entity.config_entity import (
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
    TrainingPipelineConfig,
)
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

import sys


if __name__ == "__main__":
    try:
        trainingpipelineconfig = TrainingPipelineConfig()
        data_ingestion_config = DataIngestionConfig(trainingpipelineconfig)
        data_ingestion = DataIngestion(data_ingestion_config=data_ingestion_config)
        logging.info("Initiating the data ingestion")
        dataingestionartifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data ingestion completed and artifact is created")
        print(dataingestionartifact)

        data_validation_config = DataValidationConfig(trainingpipelineconfig)
        data_validation = DataValidation(
            data_ingestion_artifact=dataingestionartifact,
            data_validation_config=data_validation_config,
        )
        logging.info("Initiating the data validation")
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("Data validation completed and artifact is created")
        print(data_validation_artifact)

        data_transformation_config = DataTransformationConfig(trainingpipelineconfig)
        logging.info("Data transformation started")
        data_transformation = DataTransformation(
            data_validation_artifact=data_validation_artifact,
            data_transformation_config=data_transformation_config,
        )
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        print(data_transformation_artifact)
        logging.info("Data transformation completed and artifact is created")

        logging.info("Model training started")
        model_trainer_config = ModelTrainerConfig(trainingpipelineconfig)
        model_trainer = ModelTrainer(
            model_trainer_config=model_trainer_config,
            data_transformation_artifact=data_transformation_artifact,
        )
        model_trainer_artifact = model_trainer.initiate_model_trainer()

        logging.info("Model training artifact created")
        print(model_trainer_artifact)
    except Exception as e:
        raise NetworkSecurityException(e, sys)