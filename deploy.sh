#!/bin/bash

# Playwright S3 Snapshot - AWS Lambda Deployment Script

set -e

# Configuration
STACK_NAME="playwright-s3-snapshot"
ENVIRONMENT="${ENVIRONMENT:-dev}"
AWS_REGION="${AWS_REGION:-us-east-1}"
BUCKET_NAME="${BUCKET_NAME:-playwright-screenshots-bucket}"

echo "🚀 Deploying Playwright S3 Snapshot to AWS Lambda"
echo "Environment: $ENVIRONMENT"
echo "Region: $AWS_REGION"
echo "Stack: $STACK_NAME-$ENVIRONMENT"

# Step 1: Build and push Docker image
echo "📦 Building Docker image..."
docker build -t playwright-s3-snapshot:latest .

# Step 2: Create ECR repository if it doesn't exist
echo "📡 Setting up ECR repository..."
aws ecr describe-repositories --repository-names playwright-s3-snapshot --region $AWS_REGION 2>/dev/null || \
aws ecr create-repository --repository-name playwright-s3-snapshot --region $AWS_REGION

# Step 3: Get ECR login token and login
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com

# Step 4: Tag and push image
echo "⬆️ Pushing image to ECR..."
ECR_URI=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com/playwright-s3-snapshot:latest
docker tag playwright-s3-snapshot:latest $ECR_URI
docker push $ECR_URI

# Step 5: Deploy SAM template
echo "🏗️ Deploying SAM template..."
sam deploy \
  --template-file template.yaml \
  --stack-name $STACK_NAME-$ENVIRONMENT \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    BucketName=$BUCKET_NAME \
    Environment=$ENVIRONMENT \
  --region $AWS_REGION \
  --no-confirm-changeset

# Step 6: Get outputs
echo "✅ Deployment complete!"
echo ""
echo "📋 Stack Outputs:"
aws cloudformation describe-stacks \
  --stack-name $STACK_NAME-$ENVIRONMENT \
  --region $AWS_REGION \
  --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
  --output table

echo ""
echo "🔗 API Endpoint:"
API_URL=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME-$ENVIRONMENT \
  --region $AWS_REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`ScreenshotApiUrl`].OutputValue' \
  --output text)

echo "$API_URL"
echo ""
echo "📝 Test the API:"
echo "curl -X POST $API_URL/screenshot \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"url\": \"https://example.com\"}'"