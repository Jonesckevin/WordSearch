
# WordSearch

This isn't revolutionary or anything. Its a repo that can be used to find key words or regex with in cmd, powershell, bash. It's not hyper effective, and likely will provide you more info than you want. Uses keywords or regex. This will look for files names and basic content checking.

## Usage Examples

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

