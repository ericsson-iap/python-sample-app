#!/bin/bash

set -e

# More reliable than `sed -i` if we're on WSL and handling Windows paths
wsl_safe_sed_replace() {
  local pattern=$1
  local file=$2
  local tmpfile
  tmpfile=$(mktemp "${file}.XXXXXX") || exit 1
  sed "$pattern" "$file" > "$tmpfile" && mv -f "$tmpfile" "$file"
}

if [[ -z "$APP_NAME_SUFFIX" ]]; then
  echo "Error: APP_NAME_SUFFIX environment variable must be set."
  exit 1
fi

PATTERN="^[a-z0-9]([-a-z0-9]*[a-z0-9])?$"

if [[ "$APP_NAME_SUFFIX" != "APP_NAME_SUFFIX" ]]; then
  if ! [[ "$APP_NAME_SUFFIX" =~ $PATTERN ]]; then
    echo "Error: New app name '$APP_NAME_SUFFIX' is not a valid Helm chart name."
    echo "It must:"
    echo "  - Use only lowercase letters, numbers, and dashes (-)"
    echo "  - Start and end with an alphanumeric character"
    exit 1
  fi
else
  echo "WARNING: APP_NAME_SUFFIX can be set only as a placeholder. APP_NAME_SUFFIX is not valid for development purposes"
fi

APP_NAME_PREFIX="eric-oss-hello-world-python-"
NEW_APP_NAME="$APP_NAME_PREFIX$APP_NAME_SUFFIX"

if [[ ${#NEW_APP_NAME} -gt 53 ]]; then
  echo "$NEW_APP_NAME exceeds 53 characters. Helm chart name must be at most 53 characters."
  exit 1
fi

# Accept list of target paths as arguments in case we want to limit to specific paths
INPUT_PATHS=("$@")

if [[ ${#INPUT_PATHS[@]} -gt 0 ]]; then
  echo "Using provided paths as targets:"
  for path in "${INPUT_PATHS[@]}"; do
    if [[ ! -e "$path" ]]; then
      echo "Error: '$path' does not exist."
      exit 1
    fi
    echo " - $path"
  done
else
  TARGET_DIR="${TARGET_DIR:-$(pwd)}"
  echo "Using TARGET_DIR as: $TARGET_DIR"
  INPUT_PATHS=("$TARGET_DIR")
fi

chart_dirs=()

# Collect the app's chart(s)
for path in "${INPUT_PATHS[@]}"; do
  if [[ -d "$path" && -d "$path/charts" ]]; then
    chart_dirs+=("$path/charts"/*)
  fi
  if [[ "$(basename "$path")" == "charts" && -d "$path" ]]; then
    chart_dirs+=("${path%/}"/*)
  fi
done

# Expect only one chart present and assume we can use its name as our current APP_NAME
if [[ ! -d "${chart_dirs[0]}" || ${#chart_dirs[@]} -ne 1 ]]; then
  echo "Error: No valid subdirectories found in provided paths' charts/ directories."
  exit 1
fi

CURRENT_APP_NAME=$(basename "${chart_dirs[0]}")
echo "Detected CURRENT_APP_NAME as '$CURRENT_APP_NAME'"

if [[ "$CURRENT_APP_NAME" == "$NEW_APP_NAME" ]]; then
  echo "Provided NEW_APP_NAME is the same as CURRENT_APP_NAME. Exiting..."
  exit 1
fi

script_file=$(basename "$0")

echo "Replacing '$CURRENT_APP_NAME' with '$NEW_APP_NAME' in provided paths..."

echo "Updating file contents..."
for path in "${INPUT_PATHS[@]}"; do
  grep -rl "$CURRENT_APP_NAME" "$path" | while read -r file; do
    if [[ $(basename "$file") != "$script_file" && $(basename "$file") != docker.tar* ]]; then
      wsl_safe_sed_replace "s/$CURRENT_APP_NAME/$NEW_APP_NAME/g" "$file"
    fi
  done
done

echo "Renaming files..."
for path in "${INPUT_PATHS[@]}"; do
  find "$path" -depth -type f -name "*$CURRENT_APP_NAME*" | while read -r file; do
    if [[ $(basename "$file") != "$script_file" ]]; then
      newfile="$(dirname "$file")/$(basename "$file" | sed "s/$CURRENT_APP_NAME/$NEW_APP_NAME/g")"
      mv -f "$file" "$newfile"
    fi
  done
done

echo "Renaming directories..."
for path in "${INPUT_PATHS[@]}"; do
  find "$path" -depth -type d -name "*$CURRENT_APP_NAME*" | while read -r dir; do
    newdir="$(dirname "$dir")/$(basename "$dir" | sed "s/$CURRENT_APP_NAME/$NEW_APP_NAME/g")"
    mv -f "$dir" "$newdir"
  done
done

echo "Finished renaming."
