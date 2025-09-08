# Sales Analysis Pipeline with Apache Beam and Dataflow

This project implements an ETL (Extract, Transform, Load) data pipeline that processes a sales CSV file, performs data sanitization and cleaning, and calculates the total freight costs, grouped by category, for delivered and canceled orders.

The pipeline is built with Apache Beam in Python and is designed to run scalably on Google Cloud Dataflow.

## Architecture

The data flow follows a simple and robust cloud architecture:

**Google Cloud Storage (GCS)** ➔ **Google Cloud Dataflow** ➔ **Google Cloud Storage (GCS)**

1.  **Extraction:** The pipeline reads the `vendas_faker.csv` file from an `input` folder in GCS.
2.  **Transformation:** A Dataflow job executes the Beam logic to clean, validate, transform, and aggregate the data in memory.
3.  **Load:** The aggregated result is written as a new CSV file to an `output` folder in GCS.

---

## 4. Prerequisites

Before you begin, ensure you have the following tools installed and configured:

* **Python 3.12+**
* **`uv`**: An extremely fast Python package installer and manager. (Instructions at [astral.sh/uv](https://astral.sh/uv))
* **Google Cloud SDK (`gcloud`)**: Installed and authenticated with your Google account.
* An active Google Cloud Platform project with billing enabled.

---

## 5. Environment Setup (GCP)

Follow these steps to set up the necessary infrastructure in Google Cloud.

### 5.1. GCP Project Setup

First, set your active project in `gcloud`:
```bash
gcloud config set project YOUR-PROJECT-ID
```

### 5.2. Service Account Creation

Dataflow requires an identity (Service Account) to operate.
```bash
# Create the Service Account
gcloud iam service-accounts create dataflow-vendas-sa --display-name="Service Account for Sales Pipeline"

# Grant the necessary permissions (replace YOUR-PROJECT-ID)
gcloud projects add-iam-policy-binding YOUR-PROJECT-ID --member="serviceAccount:dataflow-vendas-sa@YOUR-PROJECT-ID.iam.gserviceaccount.com" --role="roles/dataflow.worker"
gcloud projects add-iam-policy-binding YOUR-PROJECT-ID --member="serviceAccount:dataflow-vendas-sa@YOUR-PROJECT-ID.iam.gserviceaccount.com" --role="roles/dataflow.admin"
gcloud projects add-iam-policy-binding YOUR-PROJECT-ID --member="serviceAccount:dataflow-vendas-sa@YOUR-PROJECT-ID.iam.gserviceaccount.com" --role="roles/storage.admin"
```

### 5.3. Google Cloud Storage Bucket Creation

The pipeline needs a bucket to store all its files.
```bash
# Create the bucket (choose a globally unique name)
gsutil mb gs://YOUR-BUCKET-NAME

# (Optional) Create the folders inside the bucket
gsutil mkdir gs://YOUR-BUCKET-NAME/input/ gs://YOUR-BUCKET-NAME/output/ gs://YOUR-BUCKET-NAME/temp/ gs://YOUR-BUCKET-NAME/staging/ gs://YOUR-BUCKET-NAME/models/
```

### 5.4. Local Authentication

To allow your Python script to interact with GCP from your local machine, generate an authentication key.
```bash
# Create and download a key for the Service Account
gcloud iam service-accounts keys create gcp-credentials.json --iam-account="dataflow-vendas-sa@YOUR-PROJECT-ID.iam.gserviceaccount.com"

# Set the environment variable so the Google libraries can find it
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/gcp-credentials.json"
```
**Important:** Add `gcp-credentials.json` to your `.gitignore` file to never commit this key to a repository!

---

## 6. Local Environment Setup with `uv`

With the cloud environment ready, set up the project on your machine.

```bash
# 1. Clone this repository
git clone <URL_OF_YOUR_REPOSITORY>
cd <NAME_OF_YOUR_REPOSITORY>

# 2. Create a virtual environment with uv
uv venv

# 3. Activate the virtual environment (command is the same)
source .venv/bin/activate

# 4. Install dependencies with uv
uv pip install -r requirements.txt

# 5. Configure the local environment variables
# Copy the example file and fill it in with your details
cp .env.example .env
nano .env  # or use your favorite editor to fill in the values
```

---

## 7. How to Run the Pipeline

With everything configured, follow these steps:

### 7.1. Prepare the Input Data

Generate the sample data and upload it to GCS.
```bash
# Generate the data file locally
python generator-data.py

# Upload the file to the 'input' folder in your bucket
gsutil cp vendas_faker.csv gs://YOUR-BUCKET-NAME/input/
```

### 7.2. Run the Pipeline

Execute the `main.py` script. It will read the settings from your `.env` file and submit the job to Dataflow.
```bash
python main.py
```
You can monitor the job in the Dataflow UI in the Google Cloud Console.

### 7.3. Check the Output

After the job completes, the results will be in the output folder of your bucket.
```bash
gsutil ls gs://YOUR-BUCKET-NAME/output/
```

---

## 8. Project Structure

```
.
├── .env                  # Your local settings (DO NOT COMMIT TO GIT)
├── .env.example          # Example configuration for other developers
├── .gitignore
├── README.md             # This documentation
├── gcp-credentials.json  # Authentication key (DO NOT COMMIT TO GIT)
├── generator-data.py     # Script to generate test data
├── main.py               # Main script that runs the pipeline
├── requirements.txt      # Python dependencies for the project
└── pipeline/
    ├── __init__.py
    └── transforms.py     # Module with DoFn transformation classes
```

---

## 9. Running the Job from a Template

With the template published, anyone with the correct permissions can run the pipeline using this `gcloud` command. Note that it is much cleaner, as the complexity is already packaged into the template.

```bash
# Set variables for the command (replace with your values)
PROJECT_ID="your-project-id"
BUCKET_NAME="your-bucket-name"
REGION="us-east1"
JOB_NAME="vendas-processing-job"
SERVICE_ACCOUNT_EMAIL="dataflow-vendas-sa@${PROJECT_ID}.iam.gserviceaccount.com"
TEMPLATE_PATH="gs://${BUCKET_NAME}/models/template_vendas.json"

# Command to run the job
gcloud dataflow flex-template run ${JOB_NAME} \
    --template-file-gcs-location ${TEMPLATE_PATH} \
    --project ${PROJECT_ID} \
    --region ${REGION} \
    --staging-location "gs://${BUCKET_NAME}/staging/" \
    --temp-location "gs://${BUCKET_NAME}/temp/" \
    --service-account-email ${SERVICE_ACCOUNT_EMAIL} \
    --max-workers 1 \
    --num-workers 1 \
    --parameters input_path="gs://${BUCKET_NAME}/input/vendas_faker.csv" \
    --parameters output_path="gs://${BUCKET_NAME}/output/totals_aggregates"
```
