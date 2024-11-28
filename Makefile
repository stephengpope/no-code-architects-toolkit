.DEFAULT_GOAL := build_container
#.SILENT:

build_container:
	docker buildx build -t us-east1-docker.pkg.dev/csagi-439110/no-code-architects-toolkit/no-code-architects-toolkit:latest --push .