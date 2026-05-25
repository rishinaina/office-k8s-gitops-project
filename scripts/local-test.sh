#!/bin/bash
set -e

IMAGE_NAME=python-k8s-app:local

echo "Building local Docker image..."
docker build -t $IMAGE_NAME ./app

echo "For Minikube only, load image using: minikube image load $IMAGE_NAME"
echo "For Docker Desktop Kubernetes, the image is already available locally."
