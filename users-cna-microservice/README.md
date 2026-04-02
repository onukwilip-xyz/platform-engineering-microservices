# User Profile Microservice

## Pre-requisites
You must have following software on your machine,
- Python 3.x or beyond
- pipenv package installed

## Setup (Local)
Installa python packages referred in application.
```
pipenv install
```
Activates virualenv.
```
pipenv shell
```

## Run Application
Start applciation locally
```
python app.py
```

```bash
gcloud auth login
gcloud auth print-access-token \
  --impersonate-service-account="$IMPERSONATE_SA" \
  | docker login -u oauth2accesstoken --password-stdin https://us-central1-docker.pkg.dev

docker buildx build --platform linux/amd64 -t $REPO_URL/users:1 users-cna-microservice
```