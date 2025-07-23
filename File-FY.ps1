# Example usage:
# powershell -NoProfile -ExecutionPolicy Bypass `
#   .\File-FY.ps1 `
#   -Verbose `
#   -SearchPath "D:\" `
#   -CaseSensitive `
#   -Strings `
#   -Extension "txt","log" `
#   -TermsFile ".\terms_list.txt" `
#   -RegexFile ".\regex_list.txt" `
#   -OutputFile "search_results.csv" `
#   -LogFile "search_log.txt"

param(
    [string]$SearchPath = 'C:\',  # Default search path, can be overridden
    [ValidateNotNullOrEmpty()]
    [string]$TermsFile = ".\.terms_list",
    [string]$RegexFile = ".\.regex_list",
    [string]$OutputFile = "search_results.csv",
    [string]$LogFile = "search_log.txt",
    [switch]$Verbose,
    [switch]$CaseSensitive,
    [switch]$Strings,
    [int64]$MaxFileSize = 1MB,
    [string[]]$Extension
)


### Logging
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    # Output to console if verbose
    if ($VerboseFileCheck) {
        Write-Host $logEntry -ForegroundColor Green
    }
    # Always append to logfile
    $logEntry | Out-File -FilePath $LogFile -Append -Encoding UTF8
}

[bool]$VerboseFileCheck = $Verbose.IsPresent
[bool]$CaseInsensitive = -not $CaseSensitive.IsPresent
[bool]$UseStringsExe = $Strings.IsPresent

# Check for strings.exe if requested
if ($UseStringsExe) {
    $StringsExePath = Join-Path $PSScriptRoot "strings.exe"
    $StringsExeAvailable = $false
    if (Test-Path $StringsExePath) {
        try {
            $null = & $StringsExePath -? 2>$null
            $StringsExeAvailable = $true
            Write-Log "Using strings.exe for file content search." -ForegroundColor Cyan
        }
        catch {
            $StringsExeAvailable = $false
        }
    }
    if (-not $StringsExeAvailable) {
        Write-Log "strings.exe not found locally. Attempting to download from Sysinternals..."
        $downloadUrl = "https://download.sysinternals.com/files/Strings.zip"
        $zipPath = Join-Path $PSScriptRoot "Strings.zip"
        try {
            $response = Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath -UseBasicParsing -ErrorAction SilentlyContinue
            if (Test-Path $zipPath) {
                Write-Log "Downloaded Strings.zip. Extracting..."
                Add-Type -AssemblyName System.IO.Compression.FileSystem
                [System.IO.Compression.ZipFile]::ExtractToDirectory($zipPath, $PSScriptRoot)
                Remove-Item $zipPath -Force
                if (Test-Path $StringsExePath) {
                    $StringsExeAvailable = $true
                    Write-Log "strings.exe extracted and ready for use."
                }
                else {
                    Write-Log "Extraction failed. strings.exe not found after extraction."
                    $UseStringsExe = $false
                }
            }
            else {
                Write-Log "Download failed. strings.exe will not be used."
                $UseStringsExe = $false
            }
        }
        catch {
            Write-Log "Error downloading or extracting strings.exe. Continuing with normal content search."
            $UseStringsExe = $false
        }
    }
}

### CSV Output
function Write-CsvRow {
    param(
        [string]$SearchType,
        [string]$FilePath,
        [string]$FileName,
        [string]$LineNumber,
        [string]$MatchedTerm,
        [string]$MatchedText
    )
    
    # Escape double quotes in CSV data
    $FilePath = $FilePath.Replace('"', '""')
    $FileName = $FileName.Replace('"', '""')
    $MatchedTerm = $MatchedTerm.Replace('"', '""')
    $MatchedText = $MatchedText.Replace('"', '""')
    
    $csvLine = "`"$SearchType`",`"$FilePath`",`"$FileName`",`"$LineNumber`",`"$MatchedTerm`",`"$MatchedText`""
    $csvLine | Out-File -FilePath $OutputFile -Append -Encoding UTF8
}

