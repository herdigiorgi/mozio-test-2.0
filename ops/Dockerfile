FROM python:3.7
RUN mkdir /code
WORKDIR /code
RUN apt-get update && \
    apt-get install -y binutils libproj-dev gdal-bin
RUN pip install pipenv
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --deploy --system

CMD bash -c "python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8080"