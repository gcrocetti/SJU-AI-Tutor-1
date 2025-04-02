// AWS Configuration for SJU-AI-Tutor
// This file will be automatically updated by the Cognito setup script

export const awsConfig = {
  Auth: {
    region: 'us-east-2', // Your AWS region
    userPoolId: 'PLACEHOLDER_USER_POOL_ID', // Will be replaced by setup script
    userPoolWebClientId: 'PLACEHOLDER_APP_CLIENT_ID', // Will be replaced by setup script
    authenticationFlowType: 'USER_PASSWORD_AUTH'
  }
};