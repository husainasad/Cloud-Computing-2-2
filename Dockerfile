# Define global args
ARG FUNCTION_DIR="/home/app/"
ARG RUNTIME_VERSION="3.9"

FROM python:${RUNTIME_VERSION}-slim AS python-slim

RUN python${RUNTIME_VERSION} -m pip install --upgrade pip

FROM python-slim AS build-image

# Include global args in this stage of the build
ARG FUNCTION_DIR
ARG RUNTIME_VERSION

# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

# Install Lambda Runtime Interface Client for Python
RUN python${RUNTIME_VERSION} -m pip install awslambdaric --target ${FUNCTION_DIR}

# Stage 3 - final runtime image
# Grab a fresh copy of the Python image
FROM python-slim

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

# (Optional) Add Lambda Runtime Interface Emulator and use a script in the ENTRYPOINT for simpler local runs
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
RUN chmod 755 /usr/bin/aws-lambda-rie

# Copy requirments list
COPY requirements.txt ${FUNCTION_DIR}

# Install requirments
RUN python${RUNTIME_VERSION} -m pip install -r requirements.txt --target ${FUNCTION_DIR}

# Install additional project dependencies
RUN python${RUNTIME_VERSION} -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --target ${FUNCTION_DIR}
RUN python${RUNTIME_VERSION} -m pip install facenet-pytorch --no-deps --target ${FUNCTION_DIR}

# Copy entry script
COPY entry.sh /

# Copy project data file
COPY data.pt ${FUNCTION_DIR}

# Copy configuration
COPY lambda_config.json ${FUNCTION_DIR}

# Copy function code
COPY face-recognition.py ${FUNCTION_DIR}

RUN chmod 777 /entry.sh

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
ENTRYPOINT [ "/entry.sh" ]
CMD [ "face-recognition.handler" ]