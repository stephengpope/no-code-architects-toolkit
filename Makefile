.DEFAULT_GOAL := build_container
#.SILENT:

build_container:
	aws --region us-east-1 ecr-public get-login-password | docker login --username AWS --password-stdin public.ecr.aws/t6d9z0z5/no-code-architects-toolkit
	docker buildx build -t public.ecr.aws/t6d9z0z5/no-code-architects-toolkit:latest --push .