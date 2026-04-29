# FROM python:3.10.5-alpine3.16
FROM python:3.11-alpine

RUN apk add --no-cache build-base libffi-dev openssl-dev postgresql-dev \
    && pip install --no-cache-dir pipenv

WORKDIR /usr/src/app

# Install deps from the lockfile against the system interpreter so we don't
# need pipenv at runtime. --deploy fails fast if Pipfile.lock is stale.
COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy --system \
    && pip uninstall -y pipenv virtualenv \
    && apk del build-base libffi-dev openssl-dev

COPY . .

RUN addgroup -S app && adduser -S app -G app && chown -R app:app /usr/src/app
USER app

EXPOSE 9090

CMD ["gunicorn", "app:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--worker-tmp-dir", "/dev/shm", \
     "--bind", "0.0.0.0:9090", \
     "--forwarded-allow-ips=*", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--timeout", "60", \
     "--keep-alive", "5", \
     "--graceful-timeout", "30"]