.PHONY: clean workflow install sync vendor

TARGET_DIR := target
WORKFLOW_FILE := $(TARGET_DIR)/alfred-datetime-format-converter.alfredworkflow
VENV_DIR := .venv
WORKFLOW_DIR := workflow

target/:
	mkdir -p target

# Install dependencies using uv
sync:
	uv sync

# Vendor dependencies into workflow directory
vendor: sync
	@echo "Vendoring dependencies into workflow directory..."
	@# Remove old vendored dependencies (keep alfred.py, process.py, icon.png, info.plist)
	@rm -rf $(WORKFLOW_DIR)/pytz $(WORKFLOW_DIR)/tzlocal $(WORKFLOW_DIR)/delorean $(WORKFLOW_DIR)/dateutil $(WORKFLOW_DIR)/six.py
	@# Copy dependencies from venv to workflow
	@cp -r $(VENV_DIR)/lib/python*/site-packages/pytz $(WORKFLOW_DIR)/
	@cp -r $(VENV_DIR)/lib/python*/site-packages/tzlocal $(WORKFLOW_DIR)/
	@cp -r $(VENV_DIR)/lib/python*/site-packages/delorean $(WORKFLOW_DIR)/
	@cp -r $(VENV_DIR)/lib/python*/site-packages/dateutil $(WORKFLOW_DIR)/
	@# Clean up __pycache__ and .pyc files
	@find $(WORKFLOW_DIR) -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find $(WORKFLOW_DIR) -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Dependencies vendored successfully."

clean:
	@rm -rf $(TARGET_DIR)

workflow: vendor clean target/
	cd $(WORKFLOW_DIR) && zip -r ../$(WORKFLOW_FILE) . -x "*.pyc" -x "__pycache__/*" -x "*/__pycache__/*" -x "*.dist-info/*" -x "*/*.dist-info/*"

install: vendor
	@echo "Installing workflow to Alfred..."
	@cp -r $(WORKFLOW_DIR)/* $$alfred_preferences/workflows/user.workflow.4819E8F4-F5E4-4E43-9E46-B9E6E16DB205/
	@echo "Workflow installed to Alfred."
