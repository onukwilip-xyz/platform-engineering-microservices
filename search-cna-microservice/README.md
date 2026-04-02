# Products Cloud Native Microservice

## Prerequisites

### Node 18
For Windows
```bsh
choco install node
```
For MacOS
```bsh
brew install node
```


```bsh
source .env.local
```

## Build
```bsh
npm install
npm install -g nodemon
```

## Run Locally
```bsh
npm start
```

## Build Docker Image

Tell Docker CLI to talk to minikube's VM.

For MacOS,
`eval $(minikube docker-env)`
For Windows,
`& minikube -p minikube docker-env --shell powershell | Invoke-Expression`

Build docker image,
```bash
REPO_URL=us-central1-docker.pkg.dev/pe-staging-project-131b/images
IMPERSONATE_SA=tf-platform@pe-terraform-project.iam.gserviceaccount.com

gcloud auth login
gcloud auth print-access-token \
  --impersonate-service-account="$IMPERSONATE_SA" \
  | docker login -u oauth2accesstoken --password-stdin https://us-central1-docker.pkg.dev

docker buildx build --platform linux/amd64 -t $REPO_URL/search:1 search-cna-microservice
```