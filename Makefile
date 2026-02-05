PROJECT_NAME := project-chimera

.PHONY: setup test spec-check

setup:
	@echo "Setting up Python environment for $(PROJECT_NAME)..."
	@pip install --upgrade pip
	@pip install uv
	@uv pip install --system .

test:
	@echo "Running tests with pytest..."
	@pytest -q

spec-check:
	@echo "Spec check placeholder: verifying core spec files exist..."
	@test -d specs
	@test -f specs/_meta.md
	@test -f specs/functional.md
	@test -f specs/technical.md
	@test -f skills/skill.md
	@echo "Specs and skills files present. Further semantic checks will be added later."

