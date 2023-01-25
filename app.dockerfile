FROM python:3.10

COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --system --deploy

RUN apt update && apt install -y coreutils
ADD app/app /app/
WORKDIR /app/
