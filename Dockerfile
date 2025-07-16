# Multi-stage build for AWS Lambda with Playwright
FROM public.ecr.aws/lambda/python:3.12

# Install system dependencies for Playwright
RUN dnf update -y && \
    dnf install -y \
        wget \
        unzip \
        fontconfig \
        freetype \
        harfbuzz \
        ca-certificates \
        ttf-liberation \
        gtk3 \
        libXcomposite \
        libXdamage \
        libXrandr \
        libgbm \
        libatk-bridge-2.0 \
        libdrm \
        libXss \
        libasound \
        && dnf clean all

# Copy requirements and install Python dependencies
COPY requirements-lambda.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r requirements-lambda.txt

# Install Playwright and browsers
RUN pip install playwright==1.53.0
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application code
COPY src/ ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler
CMD ["playwright_s3_snapshot.lambda_handler.lambda_handler"]