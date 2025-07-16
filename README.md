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

Coming in Phase 4...