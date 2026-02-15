#!/bin/bash
set -e

# MangroveMarkets Cloud Run Deployment Script
# Usage: ./deploy.sh [region]

PROJECT_ID="mangrove-markets"
SERVICE_NAME="mangrovemarkets"
REGION="${1:-us-central1}"
REGISTRY="us-central1-docker.pkg.dev"
REPO_NAME="mangrove-markets-repo"
IMAGE_NAME="${REGISTRY}/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}:latest"

echo "🌳 Deploying MangroveMarkets to Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Ensure we're using the correct project
gcloud config set project $PROJECT_ID

# Create Artifact Registry repository if it doesn't exist
echo "📦 Ensuring Artifact Registry repository exists..."
if ! gcloud artifacts repositories describe $REPO_NAME --location=$REGION &>/dev/null; then
    echo "Creating Artifact Registry repository..."
    gcloud artifacts repositories create $REPO_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="MangroveMarkets container images"
else
    echo "Repository already exists."
fi

# Configure Docker auth for Artifact Registry
echo "🔐 Configuring Docker authentication..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# Build and push image
echo "🏗️  Building Docker image..."
docker build --platform linux/amd64 -t $IMAGE_NAME .

echo "⬆️  Pushing image to Artifact Registry..."
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --timeout 120 \
    --set-env-vars "ENV=production" \
    --quiet

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')

echo ""
echo "✅ Deployment complete!"
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "To map a custom domain:"
echo "  gcloud run domain-mappings create --service=$SERVICE_NAME --domain=yourdomain.com --region=$REGION"
