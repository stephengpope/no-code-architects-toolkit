.DEFAULT_GOAL := build_container
#.SILENT:

build_container:
	gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin https://us-east1-docker.pkg.dev
	docker buildx build -t us-east1-docker.pkg.dev/csagi-439110/no-code-architects-toolkit:latest --push .