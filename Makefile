.PHONY: all venv deps dev stop-local docker-build docker-run docker-stop docker-logs clean

VENV := .venv

# Create virtual environment
$(VENV):
	python3 -m venv $(VENV)

# Install dependencies in venv
deps: $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt

# Run development server in venv with reload
dev: deps
	$(VENV)/bin/uvicorn prototype:application --reload --host 0.0.0.0 --port 8000

# Stop local uvicorn processes
stop-local:
	-pkill -f "uvicorn.*prototype"

# Build Docker image
docker-build:
	docker build -t wiki-extractor-api .

# Run Docker container (stops local app first, builds image, removes old container if exists)
docker-run: stop-local docker-build
	docker rm -f wiki-extractor-api || true
	docker run -d -p 8000:8000 --name wiki-extractor-api wiki-extractor-api

# Stop and remove Docker container
docker-stop:
	docker stop wiki-extractor-api || true
	docker rm wiki-extractor-api || true

# View Docker container logs
docker-logs:
	docker logs -f wiki-extractor-api

# Clean up venv and Docker resources
clean:
	rm -rf $(VENV)
	docker rm -f wiki-extractor-api || true
	docker rmi wiki-extractor-api || true