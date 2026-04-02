# Web Store Front UI
A web front end for e-commerce application. Built using React, MUI.

## Prerequisites
- Node > 18
- Git

## Install Dependencies
Install required node modules.

`npm install`

### Run App Locally
`npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### Run Tests
`npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### Production Build
 `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

### Build Docker Image

Tell Docker CLI to talk to minikube's VM.

For MacOS,
`eval $(minikube docker-env)`

For Windows,
`& minikube -p minikube docker-env --shell powershell | Invoke-Expression`

Build docker image,
```bash
gcloud auth login
gcloud auth print-access-token \
  --impersonate-service-account="$IMPERSONATE_SA" \
  | docker login -u oauth2accesstoken --password-stdin https://us-central1-docker.pkg.dev

docker buildx build --platform linux/amd64 -t $REPO_URL/store-ui:1 store-ui
```