### Input Validation
if (-not (Test-Path $TermsFile)) {
    Write-Error "Terms file '$TermsFile' not found!"
    exit 1
}

Write-Log "Starting file and content search..."
Write-Log "Search Path: $SearchPath"
Write-Log "Terms File: $TermsFile"
Write-Log "Output File: $OutputFile"
Write-Log "Case Sensitive: $(-not $CaseInsensitive)"

### Read Search Terms
$searchTerms = Get-Content $TermsFile -ErrorAction SilentlyContinue | 
Where-Object { $_.Trim() -ne "" -and $_.Trim() -notmatch '^[#]' }
Write-Log "Loaded $($searchTerms.Count) search terms"

### Read Regex Patterns
$regexPatterns = @()
if (Test-Path $RegexFile) {
    $regexPatterns = Get-Content $RegexFile -ErrorAction SilentlyContinue | 
    Where-Object { $_.Trim() -ne "" -and $_.Trim() -notmatch '^[#]' }
    Write-Log "Loaded $($regexPatterns.Count) regex patterns"
}
else {
    Write-Log "No regex pattern file found at $RegexFile. Skipping regex pattern search."
}

### Validate Search Terms/Patterns
if ($searchTerms.Count -eq 0 -and $regexPatterns.Count -eq 0) {
    Write-Error "No search terms or regex patterns found!"
    exit 1
}

### Initialize Counters
$regexOptions = [System.Text.RegularExpressions.RegexOptions]::None
if ($CaseInsensitive) { $regexOptions = [System.Text.RegularExpressions.RegexOptions]::IgnoreCase }


$matchCount = 0
$fileNameMatches = 0
$contentMatches = 0

# Track individual counts for each term and regex
$termCounts = @{}
foreach ($term in $searchTerms) { $termCounts[$term] = 0 }
$regexCounts = @{}
foreach ($pattern in $regexPatterns) { $regexCounts[$pattern] = 0 }

### Write CSV Header
"SearchType,FilePath,FileName,LineNumber,MatchedTerm,MatchedText" | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Log "Searching files recursively..."

### Get All Files
$outputFileName = Split-Path $OutputFile -Leaf
$allFiles = Get-ChildItem -Path $SearchPath -Recurse -File -ErrorAction SilentlyContinue | 
Where-Object { $_.Name -ne $outputFileName }

# Filter by extension if specified
if ($Extension -and $Extension.Count -gt 0) {
    $extPattern = $Extension | ForEach-Object { "*." + $_ }
    $allFiles = Get-ChildItem -Path $SearchPath -Recurse -File -ErrorAction SilentlyContinue -Include $extPattern |
    Where-Object { $_.Name -ne $outputFileName }
}

$totalFiles = $allFiles.Count
Write-Log "Found $totalFiles files to search"

