from google.cloud import storage

from app.config import logger


def get_gcs_client():
    try:
        client = storage.Client()
        logger.info('GCS client successfully connected')
    
    except Exception as e:
        logger.info('Error during connection to GCS Client: %s' % e)
        return None

    return client
    