FROM python:3.9-alpine

WORKDIR /diakosmisi

COPY ./src ./src
COPY ./requirments.txt .

RUN pip install -r requirments.txt

CMD ["python","src/main.py"]