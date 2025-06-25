#!/bin/bash
# AWS Cognito User Pool Creation Script for SJU-AI-Tutor
# This script creates a Cognito user pool and app client configured for the SJU-AI-Tutor application

# Set variables
USER_POOL_NAME="sju-ai-tutor-users"
CLIENT_NAME="sju-ai-tutor-web-client"
REGION="us-east-2"  # Change this to your preferred region
AWS_PROFILE="default" # Change this to your SSO profile name if needed (e.g., "sju-dev")

# Text styling
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RESET="\033[0m"

echo -e "${BOLD}${BLUE}=== Setting up Cognito User Pool for SJU-AI-Tutor ===${RESET}"
echo -e "${YELLOW}Region: ${REGION}${RESET}"
echo -e "${YELLOW}User Pool Name: ${USER_POOL_NAME}${RESET}"
echo -e "${YELLOW}App Client Name: ${CLIENT_NAME}${RESET}"
echo -e ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${BOLD}Error: AWS CLI is not installed.${RESET}"
    echo "Please install the AWS CLI using the instructions at:"
    echo "https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check if AWS CLI is configured
aws configure get aws_access_key_id &> /dev/null
if [ $? -ne 0 ]; then
    echo -e "${BOLD}Error: AWS CLI is not configured.${RESET}"
    echo "Please run 'aws configure' to set up your access key, secret key, and region."
    exit 1
fi

echo -e "${BOLD}Step 1:${RESET} Creating Cognito User Pool..."
USER_POOL_ID=$(aws cognito-idp create-user-pool \
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
    echo -e "${BOLD}Error: Failed to create user pool.${RESET}"
    exit 1
fi

echo -e "${GREEN}User Pool created successfully!${RESET}"
echo -e "User Pool ID: ${BOLD}${USER_POOL_ID}${RESET}"

echo -e "${BOLD}Step 2:${RESET} Creating App Client..."
APP_CLIENT_ID=$(aws cognito-idp create-user-pool-client \
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
    echo -e "${BOLD}Error: Failed to create app client.${RESET}"
    exit 1
fi

echo -e "${GREEN}App Client created successfully!${RESET}"
echo -e "App Client ID: ${BOLD}${APP_CLIENT_ID}${RESET}"

# Create a config file
echo -e "${BOLD}Step 3:${RESET} Creating AWS configuration file..."

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
echo -e "${BOLD}Step 4:${RESET} Creating a test user..."
TEST_EMAIL="test@example.com"
TEST_PASS="Test123456!"

# Create test user
aws cognito-idp admin-create-user \
    --user-pool-id "${USER_POOL_ID}" \
    --username "${TEST_EMAIL}" \
    --temporary-password "${TEST_PASS}" \
    --user-attributes Name=email,Value="${TEST_EMAIL}" Name=email_verified,Value=true Name=given_name,Value=Test Name=family_name,Value=User \
    --region "${REGION}" > /dev/null

# Set permanent password
aws cognito-idp admin-set-user-password \
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