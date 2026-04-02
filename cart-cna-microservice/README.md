# Shopping Cart Cloud Native Microservice

## Prerequisites

### Java 17
Install OpenJDK by executing following instructions,

For Windows
```bsh
choco install openjdk@18
```
For MacOS
```bsh
brew install openjdk@18
```

## Build
Set Redis server environment variables in '.env' file. This file will not checked into Git as it holds sensitive information such as Redis password.
```bsh
export $(cat .env | xargs)
gradle build
```


## Run Locally
gradle bootRun


### Build Docker Image

Tell Docker CLI to talk to minikube's VM.

For MacOS,
`eval $(minikube docker-env)`

For Windows,
`& minikube -p minikube docker-env --shell powershell | Invoke-Expression`

Build docker image,
```bash
REPO_URL=us-central1-docker.pkg.dev/pe-staging-project-131b/images
IMPERSONATE_SA=tf-platform@pe-terraform-project.iam.gserviceaccount.com

docker buildx build --platform linux/amd64 -t $REPO_URL/cart:1 cart-cna-microservice

gcloud auth login
gcloud auth print-access-token \
  --impersonate-service-account=$IMPERSONATE_SA \
  | docker login -u oauth2accesstoken --password-stdin https://us-central1-docker.pkg.dev

docker push $REPO_URL/cart:1
```

