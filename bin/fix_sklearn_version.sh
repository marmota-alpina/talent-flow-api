#!/bin/bash

echo "Installing scikit-learn version 1.6.1 directly..."

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

# Try to activate the virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "No virtual environment found. Installing in user space..."
fi

# Try different methods to install scikit-learn
echo "Installing scikit-learn version 1.6.1..."

# Try with poetry if available
if command -v poetry &> /dev/null; then
    echo "Trying with poetry..."
    poetry run pip install scikit-learn==1.6.1 || true
fi

# Try with pip directly
echo "Trying with pip directly..."
$PIP install scikit-learn==1.6.1

# Verify the installation
echo "Verifying installation..."
if command -v poetry &> /dev/null; then
    poetry run python -c "import sklearn; print(f'scikit-learn version: {sklearn.__version__}')" || true
fi

$PYTHON -c "import sklearn; print(f'scikit-learn version: {sklearn.__version__}')" || echo "Failed to verify scikit-learn version."

echo "scikit-learn version update complete."
echo "You can now run the application with: poetry run uvicorn app.main:app --reload"
