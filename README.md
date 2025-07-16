# Playwright S3 Snapshot

A Python CLI tool and AWS Lambda function for taking full-page screenshots of web pages using Playwright and uploading them to S3.

## Features

- Take full-page screenshots of any URL
- Upload screenshots to S3 with timestamped naming
- CLI interface for local testing
- AWS Lambda deployment for serverless operation

## Installation

```bash
pip install -e .
playwright install chromium
```

## Usage

### CLI
```bash
snapshot https://example.com --bucket my-bucket --prefix screenshots/
```

### Lambda
Deploy as AWS Lambda function and trigger with events.

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