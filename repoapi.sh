#!/bin/bash

# Check if all required arguments are passed
if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <token> <ownername> <choice (create/delete/list)> [repo-name]"
  exit 1
fi

# Assigning arguments to variables
TOKEN=$1
OWNERNAME=$2
CHOICE=$3
REPO_NAME=$4

# GitHub API endpoint
API_URL="https://api.github.com"

# Headers for API requests
AUTH_HEADER="Authorization: token $TOKEN"
CONTENT_HEADER="Content-Type: application/json"

# Function to create a repository (correct API)
create_repo() {
  if [ -z "$REPO_NAME" ]; then
    echo "Error: Repository name must be provided for creation."
    exit 1
  fi
  
  echo "Creating repository '$REPO_NAME' for owner '$OWNERNAME'..."
  
  # Use the correct API endpoint for creating a repository
  curl -X POST -H "$AUTH_HEADER" -H "$CONTENT_HEADER" \
    -d "{\"name\": \"$REPO_NAME\", \"private\": false}" \
    "$API_URL/user/repos"
  
  echo "Repository '$REPO_NAME' created."
}

# Function to delete a repository
delete_repo() {
  if [ -z "$REPO_NAME" ]; then
    echo "Error: Repository name must be provided for deletion."
    exit 1
  fi
  
  echo "Deleting repository '$REPO_NAME' for owner '$OWNERNAME'..."
  
  # Delete the repository using GitHub's API
  curl -X DELETE -H "$AUTH_HEADER" \
    "$API_URL/repos/$OWNERNAME/$REPO_NAME"
  
  echo "Repository '$REPO_NAME' deleted."
}

# Function to list existing repositories (name and creation time)
list_repos() {
  echo "Listing repositories for owner '$OWNERNAME'..."

  # Fetch the list of repositories and filter the name and created_at fields
  curl -H "$AUTH_HEADER" \
    "$API_URL/users/$OWNERNAME/repos" | \
    grep -E '"name"|"created_at"' | \
    awk 'NR % 2 == 1 {name = $2} NR % 2 == 0 {print name " - " substr($0, 14, length($0)-15)}'
}

# Handling the choice
if [ "$CHOICE" == "create" ]; then
  create_repo
elif [ "$CHOICE" == "delete" ]; then
  delete_repo
elif [ "$CHOICE" == "list" ]; then
  list_repos
else
  echo "Invalid choice. Please choose 'create', 'delete', or 'list'."
  exit 1
fi
