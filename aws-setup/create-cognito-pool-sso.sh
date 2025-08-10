#!/bin/bash
# AWS Cognito User Pool Creation Script for SJU-AI-Tutor
# This script creates a Cognito user pool and app client configured for the SJU-AI-Tutor application
# Version: AWS SSO Compatible

# Set variables
USER_POOL_NAME="sju-ai-tutor-users"
CLIENT_NAME="sju-ai-tutor-web-client"
REGION="us-east-2"  # Change this to your preferred region
AWS_PROFILE="default" # Change this to your SSO profile name (e.g., "sju-dev")

# Text styling
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
RESET="\033[0m"

echo -e "${BOLD}${BLUE}=== Setting up Cognito User Pool for SJU-AI-Tutor ===${RESET}"
echo -e "${YELLOW}AWS Profile: ${AWS_PROFILE}${RESET}"
echo -e "${YELLOW}Region: ${REGION}${RESET}"
echo -e "${YELLOW}User Pool Name: ${USER_POOL_NAME}${RESET}"
echo -e "${YELLOW}App Client Name: ${CLIENT_NAME}${RESET}"
echo -e ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${BOLD}${RED}Error: AWS CLI is not installed.${RESET}"
    echo "Please install the AWS CLI using the instructions at:"
    echo "https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check AWS credentials/session
echo -e "${BOLD}Step 1:${RESET} Checking AWS credentials..."

# Check if we can access AWS with the specified profile
if [ "$AWS_PROFILE" == "default" ]; then
    # Using default profile
    PROFILE_ARG=""
    PROFILE_MSG="default profile"
else
    # Using named profile
    PROFILE_ARG="--profile $AWS_PROFILE"
    PROFILE_MSG="profile $AWS_PROFILE"
fi

# Check if credentials work
aws $PROFILE_ARG sts get-caller-identity --region $REGION > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${BOLD}${RED}Error: Cannot access AWS with $PROFILE_MSG.${RESET}"
    
    if [ "$AWS_PROFILE" != "default" ]; then
        echo -e "Please run: ${BOLD}aws sso login --profile $AWS_PROFILE${RESET}"
    else
        echo -e "Please run: ${BOLD}aws configure${RESET} or set up AWS SSO"
    fi
    
    exit 1
fi

# Get account info for confirmation
ACCOUNT_INFO=$(aws $PROFILE_ARG sts get-caller-identity --region $REGION --output json)
ACCOUNT_ID=$(echo $ACCOUNT_INFO | grep -o '"Account": "[^"]*' | cut -d'"' -f4)
IDENTITY=$(echo $ACCOUNT_INFO | grep -o '"Arn": "[^"]*' | cut -d'"' -f4)

echo -e "${GREEN}Authenticated successfully with ${PROFILE_MSG}!${RESET}"
echo -e "AWS Account: ${BOLD}$ACCOUNT_ID${RESET}"
echo -e "Identity: ${BOLD}$IDENTITY${RESET}"
echo -e ""

# Ask for confirmation
read -p "Press Enter to continue or Ctrl+C to abort..." -n 1 -r -s
echo -e "\n"

echo -e "${BOLD}Step 2:${RESET} Creating Cognito User Pool..."
USER_POOL_ID=$(aws $PROFILE_ARG cognito-idp create-user-pool \
    --pool-name "${USER_POOL_NAME}" \
    --policies '{"PasswordPolicy":{"MinimumLength":8,"RequireUppercase":true,"RequireLowercase":true,"RequireNumbers":true,"RequireSymbols":false}}' \
    --auto-verified-attributes "email" \
    --schema '[
        {"Name":"email","Required":true,"Mutable":true},
        {"Name":"given_name","Required":true,"Mutable":true},
        {"Name":"family_name","Required":true,"Mutable":true}
    ]' \
    --username-attributes "email" \
    --mfa-configuration "OFF" \
    --account-recovery-setting '{"RecoveryMechanisms":[{"Priority":1,"Name":"verified_email"}]}' \
    --region "${REGION}" \
    --query "UserPool.Id" \
    --output text)

if [ -z "$USER_POOL_ID" ]; then
    echo -e "${BOLD}${RED}Error: Failed to create user pool.${RESET}"
    exit 1
fi

