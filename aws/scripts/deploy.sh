#!/bin/bash
# Deployment script for SJU AI Tutoring Agents
# Builds and deploys all agent containers to AWS

set -e  # Exit on any error

# Check for AWS CLI
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed or not in PATH"
    exit 1
fi

# Load environment variables if .env exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file"
    export $(grep -v '^#' .env | xargs)
else
    echo "Warning: .env file not found. Make sure required environment variables are set"
fi

# Check required environment variables
required_vars=("AWS_REGION" "OPENAI_API_KEY" "GOOGLE_API_KEY" "GOOGLE_CSE_ID")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: Required environment variable $var is not set"
        exit 1
    fi
done

# Set default environment if not specified
ENV=${DEPLOY_ENV:-dev}
echo "Deploying to $ENV environment"

# ECR Repository names
BASE_REPO="sju-ai-tutor-base"
UNIVERSITY_REPO="sju-ai-tutor-university-agent-$ENV"
MOTIVATOR_REPO="sju-ai-tutor-motivator-agent-$ENV"
ORCHESTRATOR_REPO="sju-ai-tutor-orchestrator-agent-$ENV"

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
if [ $? -ne 0 ]; then
    echo "Error: Failed to get AWS account ID. Check your AWS credentials"
    exit 1
fi

# Login to ECR
echo "Logging in to Amazon ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Function to create ECR repository if it doesn't exist
create_repo_if_not_exists() {
    repo_name=$1
    repo_exists=$(aws ecr describe-repositories --repository-names $repo_name --region $AWS_REGION 2>&1 || echo "false")
    
    if [[ $repo_exists == *"RepositoryNotFoundException"* ]]; then
        echo "Creating ECR repository: $repo_name"
        aws ecr create-repository --repository-name $repo_name --region $AWS_REGION
    else
        echo "ECR repository already exists: $repo_name"
    fi
}

# Create repositories if they don't exist
create_repo_if_not_exists $BASE_REPO
create_repo_if_not_exists $UNIVERSITY_REPO
create_repo_if_not_exists $MOTIVATOR_REPO
create_repo_if_not_exists $ORCHESTRATOR_REPO

# Build and push base image
echo "Building base image..."
docker build -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$BASE_REPO:latest -f docker/base/Dockerfile .

echo "Pushing base image to ECR..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$BASE_REPO:latest

# Build and push university agent image
echo "Building university agent image..."
docker build -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$UNIVERSITY_REPO:latest -f docker/university_agent/Dockerfile .

echo "Pushing university agent image to ECR..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$UNIVERSITY_REPO:latest

# Build and push motivator agent image
echo "Building motivator agent image..."
docker build -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$MOTIVATOR_REPO:latest -f docker/motivator_agent/Dockerfile .

echo "Pushing motivator agent image to ECR..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$MOTIVATOR_REPO:latest

# Build and push orchestrator agent image
echo "Building orchestrator agent image..."
docker build -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ORCHESTRATOR_REPO:latest -f docker/orchestrator/Dockerfile .

echo "Pushing orchestrator agent image to ECR..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ORCHESTRATOR_REPO:latest

# Deploy CloudFormation stack
echo "Deploying CloudFormation stack..."
aws cloudformation deploy \
  --template-file aws/cloudformation/template.yaml \
  --stack-name sju-ai-tutor-$ENV \
  --parameter-overrides \
    Environment=$ENV \
    OpenAIApiKey=$OPENAI_API_KEY \
    GoogleApiKey=$GOOGLE_API_KEY \
    GoogleCseId=$GOOGLE_CSE_ID \
    PineconeApiKey=${PINECONE_API_KEY:-""} \
    PineconeEnvironment=${PINECONE_ENVIRONMENT:-""} \
    PineconeIndex=${PINECONE_INDEX:-""} \
  --capabilities CAPABILITY_IAM

# Get API endpoint
API_ENDPOINT=$(aws cloudformation describe-stacks --stack-name sju-ai-tutor-$ENV --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" --output text)

echo ""
echo "Deployment completed successfully!"
echo "API Endpoint: $API_ENDPOINT"
echo "University Agent: $API_ENDPOINT/university"
echo "Motivator Agent: $API_ENDPOINT/motivator"
echo "Main Chat Endpoint (Orchestrator): $API_ENDPOINT/chat"
echo ""