# Playwright S3 Snapshot

A Python CLI tool and AWS Lambda function for taking full-page screenshots of web pages using Playwright and uploading them to S3.

## Features

- 📸 Take full-page screenshots of any URL using Playwright
- ☁️ Upload screenshots to S3 with timestamped naming
- 🔧 Comprehensive CLI with validation and configuration support
- 📁 Batch processing from URL files
- 🔄 Retry logic for failed operations
- 🔧 Configuration file and environment variable support
- 🚀 AWS Lambda deployment for serverless operation

## Installation

```bash
pip install -e .
playwright install chromium
```

## Quick Start

```bash
# Single screenshot (local file)
python -m playwright_s3_snapshot.cli https://example.com

# Upload to S3
python -m playwright_s3_snapshot.cli https://example.com --bucket my-bucket --prefix qa/

# Create configuration file
python -m playwright_s3_snapshot.cli --create-config

# Batch processing
python -m playwright_s3_snapshot.cli --url-file urls.txt --bucket my-bucket
```

## CLI Usage

### Basic Commands
```bash
# Local screenshot
python -m playwright_s3_snapshot.cli https://example.com
python -m playwright_s3_snapshot.cli https://example.com --output screenshot.png

# S3 upload
python -m playwright_s3_snapshot.cli https://example.com --bucket my-bucket
python -m playwright_s3_snapshot.cli https://example.com --bucket my-bucket --prefix qa/

# Batch processing
python -m playwright_s3_snapshot.cli --url-file urls.txt --bucket my-bucket
```

### Advanced Options
```bash
# Custom viewport and timeout
python -m playwright_s3_snapshot.cli https://example.com --width 1280 --height 720 --timeout 60000

# Retry logic and verbose output
python -m playwright_s3_snapshot.cli https://example.com --retries 3 --verbose

# Quiet mode (only errors)
python -m playwright_s3_snapshot.cli https://example.com --quiet
```

### Configuration

#### Configuration File
Create a configuration file to set default values:

```bash
python -m playwright_s3_snapshot.cli --create-config
```

This creates `playwright-s3-snapshot.json`:
```json
{
  "bucket": "my-screenshots-bucket",
  "prefix": "qa-screenshots", 
  "region": "us-east-1",
  "width": 1920,
  "height": 1080,
  "timeout": 30000,
  "retries": 3,
  "verbose": false
}
```

Configuration files are loaded from (in order):
- `playwright-s3-snapshot.json` (current directory)
- `.playwright-s3-snapshot.json` (current directory)
- `~/.playwright-s3-snapshot.json` (home directory)

#### Environment Variables
```bash
export PS3S_BUCKET="my-bucket"
export PS3S_PREFIX="screenshots/"
export PS3S_REGION="us-west-2"
export PS3S_WIDTH=1280
export PS3S_HEIGHT=720
export PS3S_TIMEOUT=60000
export PS3S_RETRIES=3
export PS3S_VERBOSE=true
```

### Batch Processing

Create a file with URLs (one per line):
```
# urls.txt
https://example.com
https://httpbin.org/html
google.com
# Comments are ignored
```

Process all URLs:
```bash
python -m playwright_s3_snapshot.cli --url-file urls.txt --bucket my-bucket --verbose
```

## AWS Setup

### Credentials
Set AWS credentials via:
- Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- AWS CLI: `aws configure`
- IAM roles (for Lambda/EC2)

