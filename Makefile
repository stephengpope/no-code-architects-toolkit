# No-Code Architects Toolkit - Docker Build & GCP Deploy
#
# Usage:
#   make setup                  - Generate .env file with API key for running the server
#   make build                  - Build Docker image locally
#   make up                     - Build and start container
#   make down                   - Stop and remove container
#   make connect                - Connect CLI tools to a running API instance
#   make push                   - Tag and push to Google Artifact Registry
#   make deploy                 - Build locally, push, and deploy to Cloud Run
#   make cloud-deploy           - Build on Cloud Build and deploy to Cloud Run
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

.PHONY: setup build up up-local down connect clean

## Generate .env file with API key — prepares the server to run
setup:
	@if [ -f .env ]; then \
		printf "\033[1;33m  .env already exists.\033[0m\n"; \
		printf "  Overwrite? [y/N]: "; \
		read ans; \
		case "$$ans" in [yY]*) ;; *) echo "  Keeping existing .env"; exit 0 ;; esac; \
	fi
	@printf "\n"
	@printf "\033[1;36m  NCA Toolkit — Server Setup\033[0m\n"
	@printf "\033[0;90m  ──────────────────────────────────────────────────\033[0m\n"
	@printf "\n"
	@printf "  This creates a .env file to configure the API server.\n"
	@printf "  An API key will be auto-generated for you.\n"
	@printf "\n"
	@API_KEY=$$(python3 -c "import secrets; print(secrets.token_urlsafe(32))"); \
	cp .env.example .env; \
	if [ "$$(uname)" = "Darwin" ]; then \
		sed -i '' "s|API_KEY=your_api_key_here|API_KEY=$$API_KEY|" .env; \
	else \
		sed -i "s|API_KEY=your_api_key_here|API_KEY=$$API_KEY|" .env; \
	fi; \
	printf "  \033[1;32m.env created with generated API key:\033[0m\n"; \
	printf "  \033[0;36m$$API_KEY\033[0m\n"; \
	printf "\n"; \
	printf "  \033[0;90mSave this key — you'll need it to connect clients.\033[0m\n"; \
	printf "\n"; \
	printf "  \033[1;33mNext steps:\033[0m\n"; \
	printf "    1. Edit .env to configure your storage provider (S3 or GCP)\n"; \
	printf "    2. \033[1;32mmake up\033[0m        Start the server\n"; \
	printf "    3. \033[1;32mmake connect\033[0m   Connect the CLI to the running server\n"; \
	printf "\n"

## Connect CLI tools to a running API instance
connect:
	@python3 tools/nca.py connect

## Build the Docker image locally (linux/amd64 for Cloud Run compatibility)
build:
	@echo "🔨 Building Docker image: $(LOCAL_TAG) (linux/amd64)"
	docker build --platform linux/amd64 -t $(LOCAL_TAG) .

## Start the container locally (requires .env file)
up: build
	@echo "🚀 Starting container on port 8080"
	docker run -d --name $(IMAGE_NAME) \
		-p 8080:8080 \
		--env-file .env \
		$(LOCAL_TAG)
	@echo "✅ Running at http://localhost:8080"

## Start container with local file I/O (no cloud storage needed)
up-local: build
	@mkdir -p local/input local/output
	@echo "🚀 Starting container with local file mounts"
	docker run -d --name $(IMAGE_NAME) \
		-p 8080:8080 \
		--env-file .env \
		-v $(CURDIR)/local/input:/data/input:ro \
		-v $(CURDIR)/local/output:/data/output \
		$(LOCAL_TAG)
	@echo "✅ Running at http://localhost:8080"
	@echo ""
	@echo "  📂 Input files:  ./local/input/  → /data/input  (read-only)"
	@echo "  📂 Output files: ./local/output/ → /data/output (writable)"
	@echo ""
	@echo "  Usage: place files in ./local/input/ then reference as:"
	@echo "    file:///data/input/yourfile.mp4"
	@echo ""
	@echo "  Or use the CLI:  python3 tools/nca.py transcribe --file ./local/input/video.mp4"

## Stop and remove the local container
down:
	@echo "🛑 Stopping container"
	-docker stop $(IMAGE_NAME)
	-docker rm $(IMAGE_NAME)

## Remove local Docker image
clean: down
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

# ─── Cloud Build (remote builds on GCP) ─────────────────────────────────────

.PHONY: cloud-build cloud-deploy

