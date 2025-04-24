# Installing on Digital Ocean

This guide walks you through deploying the No-Code Architects Toolkit API on Digital Ocean's App Platform.

## Prerequisites

- A Digital Ocean account ([Sign up here](https://www.digitalocean.com/))
- Basic familiarity with Digital Ocean App Platform
- A credit/debit card for billing (you'll only be charged for what you use)

## Step 1: Create a New Project

1. Sign in to your Digital Ocean account
2. Create a new project or select an existing one
3. This will organize your resources for the NCA Toolkit

## Step 2: Create a Digital Ocean Space

You'll need to create a Space (Digital Ocean's object storage) for the toolkit to store processed files:

1. Navigate to **Spaces Object Storage** in the Digital Ocean dashboard
2. Click **Create a Space**
3. Select a region (e.g., New York)
4. Give your bucket a name (e.g., `nca-toolkit-bucket`)
5. Select your project
6. Click **Create Space**

## Step 3: Generate API Keys for Your Space

1. From your new Space, go to **Settings**
2. Click **Create Access Key**
3. Select **Full Access**
4. Give your key a name (e.g., `nca-toolkit-key`)
5. Click **Create Access Key**
6. **IMPORTANT**: Save both the Access Key and Secret Key shown - you will only see them once!
7. Also copy the Space URL (endpoint) for use in the next step

## Step 4: Deploy the App

1. From your Digital Ocean dashboard, click **Create** and select **App**
2. Choose **Container Image** as the deployment source
3. Select **Docker Hub** for the repository
4. Enter `stephengpope/no-code-architects-toolkit` as the image name
5. Enter `latest` for the image tag
6. Click **Next**
7. If needed, edit the name to remove any extra dashes (Digital Ocean may show an error for long names)
8. Choose **Web Service** as the service type

## Step 5: Configure Resources

1. Select a plan with adequate resources for your needs:
   - For testing, a $50/month instance provides good performance
   - For smaller workloads, you can select a smaller instance
   - Note: You're only charged for the time the server is running
2. Set Containers to 1
3. Close the resource selection dialog

## Step 6: Configure Environment Variables

Add the following environment variables exactly as shown (be careful with underscores vs. dashes and avoid any leading/trailing spaces):

1. `API_KEY`: Your API key (e.g., `test123` for testing - change for production)
2. `S3_ENDPOINT_URL`: The URL of your Space (copied from Step 3)
3. `S3_ACCESS_KEY`: The access key from Step 3
4. `S3_SECRET_KEY`: The secret key from Step 3
5. `S3_BUCKET_NAME`: The name of your Space bucket (e.g., `nca-toolkit-bucket`)
6. `S3_REGION`: The region code of your Space (e.g., `NYC3` for New York)

## Step 7: Finalize and Deploy

1. For Deployment Region, select a region close to your location (e.g., San Francisco)
2. You can use the default app name or choose a custom name
3. Click **Create Resource**
4. Wait for the deployment to complete (this may take a few minutes)
   - You may need to refresh the page to see updates

## Step 8: Test Your Deployment

### Using Postman

1. Sign up for or log in to [Postman](https://www.postman.com/)
2. Import the [NCA Toolkit Postman Collection](https://bit.ly/49Gkh61)
3. Fork the collection to your workspace
4. Create a new environment:
   - Name it "Digital Ocean" or similar
   - Add a variable `x-api-key` with the value matching your API_KEY (e.g., `test123`)
   - Add a variable `base_url` with the value of your app's URL (shown in the Digital Ocean dashboard)
   - Save the environment
5. In the collection, navigate to the `toolkit/authenticate` endpoint and click Send
6. If you receive a success response, your deployment is working correctly
7. Then test the `toolkit/test` endpoint to verify complete functionality

## Monitoring and Management

- **Overview**: View basic information about your app
- **Insights**: Monitor CPU and memory usage
- **Runtime Logs**: View logs of API calls and server activity
- **Console**: Access the server's command line (rarely needed)
- **Settings**: Modify your app's configuration

## Next Steps

Now that you have successfully deployed the NCA Toolkit API, you can:
- Explore all the available endpoints in the Postman collection
- Integrate the API with your applications
- Consider securing your API key with a more complex value
- Scale your resources up or down based on your usage requirements

Remember, Digital Ocean charges based on usage, so you can always delete the app when you're not using it to save costs.