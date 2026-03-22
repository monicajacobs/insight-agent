# Insight-Agent

A production-ready, secure, and scalable text analysis service deployed on Google Cloud Platform.

## Architecture Overview

Insight-Agent is a Python-based REST API that performs basic text analysis on customer feedback. The service is containerized and deployed to Google Cloud Run with infrastructure managed via Terraform.

### Architecture Diagram

```
                                    ┌─────────────────────────────────────────────────────────────┐
                                    │                     Google Cloud Platform                    │
                                    │                                                              │
┌──────────────┐                    │  ┌─────────────────────────────────────────────────────┐    │
│   GitHub     │                    │  │                    VPC Network                       │    │
│  Repository  │                    │  │                                                      │    │
│              │    Push to main    │  │   ┌───────────────────────────────────────────┐     │    │
│  ┌────────┐  │───────────────────►│  │   │            Cloud Run Service               │     │    │
│  │  Code  │  │                    │  │   │         (Internal Traffic Only)            │     │    │
│  │Terraform│ │                    │  │   │                                            │     │    │
│  │ CI/CD  │  │                    │  │   │   ┌────────────────────────────────────┐  │     │    │
│  └────────┘  │                    │  │   │   │      Insight-Agent Container       │  │     │    │
└──────────────┘                    │  │   │   │                                    │  │     │    │
       │                            │  │   │   │  ┌──────────┐    ┌─────────────┐  │  │     │    │
       │                            │  │   │   │  │  FastAPI │    │   Uvicorn   │  │  │     │    │
       │                            │  │   │   │  │   App    │◄───│   Server    │  │  │     │    │
       ▼                            │  │   │   │  └──────────┘    └─────────────┘  │  │     │    │
┌──────────────┐                    │  │   │   │        │                          │  │     │    │
│GitHub Actions│                    │  │   │   │        ▼                          │  │     │    │
│              │                    │  │   │   │  POST /analyze                    │  │     │    │
│ ┌──────────┐ │  Build & Push      │  │   │   │  GET  /health                     │  │     │    │
│ │  Build   │─┼───────────────────►│  │   │   └────────────────────────────────────┘  │     │    │
│ │  Image   │ │                    │  │   │              │                             │     │    │
│ └──────────┘ │                    │  │   │              │ Service Account             │     │    │
│      │       │                    │  │   │              │ (Least Privilege)           │     │    │
│      ▼       │                    │  │   │              ▼                             │     │    │
│ ┌──────────┐ │  Terraform Apply   │  │   └───────────────────────────────────────────┘     │    │
│ │  Deploy  │─┼───────────────────►│  │                                                      │    │
│ └──────────┘ │                    │  └─────────────────────────────────────────────────────┘    │
└──────────────┘                    │                                                              │
                                    │  ┌─────────────────────┐    ┌─────────────────────────┐     │
                                    │  │  Artifact Registry  │    │   Cloud Logging &       │     │
                                    │  │  (Docker Images)    │    │   Monitoring            │     │
                                    │  └─────────────────────┘    └─────────────────────────┘     │
                                    │                                                              │
                                    └─────────────────────────────────────────────────────────────┘
```

### GCP Services Used

| Service | Purpose |
|---------|---------|
| **Cloud Run** | Serverless container hosting for the API |
| **Artifact Registry** | Docker image storage and versioning |
| **Cloud Build** | CI/CD build environment (API enabled) |
| **Cloud Logging** | Centralized log aggregation |
| **Cloud Monitoring** | Metrics and alerting |
| **IAM** | Identity and access management |
| **Cloud Storage** | Terraform state backend (optional) |

## Design Decisions

### Why Cloud Run?

Cloud Run was chosen over other compute options for several reasons:

1. **Serverless Simplicity**: No infrastructure management required; focus on code
2. **Auto-scaling**: Scales to zero when idle (cost-effective), scales up automatically under load
3. **Pay-per-use**: Only billed for actual request processing time
4. **Managed TLS**: Automatic HTTPS certificates and termination
5. **Container Native**: Full control over runtime environment via Docker
6. **Fast Deployments**: New revisions deploy in seconds with traffic splitting capabilities

**Alternatives Considered:**
- *GKE*: Overkill for a single service; higher operational overhead
- *Compute Engine*: Requires manual scaling and infrastructure management
- *Cloud Functions*: Less control over runtime; cold start concerns for consistent latency

