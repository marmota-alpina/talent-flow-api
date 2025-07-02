#!/bin/bash

echo "Rebuilding virtual environment with correct scikit-learn version..."

# Try to find Python and pip
if command -v python3 &> /dev/null; then
    PYTHON="python3"
elif command -v python &> /dev/null; then
    PYTHON="python"
else
    echo "Error: Python not found. Please install Python 3."
    exit 1
fi

if command -v pip3 &> /dev/null; then
    PIP="pip3"
elif command -v pip &> /dev/null; then
    PIP="pip"
else
    echo "Error: pip not found. Please install pip."
    exit 1
fi

echo "Using Python: $($PYTHON --version)"
echo "Using pip: $($PIP --version)"

# Check if Poetry is installed
if command -v poetry &> /dev/null; then
    echo "Poetry found. Attempting to rebuild environment with Poetry..."

    # Remove existing virtual environment
    echo "Removing existing virtual environment..."
    rm -rf .venv

    # Update the lock file to match pyproject.toml
    echo "Updating lock file..."
    poetry lock || echo "Warning: Failed to update lock file. Continuing anyway..."

    # Install dependencies and create a new virtual environment
    echo "Installing dependencies and creating a new virtual environment..."
    poetry install --no-root || echo "Warning: Failed to install dependencies with Poetry. Trying alternative method..."

    # Verify scikit-learn version
    echo "Verifying scikit-learn version with Poetry..."
    poetry run python -m app.check_sklearn_version || echo "Warning: Failed to verify scikit-learn version with Poetry."

    # Verify imbalanced-learn version
    echo "Verifying imbalanced-learn version with Poetry..."
    poetry run python -m app.check_imbalanced_learn_version || echo "Warning: Failed to verify imbalanced-learn version with Poetry."
else
    echo "Poetry not found. Using alternative method..."
fi

# Fallback to direct pip installation if Poetry failed or is not available
echo "Installing scikit-learn version 1.6.1 directly with pip..."
$PIP install scikit-learn==1.6.1

# Try to install imbalanced-learn if needed
echo "Installing imbalanced-learn version 0.13.0 directly with pip..."
$PIP install imbalanced-learn==0.13.0

# Verify installations
echo "Verifying installations..."
$PYTHON -c "import sklearn; print(f'scikit-learn version: {sklearn.__version__}')" || echo "Failed to verify scikit-learn version."
$PYTHON -c "import imblearn; print(f'imbalanced-learn version: {imblearn.__version__}')" || echo "Failed to verify imbalanced-learn version."

echo "Environment setup complete."
echo "You can now run the application with: poetry run uvicorn app.main:app --reload"
echo "Or if Poetry is not working: $PYTHON -m uvicorn app.main:app --reload"
