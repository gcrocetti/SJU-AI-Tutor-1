# Setting Up CORS for AWS API Gateway

This document provides instructions for properly configuring CORS (Cross-Origin Resource Sharing) on your AWS API Gateway to work with the frontend application.

## The Problem

You're currently seeing a CORS error that looks like this:

```
Access to fetch at 'https://rvqkmofwv7.execute-api.us-east-2.amazonaws.com/dev/signin' from origin 'http://localhost:3000' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

This occurs because the browser enforces security restrictions that prevent a web page from making requests to a different domain than the one that served the web page, unless the server explicitly allows it.

## Solution: Configure CORS in API Gateway

1. **Log in to the AWS Management Console**

2. **Navigate to API Gateway**
   - Search for "API Gateway" in the services search box

3. **Select Your API**
   - Find and click on the API with ID `rvqkmofwv7`

4. **Enable CORS for the API**
   - In the left navigation panel, click on **Resources**
   - Click the **Actions** dropdown button
   - Select **Enable CORS**

5. **Configure CORS settings**
   - Set **Access-Control-Allow-Origin** to `http://localhost:3000` for development, and your production domain for production
   - Set **Access-Control-Allow-Headers** to include at minimum `Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token`
   - Set **Access-Control-Allow-Methods** to include at minimum `POST,GET,OPTIONS`
   - Check **Access-Control-Allow-Credentials** if your API needs to support credentials

6. **Deploy the API**
   - After saving the CORS configuration, you'll need to redeploy your API
   - Click the **Actions** dropdown again
   - Select **Deploy API**
   - Choose a deployment stage (e.g., `dev`)
   - Add a deployment description (e.g., "Enabled CORS")
   - Click **Deploy**

## Using Environment-Specific URLs

To support both development and production environments, you can modify the API endpoints to use environment variables in your frontend application:

1. **Create `.env.development` file**
   ```
   VITE_API_BASE_URL=https://rvqkmofwv7.execute-api.us-east-2.amazonaws.com/dev
   ```

2. **Create `.env.production` file**
   ```
   VITE_API_BASE_URL=https://rvqkmofwv7.execute-api.us-east-2.amazonaws.com/prod
   ```

3. **Update `authService.ts` to use these environment variables**
   ```typescript
   const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
   private readonly SIGNUP_ENDPOINT = `${API_BASE_URL}/signup`;
   private readonly SIGNIN_ENDPOINT = `${API_BASE_URL}/signin`;
   ```

## Testing CORS Configuration

Once CORS is configured, you can:

1. Set `USE_MOCK_AUTH = false` and `USE_CORS_PROXY = false` in `authService.ts`
2. Restart your development server
3. Try logging in with a test account

## Additional Resources

- [AWS API Gateway CORS Documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors.html)
- [MDN CORS Documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)