### Security Management Approach

1. **Internal-Only Ingress**: Cloud Run is configured with `INGRESS_TRAFFIC_INTERNAL_ONLY`, blocking all public internet access
2. **Least-Privilege Service Account**: Dedicated service account with only required permissions:
   - `roles/logging.logWriter` - Write application logs
   - `roles/monitoring.metricWriter` - Publish metrics
   - `roles/cloudtrace.agent` - Send trace data
3. **Non-Root Container**: Application runs as unprivileged user `appuser`
4. **No Secrets in Code**: All sensitive values passed via GitHub Secrets / environment variables

### CI/CD Pipeline Design

The pipeline follows a GitOps approach with clear separation of concerns:

```
Push to main
     │
     ├──► Lint & Test (Python)
     │         │
     │         ├── Ruff linting
     │         └── Pytest unit tests
     │
     ├──► Terraform Validate
     │         │
     │         ├── Format check
     │         └── Configuration validation
     │
     └──► Build & Push (on success)
               │
               ├── Build Docker image
               ├── Tag with commit SHA
               └── Push to Artifact Registry
                        │
                        ▼
                    Deploy
                        │
                        ├── Terraform plan
                        └── Terraform apply
                             (passes image tag)
```

**Image Tag Strategy**: Each deployment uses a unique tag (7-char commit SHA), enabling:
- Immutable deployments
- Easy rollbacks
- Audit trail of deployed versions

## Project Structure

```
.
├── app/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   └── tests/
│       ├── __init__.py
│       ├── test_main.py        # Unit tests
│       └── requirements-test.txt
├── terraform/
│   ├── providers.tf            # Terraform & provider config
│   ├── variables.tf            # Input variables
│   ├── main.tf                 # Core infrastructure (APIs, IAM)
│   ├── cloud-run.tf            # Cloud Run service
│   ├── outputs.tf              # Output values
│   └── terraform.tfvars.example
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD pipeline
├── Dockerfile                  # Container definition
├── .dockerignore
├── .gitignore
└── README.md
```

## Setup and Deployment Instructions

### Prerequisites

- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- [Terraform](https://developer.hashicorp.com/terraform/downloads) >= 1.5.0
- [Docker](https://docs.docker.com/get-docker/)
- A GCP Project with billing enabled
- A GitHub repository

### Step 1: Authenticate with GCP

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
export REGION="us-central1"

# Authenticate with GCP
gcloud auth login
gcloud auth application-default login
gcloud config set project $PROJECT_ID
```

### Step 2: Create Terraform State Bucket (Optional but Recommended)

```bash
# Create a GCS bucket for Terraform state
gsutil mb -p $PROJECT_ID -l $REGION gs://${PROJECT_ID}-terraform-state

# Update terraform/providers.tf with your bucket name in the backend block
```

### Step 3: Create Service Account for CI/CD

```bash
# Create service account
gcloud iam service-accounts create github-actions-sa \
  --display-name="GitHub Actions Service Account"

# Grant required roles
SA_EMAIL="github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com"

for role in roles/run.admin roles/artifactregistry.admin roles/iam.serviceAccountUser roles/storage.admin; do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="$role"
done

# Create and download key (handle securely!)
gcloud iam service-accounts keys create github-sa-key.json \
  --iam-account=$SA_EMAIL

# IMPORTANT: Add this key to GitHub Secrets, then delete the local file
cat github-sa-key.json
rm github-sa-key.json
```

### Step 4: Configure Terraform Variables

```bash
cd terraform

# Create terraform.tfvars from example
cp terraform.tfvars.example terraform.tfvars

# Edit with your project ID
# project_id = "your-project-id"
# region     = "us-central1"
```

### Step 5: Deploy Infrastructure and Application

```bash
cd terraform

# Initialize Terraform
terraform init

# Deploy APIs, Artifact Registry, and IAM first
terraform apply -target=google_project_service.required_apis \
  -target=google_artifact_registry_repository.insight_agent \
  -target=google_service_account.cloud_run_sa \
  -target=google_project_iam_member.cloud_run_logging \
  -target=google_project_iam_member.cloud_run_metrics \
  -target=google_project_iam_member.cloud_run_traces
```

### Step 6: Build and Push Docker Image

```bash
cd ..  # Back to project root

# Configure Docker for Artifact Registry
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Build for linux/amd64 (required for Cloud Run)
docker build --platform linux/amd64 \
  -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/insight-agent/insight-agent:latest .

# Push to Artifact Registry
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/insight-agent/insight-agent:latest
```

### Step 7: Deploy Cloud Run Service

```bash
cd terraform

# Deploy everything including Cloud Run
terraform apply
```

### Step 8: Configure GitHub Secrets (for CI/CD)

Add the following secrets to your GitHub repository (Settings → Secrets and variables → Actions):

| Secret Name | Value |
|-------------|-------|
| `GCP_PROJECT_ID` | Your GCP project ID |
| `GCP_SA_KEY` | Contents of the service account JSON key |

## Testing the Deployment

### Testing from Cloud Shell (Recommended for Internal-Only Services)

Since the service is configured for internal-only traffic, test from [Google Cloud Shell](https://shell.cloud.google.com):

```bash
# Set project
gcloud config set project your-project-id

# Get service URL
SERVICE_URL=$(gcloud run services describe insight-agent \
  --region=us-central1 --format='value(status.url)')

# Test health endpoint
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  "${SERVICE_URL}/health"

# Test analyze endpoint
curl -X POST "${SERVICE_URL}/analyze" \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love cloud engineering!"}'
```

**Expected responses:**

Health check:
```json
{"status": "healthy"}
```

Analyze:
```json
{"original_text": "I love cloud engineering!", "word_count": 4, "character_count": 25}
```

### Testing Locally (for Public Access - Development Only)

If you temporarily allow public access for testing:

```bash
# Update ingress to allow all traffic
cd terraform
terraform apply -var="ingress=all"

# Test directly
SERVICE_URL=$(gcloud run services describe insight-agent \
  --region=us-central1 --project=your-project-id --format='value(status.url)')

curl "${SERVICE_URL}/health"

curl -X POST "${SERVICE_URL}/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world"}'

# IMPORTANT: Revert to internal-only after testing
terraform apply -var="ingress=internal"
```

## API Reference

### POST /analyze

Analyze text and return word/character counts.

**Request:**
```json
{
  "text": "I love cloud engineering!"
}
```

**Response:**
```json
{
  "original_text": "I love cloud engineering!",
  "word_count": 4,
  "character_count": 25
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Logging and Monitoring

### Viewing Logs

```bash
# View recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=insight-agent" \
  --project=your-project-id --limit=50

# Stream logs in real-time
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=insight-agent" \
  --project=your-project-id
```

Or via the GCP Console:
1. Navigate to **Cloud Logging** → **Logs Explorer**
2. Filter by `resource.type="cloud_run_revision"`
3. Select service `insight-agent`

### Monitoring Metrics

Cloud Run provides built-in metrics accessible via Cloud Monitoring:

- **Request count**: Total requests, by response code
- **Request latency**: p50, p95, p99 latencies
- **Instance count**: Current running instances
- **CPU/Memory utilization**: Resource consumption

**View metrics:**
```bash
# Check service status
gcloud run services describe insight-agent \
  --region=us-central1 --project=your-project-id
```

**Create alerts (via Console):**
1. Navigate to **Cloud Monitoring** → **Alerting**
2. Create policies for:
   - Error rate > 1%
   - Latency p95 > 1000ms
   - Instance count approaching max

## Local Development

### Setup Virtual Environment

```bash
cd /path/to/project

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate 

# Install dependencies
pip install -r app/requirements.txt -r app/tests/requirements-test.txt
```

### Run Tests

```bash
cd app
python -m pytest tests/ -v
```

### Run Server Locally

```bash
cd app
uvicorn main:app --reload --port 8080
```

Test locally:
```bash
# Health check
curl http://localhost:8080/health

# Analyze text
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world"}'
```

### Build and Run Docker Locally

```bash
# Build image
docker build -t insight-agent:local .

# Run container
docker run -p 8080:8080 insight-agent:local

# Test
curl http://localhost:8080/health
```

## Cleanup

To destroy all resources:

```bash
cd terraform
terraform destroy
```

To delete the Terraform state bucket:
```bash
gsutil rm -r gs://${PROJECT_ID}-terraform-state
```

## Security Considerations

- Cloud Run configured for internal-only traffic
- Dedicated least-privilege service account
- Container runs as non-root user
- No secrets committed to repository
- Immutable container images with SHA tags
- Input validation via Pydantic models
