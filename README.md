This service accepts a JSON payload containing blocks of video, audio, and voice-over text. It then generates all possible combinations of these media assets, analyzes their properties (like duration and resolution), and saves the resulting metadata as JSON files to Google Cloud Storage (GCS).

## API Endpoint

The service exposes a single primary endpoint for processing media combinations.

### `POST /generate`

This endpoint triggers the main logic of the service. It takes a JSON object specifying the media assets and returns a confirmation with a list of URLs to the generated metadata files.

#### Request Body

The endpoint expects a JSON payload with the following structure:

```json
{
  "task_name": "summer-campaign-analysis",
  "video_blocks": {
    "block1": ["http://.../videoA1.mp4", "http://.../videoA2.mp4"],
    "block2": ["http://.../videoB1.mp4"]
  },
  "audio_blocks": {
    "background_music": ["http://.../audio1.mp3", "http://.../audio2.mp3"]
  },
  "voice_blocks": {
    "voice_narrator_1": [
      {
        "text": ["This is the first sentence.", "This is the second."],
        "voice": "Sarah"
      }
    ]
  }
}
````

  - `task_name` (string): A descriptive name for the task.
  - `video_blocks` (dict): A dictionary where keys are block names and values are lists of video URLs.
  - `audio_blocks` (dict): A dictionary containing lists of background audio URLs.
  - `voice_blocks` (dict): A dictionary containing lists of voice-over objects, each with `text` (list of strings) and `voice` (string identifier).

#### Successful Response

Upon successful processing, the API returns a `200 OK` status with a JSON object:

```json
{
  "task_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "task_name": "task-name-1",
  "message": "Combinations for the task generated successfully.",
  "gcs_urls": [
    "[https://storage.cloud.google.com/your-bucket-name/a1b2c3d4.../1.json]",
    "[https://storage.cloud.google.com/your-bucket-name/a1b2c3d4.../2.json]"
  ],
  "status": "success"
}
```

## Getting Started

Follow these instructions to set up and run the project locally for development and testing.

### Prerequisites

  * Python 3.11+
  * Docker
  * Google Cloud SDK (`gcloud`)
  * `ffmpeg` installed on your local machine.

### Local Setup

1.  **Clone the Repository**

    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
    ```

2.  **Set up Google Cloud Authentication**

    To run the service locally, you need to authenticate with Google Cloud so it can access your GCS bucket.

    ```bash
    # Log in to your Google account
    gcloud auth login

    # Set your project
    gcloud config set project YOUR_PROJECT_ID

    # Create application default credentials
    gcloud auth application-default login
    ```

    This command will open a browser window for you to log in. Once complete, your local environment will have the necessary credentials to interact with Google Cloud services.

3.  **Configure Environment Variables**

    Create a `.env` file in the project root by copying the example. (If `.env.example` is not present, create `.env` manually).

    Now, edit the `.env` file and add your Google Cloud Storage bucket name:

    ```
    GCS_BUCKET_NAME="your-gcs-bucket-name"
    ```

4.  **Install Dependencies and Run the Service**

    It's recommended to use a virtual environment:

    ```bash
    # Create and activate a virtual environment
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

    # Install dependencies
    pip install -r requirements.txt

    # Run the FastAPI server
    uvicorn app.main:app --reload
    ```

    The service will be available at `http://127.0.0.1:8000`.


## Deployment

This service is deployed on **Google Cloud Run**, a fully managed serverless platform.

  - **Live URL**: `https://vgimage-747936449621.europe-west4.run.app`
  - **Containerization**: The application is containerized using the provided `Dockerfile`. This ensures a consistent and reliable environment.
  - **Environment Variables**: All sensitive information and configuration details (like `GCS_BUCKET_NAME`) are not stored in the code. They are securely injected as environment variables directly in the Google Cloud Run service configuration.


## How to Use

You can easily test the deployed endpoint using the interactive FastAPI documentation.

1.  **Open the API Documentation**
    Navigate to the following URL in your browser:
    [https://vgimage-747936449621.europe-west4.run.app/docs](https://vgimage-747936449621.europe-west4.run.app/docs)

2.  **Interact with the Endpoint**

      - Click on the `POST /generate` endpoint to expand it.
      - Click the "**Try it out**" button.
      - Modify the example JSON in the "**Request body**" section with your desired media URLs and parameters.
      - Click the "**Execute**" button to send the request.

    You will see the live response from the server, including the list of GCS URLs where the metadata files have been saved.
