# Project Setup Guide

---

## 🔧 Preliminary Setup

```bash
pip3 install -r requirements.txt
```

## 🗄️ MongoDB Setup
1. Create an Account
2. Check your email for a MongoDB invite.
3. Accept the invite and create your account.
4. If you're prompted that a user already exists, click Continue.
5. Select the "Get connection string" option.
6. Choose Python as the driver, install the driver via the command line, and copy the full URI provided in Step 3.

## Configure Environment Variables
1. In the /backend folder, make a copy of .env.template and rename it to .env.
2. Add your Gemini API key and MongoDB URI to the .env file.

## 🔐 Google OAuth Setup
1. Go to (Google Cloud Console)[https://console.developers.google.com/].
2. Click the top-left dropdown to create a new project, then select it.
3. Navigate to Credentials (left sidebar) → Create Credentials → OAuth client ID.
4. You may be prompted to fill out the OAuth consent screen first—follow the prompts to complete it.
5. Under Application Type, choose Chrome Extension.
6. To get your extension’s Item ID:
Go to chrome://extensions/ -> Click Details on your extension -> Copy the ID shown at the end of the URL (after ?id=...)
7. Paste this ID into the OAuth Client creation form.
8. Once created, copy the CLIENT_ID and paste the CLIENT_ID into your /frontend/manifest.json.