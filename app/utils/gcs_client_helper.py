from google.cloud import storage

from app.config import GOOGLE_APPLICATION_CREDENTIALS_PATH, logger


def get_gcs_client():
    try:
        client = storage.Client.from_service_account_json(GOOGLE_APPLICATION_CREDENTIALS_PATH)
        logger.info('GCS client successfully connected')
    
    except Exception as e:
        logger.info('Error during connection to GCS Client: %s' % e)
        return None

    return client
    