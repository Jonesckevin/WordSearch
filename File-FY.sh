#!/bin/bash
# File-FY.sh - File and Content Search Tool (Bash version)
# Recursively searches for terms from .terms_list in file names and file contents
# Outputs results to a CSV file

SEARCH_PATH="."
TERMS_FILE=".terms_list"
REGEX_FILE=".regex_list"
OUTPUT_FILE="search_results.csv"
VERBOSE=false
CASE_INSENSITIVE=true

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -p|--path) SEARCH_PATH="$2"; shift 2 ;;
    -t|--terms) TERMS_FILE="$2"; shift 2 ;;
    -r|--regex) REGEX_FILE="$2"; shift 2 ;;
    -o|--output) OUTPUT_FILE="$2"; shift 2 ;;
    -v|--verbose) VERBOSE=true; shift ;;
    -c|--case-sensitive) CASE_INSENSITIVE=false; shift ;;
    -h|--help) echo "Usage: $0 [-p path] [-t terms_file] [-r regex_file] [-o output_file] [-v] [-c]"; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

log() {
  [[ $VERBOSE == true ]] && echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to escape special regex characters for literal string matching
escape_for_regex() {
  echo "$1" | sed 's/[]\/$*.^|[]/\\&/g'
}

# Function to write CSV row
write_csv_row() {
  local search_type="$1" rel_path="$2" basename="$3" line_num="$4" term="$5" matched_text="$6"
  printf '%s,"%s","%s",%s,"%s","%s"\n' "$search_type" "$rel_path" "$basename" "$line_num" "$term" "${matched_text//\"/\"\"}" >> "$OUTPUT_FILE"
}

if [[ ! -f "$TERMS_FILE" ]]; then
  echo "Error: Terms file '$TERMS_FILE' not found!" >&2
  exit 1
fi

log "Starting file and content search..."
log "Search Path: $SEARCH_PATH"
log "Terms File: $TERMS_FILE"
log "Output File: $OUTPUT_FILE"

# Read terms and regex patterns
mapfile -t SEARCH_TERMS < <(grep -vE '^\s*#|^\s*$' "$TERMS_FILE" 2>/dev/null)
log "Loaded ${#SEARCH_TERMS[@]} search terms"

REGEX_PATTERNS=()
if [[ -f "$REGEX_FILE" ]]; then
  mapfile -t REGEX_PATTERNS < <(grep -vE '^\s*#|^\s*$' "$REGEX_FILE" 2>/dev/null)
  log "Loaded ${#REGEX_PATTERNS[@]} regex patterns"
else
  log "No regex pattern file found at $REGEX_FILE. Skipping regex pattern search."
fi

# Exit if no search terms found
if [[ ${#SEARCH_TERMS[@]} -eq 0 && ${#REGEX_PATTERNS[@]} -eq 0 ]]; then
  echo "Error: No search terms or regex patterns found!" >&2
  exit 1
fi

# CSV header
echo "SearchType,FilePath,FileName,LineNumber,MatchedTerm,MatchedText" > "$OUTPUT_FILE"

MATCH_COUNT=0
FILENAME_MATCHES=0
CONTENT_MATCHES=0

# Find all files (exclude the output file itself)
mapfile -t ALL_FILES < <(find "$SEARCH_PATH" -type f ! -name "$(basename "$OUTPUT_FILE")" 2>/dev/null)
TOTAL_FILES=${#ALL_FILES[@]}
log "Found $TOTAL_FILES files to search"

# Pre-compile grep options
GREP_OPTS_CASE=""
[[ $CASE_INSENSITIVE == true ]] && GREP_OPTS_CASE="-i"

for FILE in "${ALL_FILES[@]}"; do
  [[ $VERBOSE == true ]] && echo "Checking file: $FILE"
  REL_PATH="${FILE#$PWD/}"
  # Remove leading ./ if present
  REL_PATH="${REL_PATH#./}"
  BASENAME="$(basename "$FILE")"

  # File name search (terms)
  for TERM in "${SEARCH_TERMS[@]}"; do
    if [[ $CASE_INSENSITIVE == true ]]; then
      # Convert to lowercase for case-insensitive comparison
      if [[ "${BASENAME,,}" == *"${TERM,,}"* ]]; then
        write_csv_row "FileName" "$REL_PATH" "$BASENAME" "" "$TERM" "$BASENAME"
        ((MATCH_COUNT++))
        ((FILENAME_MATCHES++))
      fi
    else
      if [[ "$BASENAME" == *"$TERM"* ]]; then
        write_csv_row "FileName" "$REL_PATH" "$BASENAME" "" "$TERM" "$BASENAME"
        ((MATCH_COUNT++))
        ((FILENAME_MATCHES++))
      fi
    fi
  done

  # File name search (regex)
  for PATTERN in "${REGEX_PATTERNS[@]}"; do
    if echo "$BASENAME" | grep -Eq $GREP_OPTS_CASE "$PATTERN"; then
      write_csv_row "FileNameRegex" "$REL_PATH" "$BASENAME" "" "$PATTERN" "$BASENAME"
      ((MATCH_COUNT++))
      ((FILENAME_MATCHES++))
    fi
  done

  # File content search (skip binary files)
  if file --mime-type "$FILE" 2>/dev/null | grep -q "text/"; then
    LINENUM=0
    while IFS= read -r LINE || [[ -n "$LINE" ]]; do
      ((LINENUM++))
      
      # Search terms in content
      for TERM in "${SEARCH_TERMS[@]}"; do
        if [[ $CASE_INSENSITIVE == true ]]; then
          if [[ "${LINE,,}" == *"${TERM,,}"* ]]; then
            write_csv_row "FileContent" "$REL_PATH" "$BASENAME" "$LINENUM" "$TERM" "$LINE"
            ((MATCH_COUNT++))
            ((CONTENT_MATCHES++))
          fi
        else
          if [[ "$LINE" == *"$TERM"* ]]; then
            write_csv_row "FileContent" "$REL_PATH" "$BASENAME" "$LINENUM" "$TERM" "$LINE"
            ((MATCH_COUNT++))
            ((CONTENT_MATCHES++))
          fi
        fi
      done
      
      # Search regex patterns in content (skip comment lines)
      [[ "$LINE" =~ ^[[:space:]]*# ]] && continue
      for PATTERN in "${REGEX_PATTERNS[@]}"; do
        if echo "$LINE" | grep -Eq $GREP_OPTS_CASE "$PATTERN"; then
          write_csv_row "FileContentRegex" "$REL_PATH" "$BASENAME" "$LINENUM" "$PATTERN" "$LINE"
          ((MATCH_COUNT++))
          ((CONTENT_MATCHES++))
        fi
      done
    done < "$FILE"
  fi
done

log "Search completed!"
log "Total matches found: $MATCH_COUNT"
log "Results saved to: $OUTPUT_FILE"

echo
echo "Summary:"
echo "  Files searched: $TOTAL_FILES"
echo "  File name matches: $FILENAME_MATCHES"
echo "  Content matches: $CONTENT_MATCHES"
echo "  Total matches: $MATCH_COUNT"
echo "  Output file: $OUTPUT_FILE"

# Show first few results if any matches found
if [[ $MATCH_COUNT -gt 0 ]]; then
  echo
  echo "First few results:"
  if command -v column >/dev/null 2>&1; then
    head -n 6 "$OUTPUT_FILE" | column -t -s,
  else
    head -n 6 "$OUTPUT_FILE"
  fi
fi

log "Script execution completed."