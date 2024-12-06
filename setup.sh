#!/bin/bash
echo "Creating a new virtual environment..."
python3 -m venv venv

echo "Activating the virtual environment..."
source venv/bin/activate

echo "Installing the requirements..."
pip install -r requirements.txt