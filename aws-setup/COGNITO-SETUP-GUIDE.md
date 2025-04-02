# AWS Cognito Integration Guide

This guide provides step-by-step instructions for setting up AWS Cognito authentication with the SJU-AI-Tutor application.

## Prerequisites

1. AWS CLI installed and configured with SSO
2. Access to your AWS account through SSO
3. Node.js and npm installed

## Step 1: Log in via AWS SSO

```bash
# Replace 'your-sso-profile' with your SSO profile name
aws sso login --profile your-sso-profile
```

## Step 2: Edit the Cognito Setup Script

Edit the `create-cognito-pool-sso.sh` script to use your SSO profile.

```bash
# Open the script
nano aws-setup/create-cognito-pool-sso.sh

# Change line 9 to use your SSO profile name
AWS_PROFILE="your-sso-profile"  # Change this to your SSO profile name

# Save and exit
```

## Step 3: Run the Cognito Setup Script

```bash
# Make the script executable if needed
chmod +x aws-setup/create-cognito-pool-sso.sh

# Run the script
./aws-setup/create-cognito-pool-sso.sh
```

The script will:
- Verify your SSO credentials
- Create a Cognito User Pool
- Create an App Client
- Generate aws-config.ts with your Cognito details
- Create a test user

## Step 4: Install AWS Amplify

```bash
cd frontend
npm install aws-amplify
```

## Step 5: Enable Amplify in main.tsx

Edit `frontend/src/main.tsx` to uncomment the Amplify configuration:

```typescript
// Remove the comment slashes from these lines
import { Amplify } from 'aws-amplify';
import { awsConfig } from './aws-config';
Amplify.configure(awsConfig);
```

## Step 6: Replace authService.ts

Replace the current authentication service with the Cognito version:

```bash
# Backup the current file
mv src/services/authService.ts src/services/authService.orig.ts

# Use the Cognito version
cp src/services/authService-cognito.ts src/services/authService.ts
```

## Step 7: Test the Integration

Start the development server and test authentication:

```bash
npm run dev
```

Use the test user credentials created by the script:
- Email: test@example.com
- Password: Test123456!

Or create a new account through the signup form.

## Troubleshooting

### Token Errors
If you see token-related errors in the console, check:
- The aws-config.ts file has the correct values
- The AWS Amplify import in main.tsx is uncommented
- The user pool and app client were created successfully

### SSO Session Expired
If you get authentication errors when running the script, your SSO session may have expired:

```bash
# Log in again with SSO
aws sso login --profile your-sso-profile
```

### User Not Confirmed
If a user signs up but can't sign in because of a "UserNotConfirmedException":

```bash
# Confirm the user manually (replace values with actual values)
aws cognito-idp admin-confirm-sign-up \
  --user-pool-id YOUR_USER_POOL_ID \
  --username user@example.com \
  --profile your-sso-profile
```

## Benefits of AWS Cognito

1. **Security**: Industry-standard authentication with token management
2. **Scalability**: Handles any number of users
3. **Features**: Built-in password reset, MFA, social logins
4. **Management**: User administration through AWS Console
5. **Integration**: Works seamlessly with other AWS services

## Additional Customization

You can further customize AWS Cognito through the AWS Console:
- Email templates
- Password policies
- MFA settings
- Custom attributes
- Identity providers (Google, Facebook, etc.)

For more information, see the [AWS Cognito Documentation](https://docs.aws.amazon.com/cognito/)