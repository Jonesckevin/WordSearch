
# WordSearch

Simple scripts to search for keywords or regex in file names and file contents.

## Quick Start - GUI Version 🎨

### Windows
```cmd
launch_gui.bat
```

### Linux/macOS
```bash
./launch_gui.sh
```

## Command Line Usage Examples

### PowerShell
```powershell
# Search current directory with default settings
./File-FY.ps1

# Specify a folder and custom terms file
./File-FY.ps1 -SearchPath "C:\myfolder" -TermsFile ".\myterms.txt"

# Case-sensitive search
./File-FY.ps1 -CaseSensitive
```

### Bash
```bash
# Search current directory with default settings
./File-FY.sh

# Specify a folder and custom terms file
./File-FY.sh -p /myfolder -t myterms.txt

# Case-sensitive search
./File-FY.sh -c
```

Both scripts output results to `search_results.csv` by default.

## Installation

### GUI Requirements
```bash
pip install -r requirements.txt
```

The GUI requires Python 3.7+ and PyQt6.

