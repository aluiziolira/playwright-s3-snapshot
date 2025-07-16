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
        liberation-fonts \
        gtk3 \
        libXcomposite \
        libXdamage \
        libXrandr \
        mesa-libgbm \
        at-spi2-atk \
        libdrm \
        libXScrnSaver \
        alsa-lib \
        && dnf clean all

# Copy requirements and install Python dependencies
COPY requirements-lambda.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r requirements-lambda.txt

# Install Playwright and browsers
RUN pip install playwright==1.53.0

# Set Playwright environment variables for Lambda
ENV PLAYWRIGHT_BROWSERS_PATH=/var/task/browsers
ENV PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true

# Install browsers to a specific location
RUN PLAYWRIGHT_BROWSERS_PATH=/var/task/browsers playwright install chromium
RUN PLAYWRIGHT_BROWSERS_PATH=/var/task/browsers playwright install-deps chromium || true

# Copy application code
COPY src/ ${LAMBDA_TASK_ROOT}/

# Verify browser installation
RUN ls -la /var/task/browsers/ || echo "Browsers directory not found"
RUN find /var/task/browsers -name "*chrome*" -o -name "*headless*" | head -10 || echo "Chrome binaries not found"

# Set the CMD to your handler
CMD ["playwright_s3_snapshot.lambda_handler.lambda_handler"]