## Build image remotely with Cloud Build (native amd64, no local Docker needed)
cloud-build:
	@echo "☁️  Building on Cloud Build: $(REMOTE_IMAGE)"
	gcloud builds submit . \
		--tag $(REMOTE_IMAGE):latest \
		--region $(GCP_REGION) \
		--machine-type e2-highcpu-32 \
		--timeout 1800
	@echo "✅ Cloud Build complete: $(REMOTE_IMAGE):latest"

## Build on Cloud Build and deploy to Cloud Run
cloud-deploy: cloud-build
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "🚀 Deploying to Cloud Run: $(CLOUD_RUN_SERVICE)"
	@grep -v '^\s*\#' .env | grep -v '^\s*$$' | sed 's/^\([^=]*\)=\(.*\)/\1: "\2"/' > /tmp/nca-env-vars.yaml
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
		--execution-environment gen2 \
		--no-use-http2 \
		--env-vars-file /tmp/nca-env-vars.yaml
	@rm -f /tmp/nca-env-vars.yaml
	@echo "✅ Deployment complete"

# ─── Cloud Run Deployment (local build) ─────────────────────────────────────

.PHONY: deploy logs describe

## Build, push, and deploy to Cloud Run (reads env vars from .env)
deploy: push
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "🚀 Deploying to Cloud Run: $(CLOUD_RUN_SERVICE)"
	@# Convert .env to YAML for gcloud --env-vars-file (handles commas in values)
	@grep -v '^\s*\#' .env | grep -v '^\s*$$' | sed 's/^\([^=]*\)=\(.*\)/\1: "\2"/' > /tmp/nca-env-vars.yaml
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
		--execution-environment gen2 \
		--no-use-http2 \
		--env-vars-file /tmp/nca-env-vars.yaml
	@rm -f /tmp/nca-env-vars.yaml
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
	@curl -sf -X GET http://localhost:8080/v1/toolkit/test \
		-H "X-API-Key: $${API_KEY:-test}" && echo " ✅ API is healthy" || echo " ❌ API not responding"

## Show available make targets
help:
	@printf "\n"
	@printf "\033[1;36m  ╔══════════════════════════════════════════════════╗\033[0m\n"
	@printf "\033[1;36m  ║\033[0m  \033[1;37mNo-Code Architects Toolkit\033[0m · \033[0;90mBuild & Deploy\033[0m   \033[1;36m║\033[0m\n"
	@printf "\033[1;36m  ╚══════════════════════════════════════════════════╝\033[0m\n"
	@printf "\n"
	@printf "  \033[1;33m SETUP & CONNECT\033[0m\n"
	@printf "  \033[0;90m─────────────────────────────────────────────────\033[0m\n"
	@printf "  \033[1;32mmake setup\033[0m          Generate .env with API key (server config)\n"
	@printf "  \033[1;32mmake connect\033[0m        Connect CLI to a running API instance\n"
	@printf "\n"
	@printf "  \033[1;33m LOCAL DEVELOPMENT\033[0m\n"
	@printf "  \033[0;90m─────────────────────────────────────────────────\033[0m\n"
	@printf "  \033[1;32mmake build\033[0m          Build Docker image\n"
	@printf "  \033[1;32mmake up\033[0m             Build and start container (cloud storage)\n"
	@printf "  \033[1;32mmake up-local\033[0m       Build and start with local file I/O\n"
	@printf "  \033[1;32mmake down\033[0m           Stop and remove container\n"
	@printf "  \033[1;32mmake clean\033[0m          Stop container and remove image\n"
	@printf "  \033[1;32mmake test\033[0m           Test the running API\n"
	@printf "\n"
	@printf "  \033[1;33m GCP DEPLOYMENT\033[0m\n"
	@printf "  \033[0;90m─────────────────────────────────────────────────\033[0m\n"
	@printf "  \033[1;34mmake auth\033[0m           Authenticate Docker with Artifact Registry\n"
	@printf "  \033[1;34mmake repo\033[0m           Create Artifact Registry repo (first time)\n"
	@printf "  \033[1;34mmake push\033[0m           Build and push image to Artifact Registry\n"
	@printf "  \033[1;35mmake deploy\033[0m         Build locally, push, and deploy to Cloud Run\n"
	@printf "  \033[1;35mmake cloud-deploy\033[0m   Build on Cloud Build and deploy (recommended)\n"
	@printf "  \033[1;34mmake cloud-build\033[0m    Build image remotely on Cloud Build\n"
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
