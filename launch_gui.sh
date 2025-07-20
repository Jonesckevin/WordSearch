#!/bin/bash
# WordSearch GUI Launcher (Linux/macOS)

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    exit 1
fi

# Check if PyQt6 is installed
if ! python3 -c "import PyQt6" &> /dev/null; then
    echo "Installing PyQt6..."
    pip3 install -r requirements.txt
fi

# Launch the GUI
python3 search_gui.py
