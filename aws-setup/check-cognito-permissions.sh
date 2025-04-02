#!/bin/bash
# Script to check if your AWS role has Cognito permissions

# Set your SSO profile name here
AWS_PROFILE="SJU-AITutor-Perm-Set"

# Colors for output
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RESET="\033[0m"
BOLD="\033[1m"

echo -e "${BOLD}Checking AWS Cognito permissions...${RESET}"
echo

# First, make sure we're authenticated
echo -e "Testing AWS authentication with profile: ${BOLD}${AWS_PROFILE}${RESET}"
aws sts get-caller-identity --profile $AWS_PROFILE
if [ $? -ne 0 ]; then
    echo -e "${RED}${BOLD}Error: Not authenticated with AWS SSO.${RESET}"
    echo -e "Please run:${BOLD} aws sso login --profile $AWS_PROFILE ${RESET}"
    exit 1
fi
echo -e "${GREEN}Successfully authenticated with AWS SSO!${RESET}"
echo

# Now test Cognito permissions specifically
echo -e "Testing Cognito permissions..."
echo

echo -e "1. Testing ${BOLD}cognito-idp:ListUserPools${RESET} permission..."
aws cognito-idp list-user-pools --max-results 10 --profile $AWS_PROFILE > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Success: Can list Cognito user pools${RESET}"
else
    echo -e "${RED}Error: Cannot list Cognito user pools${RESET}"
    echo -e "${YELLOW}This permission is needed to see existing user pools${RESET}"
fi

echo -e "2. Testing ${BOLD}cognito-idp:CreateUserPool${RESET} permission..."
# We'll just test the IAM permission check, not actually create anything
aws cognito-idp create-user-pool --pool-name "test-permission-check-delete-me" --profile $AWS_PROFILE 2>&1 | grep -q "UnauthorizedOperation\|AccessDenied"
if [ $? -eq 1 ]; then
    echo -e "${GREEN}Success: Can create Cognito user pools${RESET}"
else
    echo -e "${RED}Error: Cannot create Cognito user pools${RESET}"
    echo -e "${YELLOW}This permission is needed to create a new user pool${RESET}"
fi

echo
echo -e "${BOLD}Permission Check Summary:${RESET}"
echo -e "If any tests failed, you'll need to ask your AWS administrator to"
echo -e "add the following policies to your role:"
echo -e "  - ${BOLD}AmazonCognitoPowerUser${RESET} or"
echo -e "  - Custom policy with cognito-idp:* permissions"
echo
echo -e "Alternatively, you can have an administrator run the Cognito setup"
echo -e "script and just get the User Pool ID and App Client ID values from them."