.DEFAULT_GOAL := help
PY  := python3
NPM := npm

.PHONY: help setup dev backend frontend seed test build verify clean

help:            ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

setup:           ## Install backend + frontend dependencies
	cd backend && $(PY) -m pip install -r requirements.txt
	cd frontend && $(NPM) install
	@echo "\n✅ Setup complete. Run 'make dev' next."

dev:             ## Run backend (:8000) and frontend (:5173) together
	@echo "Starting backend on :8000 and frontend on :5173 ..."
	(cd backend && $(PY) -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload & \
	 cd ../frontend && $(NPM) run dev)

backend:         ## Run only the backend on :8000
	cd backend && $(PY) -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

frontend:        ## Run only the frontend on :5173
	cd frontend && $(NPM) run dev

seed:            ## Reset the DB with demo data
	cd backend && $(PY) seed.py

test:            ## Run backend tests
	cd backend && $(PY) -m pytest -q

build:           ## Build the frontend into backend/static (single deploy)
	cd frontend && $(NPM) run build && rm -rf ../backend/static && cp -r dist ../backend/static
	@echo "\n✅ Built. Now 'cd backend && uvicorn main:app' serves everything on :8000"

verify:          ## Pre-submission checks (run before you push!)
	@bash scripts/verify.sh

clean:           ## Remove generated files
	rm -rf backend/__pycache__ backend/app.db backend/uploads backend/static frontend/dist frontend/node_modules
	@echo "Cleaned."
