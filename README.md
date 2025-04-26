# Ctrl++

## Run Google Extension

1. Navigate to frontend folder.

```bash
  cd frontend
```

2. Install npm packages.

```bash
  npm install
```

3. Build the extension. This should create an out folder.

```bash
  npm run build
```

4. Go to Google Chrome and navigate to `Manage Extensions`.
5. At the top right corner, turn on `Developer Mode`.
6. At the top left corner, click on `Load unpacked`.
7. Select the out folder that was built at step 3. This should add the extension to your Google Chrome.
8. To load new changes, run the build command at step 3. Then, click the reload icon on the extension in `Manage Extensions`.