$fileCount = 0
foreach ($file in $allFiles) {
    $fileCount++
    if ($VerboseFileCheck) {
        Write-Host "Checking file: $($file.FullName)" -ForegroundColor DarkGray
    }
    if ($fileCount % 100 -eq 0) {
        Write-Progress -Activity "Searching Files" -Status "Processing file $fileCount of $totalFiles" -PercentComplete (($fileCount / $totalFiles) * 100)
    }
    
    try {
        $fileName = $file.Name
        $relativePath = $file.FullName.Replace((Get-Location).Path, "").TrimStart('\', '/')

        ### File Name Search (terms)
        foreach ($term in $searchTerms) {
            $matchFound = if ($CaseInsensitive) {
                $fileName.ToLower().Contains($term.ToLower())
            }
            else {
                $fileName.Contains($term)
            }
            if ($matchFound) {
                Write-CsvRow -SearchType "FileName" -FilePath $relativePath -FileName $fileName -LineNumber "" -MatchedTerm $term -MatchedText $fileName
                $matchCount++
                $fileNameMatches++
                $termCounts[$term]++
            }
        }
        
        ### File Name Search (regex)
        foreach ($pattern in $regexPatterns) {
            if ([regex]::IsMatch($fileName, $pattern, $regexOptions)) {
                Write-CsvRow -SearchType "FileNameRegex" -FilePath $relativePath -FileName $fileName -LineNumber "" -MatchedTerm $pattern -MatchedText $fileName
                $matchCount++
                $fileNameMatches++
                $regexCounts[$pattern]++
            }
        }

        ### File Content Search
        # Search all files regardless of extension
        if ($file.Length -lt $MaxFileSize) {
            try {
                if ($UseStringsExe) {
                    $content = & $StringsExePath -nobanner $file.FullName 2>$null
                }
                else {
                    $content = Get-Content $file.FullName -ErrorAction SilentlyContinue
                }
                if ($content) {
                    $lineNumber = 0
                    foreach ($line in $content) {
                        $lineNumber++
                        ### Content Search (terms)
                        foreach ($term in $searchTerms) {
                            $matchFound = if ($CaseInsensitive) {
                                $line.ToLower().Contains($term.ToLower())
                            }
                            else {
                                $line.Contains($term)
                            }
                            if ($matchFound) {
                                Write-CsvRow -SearchType "FileContent" -FilePath $relativePath -FileName $fileName -LineNumber $lineNumber -MatchedTerm $term -MatchedText $line.Trim()
                                $matchCount++
                                $contentMatches++
                                $termCounts[$term]++
                            }
                        }
                        ### Content Search (regex)
                        if ($line -notmatch '^\s*#') {
                            foreach ($pattern in $regexPatterns) {
                                if ([regex]::IsMatch($line, $pattern, $regexOptions)) {
                                    Write-CsvRow -SearchType "FileContentRegex" -FilePath $relativePath -FileName $fileName -LineNumber $lineNumber -MatchedTerm $pattern -MatchedText $line.Trim()
                                    $matchCount++
                                    $contentMatches++
                                    $regexCounts[$pattern]++
                                }
                            }
                        }
                    }
                }
            }
            catch {
                Write-Warning "Could not read content of file: $($file.FullName)"
            }
        }
    }
    catch {
        Write-Warning "Error processing file: $($file.FullName) - $($_.Exception.Message)"
    }
}

Write-Progress -Activity "Searching Files" -Completed


Write-Log "Search completed!"
Write-Log "Total matches found: $matchCount"
Write-Log "Results saved to: $OutputFile"

# Output individual term and regex counts
Write-Host "`nMatch counts for each search term:" -ForegroundColor Yellow
foreach ($term in $termCounts.Keys) {
    Write-Host "  '$term': $($termCounts[$term])" -ForegroundColor Cyan
}
Write-Host "`nMatch counts for each regex pattern:" -ForegroundColor Yellow
foreach ($pattern in $regexCounts.Keys) {
    Write-Host "  '$pattern': $($regexCounts[$pattern])" -ForegroundColor Cyan
}

### Output Summary
Write-Host "`nSummary:" -ForegroundColor Yellow
Write-Host "  Files searched: $totalFiles" -ForegroundColor Cyan
Write-Host "  File name matches: $fileNameMatches" -ForegroundColor Cyan
Write-Host "  Content matches: $contentMatches" -ForegroundColor Cyan
Write-Host "  Total matches: $matchCount" -ForegroundColor Cyan
Write-Host "  Output file: $OutputFile" -ForegroundColor Cyan

### Show First Results
if ($matchCount -gt 0) {
    Write-Host "`nFirst few results:" -ForegroundColor Yellow
    if (Test-Path $OutputFile) {
        Get-Content $OutputFile | Select-Object -First 6 | ForEach-Object { Write-Host $_ -ForegroundColor Gray }
    }
}

Write-Log "Script execution completed."
