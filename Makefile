# No-Code Architects Toolkit - Docker Build & GCP Deploy
#
# Usage:
#   make build                  - Build Docker image locally
#   make run                    - Run container locally
#   make stop                   - Stop local container
#   make push                   - Tag and push to Google Artifact Registry
#   make deploy                 - Build, push, and deploy to Cloud Run
#   make logs                   - Tail Cloud Run logs
#
# Configuration:
#   Copy .env.example to .env and set your values, or export these vars:
#     GCP_PROJECT_ID, GCP_REGION, GCP_REPO, IMAGE_NAME

# Default target
.DEFAULT_GOAL := help

# ─── Configuration ────────────────────────────────────────────────────────────

IMAGE_NAME       ?= no-code-architects-toolkit
GCP_PROJECT_ID   ?= $(shell gcloud config get-value project 2>/dev/null)
GCP_REGION       ?= us-central1
GCP_REPO         ?= nca-toolkit
CLOUD_RUN_SERVICE ?= nca-toolkit

# Artifact Registry path
REGISTRY         = $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/$(GCP_REPO)
REMOTE_IMAGE     = $(REGISTRY)/$(IMAGE_NAME)

# Local image tag
LOCAL_TAG        = $(IMAGE_NAME):latest

# ─── Local Development ────────────────────────────────────────────────────────

.PHONY: build run stop clean

## Build the Docker image locally
build:
	@echo "🔨 Building Docker image: $(LOCAL_TAG)"
	docker build -t $(LOCAL_TAG) .

## Run the container locally (requires .env file)
run:
	@echo "🚀 Starting container on port 8080"
	docker run -d --name $(IMAGE_NAME) \
		-p 8080:8080 \
		--env-file .env \
		$(LOCAL_TAG)
	@echo "✅ Running at http://localhost:8080"

## Stop and remove the local container
stop:
	@echo "🛑 Stopping container"
	-docker stop $(IMAGE_NAME)
	-docker rm $(IMAGE_NAME)

## Remove local Docker image
clean: stop
	@echo "🧹 Removing image $(LOCAL_TAG)"
	-docker rmi $(LOCAL_TAG)

# ─── GCP Artifact Registry ───────────────────────────────────────────────────

.PHONY: auth repo push

## Authenticate Docker with GCP Artifact Registry
auth:
	@echo "🔑 Authenticating with Artifact Registry"
	gcloud auth configure-docker $(GCP_REGION)-docker.pkg.dev

## Create the Artifact Registry repository (first-time setup)
repo:
	@echo "📦 Creating Artifact Registry repository: $(GCP_REPO)"
	gcloud artifacts repositories create $(GCP_REPO) \
		--repository-format=docker \
		--location=$(GCP_REGION) \
		--description="NCA Toolkit Docker images"

## Tag and push image to Artifact Registry
push: build
	@echo "📤 Pushing to $(REMOTE_IMAGE)"
	docker tag $(LOCAL_TAG) $(REMOTE_IMAGE):latest
	docker push $(REMOTE_IMAGE):latest

# ─── Cloud Run Deployment ────────────────────────────────────────────────────

.PHONY: deploy logs describe

## Build, push, and deploy to Cloud Run
deploy: push
	@echo "🚀 Deploying to Cloud Run: $(CLOUD_RUN_SERVICE)"
	gcloud run deploy $(CLOUD_RUN_SERVICE) \
		--image $(REMOTE_IMAGE):latest \
		--region $(GCP_REGION) \
		--platform managed \
		--port 8080 \
		--memory 16Gi \
		--cpu 4 \
		--timeout 300 \
		--allow-unauthenticated \
		--min-instances 0 \
		--max-instances 5 \
		--execution-environment gen2
	@echo "✅ Deployment complete"

## Tail Cloud Run logs
logs:
	gcloud run services logs tail $(CLOUD_RUN_SERVICE) --region $(GCP_REGION)

## Show Cloud Run service details
describe:
	gcloud run services describe $(CLOUD_RUN_SERVICE) --region $(GCP_REGION)

# ─── Helpers ─────────────────────────────────────────────────────────────────

.PHONY: test help

## Test the running API (local or remote)
test:
	@echo "🧪 Testing API..."
	@curl -sf -X POST http://localhost:8080/v1/toolkit/test \
		-H "X-API-Key: $${API_KEY:-test}" \
		-H "Content-Type: application/json" && echo " ✅ API is healthy" || echo " ❌ API not responding"

## Show available make targets
help:
	@printf "\n"
	@printf "\033[1;36m  ╔══════════════════════════════════════════════════╗\033[0m\n"
	@printf "\033[1;36m  ║\033[0m  \033[1;37mNo-Code Architects Toolkit\033[0m · \033[0;90mBuild & Deploy\033[0m   \033[1;36m║\033[0m\n"
	@printf "\033[1;36m  ╚══════════════════════════════════════════════════╝\033[0m\n"
	@printf "\n"
	@printf "  \033[1;33m LOCAL DEVELOPMENT\033[0m\n"
	@printf "  \033[0;90m─────────────────────────────────────────────────\033[0m\n"
	@printf "  \033[1;32mmake build\033[0m          Build Docker image\n"
	@printf "  \033[1;32mmake run\033[0m            Run container locally (needs .env)\n"
	@printf "  \033[1;32mmake stop\033[0m           Stop local container\n"
	@printf "  \033[1;32mmake clean\033[0m          Stop container and remove image\n"
	@printf "  \033[1;32mmake test\033[0m           Test the running API\n"
	@printf "\n"
	@printf "  \033[1;33m GCP DEPLOYMENT\033[0m\n"
	@printf "  \033[0;90m─────────────────────────────────────────────────\033[0m\n"
	@printf "  \033[1;34mmake auth\033[0m           Authenticate Docker with Artifact Registry\n"
	@printf "  \033[1;34mmake repo\033[0m           Create Artifact Registry repo (first time)\n"
	@printf "  \033[1;34mmake push\033[0m           Build and push image to Artifact Registry\n"
	@printf "  \033[1;35mmake deploy\033[0m         Build, push, and deploy to Cloud Run\n"
	@printf "  \033[1;34mmake logs\033[0m           Tail Cloud Run logs\n"
	@printf "  \033[1;34mmake describe\033[0m       Show Cloud Run service details\n"
	@printf "\n"
	@printf "  \033[1;33m CONFIGURATION\033[0m \033[0;90m(env vars or override on command line)\033[0m\n"
	@printf "  \033[0;90m─────────────────────────────────────────────────\033[0m\n"
	@printf "  \033[0;36mGCP_PROJECT_ID\033[0m     = \033[0;37m$(GCP_PROJECT_ID)\033[0m\n"
	@printf "  \033[0;36mGCP_REGION\033[0m         = \033[0;37m$(GCP_REGION)\033[0m\n"
	@printf "  \033[0;36mGCP_REPO\033[0m           = \033[0;37m$(GCP_REPO)\033[0m\n"
	@printf "  \033[0;36mIMAGE_NAME\033[0m         = \033[0;37m$(IMAGE_NAME)\033[0m\n"
	@printf "  \033[0;36mCLOUD_RUN_SERVICE\033[0m  = \033[0;37m$(CLOUD_RUN_SERVICE)\033[0m\n"
	@printf "\n"
