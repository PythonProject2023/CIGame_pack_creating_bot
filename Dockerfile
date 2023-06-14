FROM python:3
WORKDIR /source
ADD ./source /source/source/
ADD Pipfile Pipfile.lock dodo.py /source

RUN pip install pipenv
RUN pipenv install --dev --system
ENV PYTHONUNBUFFERED=1

CMD ["doit", "runbot"]