echo -e "${GREEN}User Pool created successfully!${RESET}"
echo -e "User Pool ID: ${BOLD}${USER_POOL_ID}${RESET}"

echo -e "${BOLD}Step 3:${RESET} Creating App Client..."
APP_CLIENT_ID=$(aws $PROFILE_ARG cognito-idp create-user-pool-client \
    --user-pool-id "${USER_POOL_ID}" \
    --client-name "${CLIENT_NAME}" \
    --no-generate-secret \
    --explicit-auth-flows "ALLOW_USER_PASSWORD_AUTH" "ALLOW_REFRESH_TOKEN_AUTH" \
    --prevent-user-existence-errors "ENABLED" \
    --refresh-token-validity 30 \
    --access-token-validity 60 \
    --id-token-validity 60 \
    --token-validity-units '{"RefreshToken":"DAYS","AccessToken":"MINUTES","IdToken":"MINUTES"}' \
    --region "${REGION}" \
    --query "UserPoolClient.ClientId" \
    --output text)

if [ -z "$APP_CLIENT_ID" ]; then
    echo -e "${BOLD}${RED}Error: Failed to create app client.${RESET}"
    exit 1
fi

echo -e "${GREEN}App Client created successfully!${RESET}"
echo -e "App Client ID: ${BOLD}${APP_CLIENT_ID}${RESET}"

# Create a config file
echo -e "${BOLD}Step 4:${RESET} Creating AWS configuration file..."

mkdir -p ../frontend/src

cat > ../frontend/src/aws-config.ts << EOF
// AWS Configuration for SJU-AI-Tutor
// Generated on $(date)

export const awsConfig = {
  Auth: {
    region: '${REGION}',
    userPoolId: '${USER_POOL_ID}',
    userPoolWebClientId: '${APP_CLIENT_ID}',
    authenticationFlowType: 'USER_PASSWORD_AUTH'
  }
};
EOF

echo -e "${GREEN}AWS Configuration file created at: ${BOLD}frontend/src/aws-config.ts${RESET}"

# Create a test user
echo -e "${BOLD}Step 5:${RESET} Creating a test user..."
TEST_EMAIL="test@example.com"
TEST_PASS="Test123456!"

# Create test user
aws $PROFILE_ARG cognito-idp admin-create-user \
    --user-pool-id "${USER_POOL_ID}" \
    --username "${TEST_EMAIL}" \
    --temporary-password "${TEST_PASS}" \
    --user-attributes Name=email,Value="${TEST_EMAIL}" Name=email_verified,Value=true Name=given_name,Value=Test Name=family_name,Value=User \
    --region "${REGION}" > /dev/null

# Set permanent password
aws $PROFILE_ARG cognito-idp admin-set-user-password \
    --user-pool-id "${USER_POOL_ID}" \
    --username "${TEST_EMAIL}" \
    --password "${TEST_PASS}" \
    --permanent \
    --region "${REGION}"

echo -e "${GREEN}Test user created successfully!${RESET}"
echo -e "Email: ${BOLD}${TEST_EMAIL}${RESET}"
echo -e "Password: ${BOLD}${TEST_PASS}${RESET}"

# Summary
echo -e "\n${BOLD}${BLUE}=== Setup Complete ===${RESET}"
echo -e "${BOLD}User Pool ID:${RESET} ${USER_POOL_ID}"
echo -e "${BOLD}App Client ID:${RESET} ${APP_CLIENT_ID}"
echo -e "${BOLD}Region:${RESET} ${REGION}"
echo -e "${BOLD}Test User:${RESET} ${TEST_EMAIL} / ${TEST_PASS}"
echo
echo -e "${YELLOW}Next Steps:${RESET}"
echo -e "1. Import AWS Amplify in your frontend:"
echo -e "   ${BOLD}npm install aws-amplify${RESET}"
echo
echo -e "2. Initialize Amplify in your main.tsx:"
echo -e "   ${BOLD}import { Amplify } from 'aws-amplify';${RESET}"
echo -e "   ${BOLD}import { awsConfig } from './aws-config';${RESET}"
echo -e "   ${BOLD}Amplify.configure(awsConfig);${RESET}"
echo
echo -e "3. Update authService.ts to use Amplify Auth methods"
echo
echo -e "${GREEN}Your Cognito setup is now complete and ready to use!${RESET}"