### S3 Permissions
Required S3 permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::your-bucket/*"
    }
  ]
}
```

## CLI Reference

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `url` | URL to screenshot | Required |
| `--url-file` | File with URLs (one per line) | None |
| `--bucket` | S3 bucket name | None |
| `--prefix` | S3 key prefix | Empty |
| `--region` | AWS region | us-east-1 |
| `--output` | Local output path | Auto-generated |
| `--width` | Viewport width (px) | 1920 |
| `--height` | Viewport height (px) | 1080 |
| `--timeout` | Page load timeout (ms) | 30000 |
| `--retries` | Retry attempts | 1 |
| `--verbose, -v` | Verbose output | False |
| `--quiet, -q` | Suppress output | False |
| `--create-config` | Create config file | False |

### Exit Codes
- `0`: Success
- `1`: General error
- `2`: Invalid arguments
- `130`: Interrupted by user (Ctrl+C)

## Development

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
playwright install chromium
```

## Testing

```bash
pytest
```

## AWS Lambda Deployment

Deploy as a serverless function for scalable screenshot processing.

### Prerequisites

1. **AWS CLI configured:**
   ```bash
   aws configure
   ```

2. **SAM CLI installed:**
   ```bash
   # macOS
   brew install aws-sam-cli
   
   # Windows
   # Download from: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
   ```

3. **Docker installed** (for container builds)

### Quick Deploy

```bash
# Deploy with default settings
./deploy.sh

# Or deploy with custom settings
ENVIRONMENT=prod BUCKET_NAME=my-screenshots ./deploy.sh
```

### Manual Deployment

1. **Build container image:**
   ```bash
   docker build -t playwright-s3-snapshot:latest .
   ```

2. **Deploy infrastructure:**
   ```bash
   sam deploy \
     --template-file template.yaml \
     --stack-name playwright-s3-snapshot-dev \
     --capabilities CAPABILITY_IAM \
     --parameter-overrides BucketName=my-screenshots
   ```

### API Usage

Once deployed, use the API Gateway endpoint:

```bash
# Single screenshot
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/dev/screenshot \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://example.com",
    "width": 1920,
    "height": 1080,
    "prefix": "api-screenshots/"
  }'

# Batch screenshots
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/dev/batch-screenshot \
  -H 'Content-Type: application/json' \
  -d '{
    "urls": ["https://example.com", "https://google.com"],
    "prefix": "batch-screenshots/"
  }'
```

### Lambda Function Configuration

#### Environment Variables
- `BUCKET_NAME`: S3 bucket for screenshots
- `KEY_PREFIX`: Default S3 key prefix
- `VIEWPORT_WIDTH`: Default viewport width (1920)
- `VIEWPORT_HEIGHT`: Default viewport height (1080)
- `WAIT_TIMEOUT`: Page load timeout in ms (30000)

#### Event Structure
```json
{
  "url": "https://example.com",
  "bucket": "my-bucket",
  "prefix": "screenshots/",
  "width": 1920,
  "height": 1080,
  "timeout": 30000,
  "region": "us-east-1"
}
```

#### Response Structure
```json
{
  "statusCode": 200,
  "body": {
    "success": true,
    "result": {
      "url": "https://example.com",
      "s3_url": "https://bucket.s3.amazonaws.com/key",
      "s3_key": "screenshots/2025-07-15_143022.png",
      "timestamp": "2025-07-15T14:30:22",
      "file_size": 55531
    }
  }
}
```

### Local Testing

```bash
# Test with mock S3 (offline)
python test-lambda-offline.py

# Test with real AWS credentials
python test-lambda-local.py
```

### Infrastructure Components

- **Lambda Functions:** Single and batch screenshot processing
- **API Gateway:** RESTful API endpoints
- **S3 Bucket:** Screenshot storage with lifecycle policies
- **ECR Repository:** Container image storage
- **IAM Roles:** Minimal required permissions

### Monitoring

- **CloudWatch Logs:** Function execution logs
- **CloudWatch Metrics:** Invocation count, duration, errors
- **X-Ray Tracing:** Request tracing (optional)

### Cost Optimization

- **Lambda:** Pay per request (first 1M requests/month free)
- **S3:** Lifecycle policies auto-delete old screenshots (30 days)
- **API Gateway:** Pay per API call
- **Container Images:** Optimized multi-stage build

### Troubleshooting

1. **Container too large:** Use multi-stage builds and minimize dependencies
2. **Timeout errors:** Increase Lambda timeout (max 15 minutes)
3. **Memory errors:** Increase Lambda memory (max 10GB)
4. **Playwright errors:** Ensure browser dependencies in container

### Security

- **IAM Permissions:** Minimal S3 write access only
- **VPC:** Optional VPC deployment for network isolation
- **Encryption:** S3 server-side encryption enabled
- **CORS:** Configurable origin restrictions