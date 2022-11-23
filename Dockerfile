FROM python:3.8.2-alpine

RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app/

# Install native libraries, required for numpy
RUN apk --no-cache add musl-dev linux-headers g++

RUN pip install --upgrade pip

RUN pip install -r requirements.txt
ADD . /app/

ENTRYPOINT ["python"]
CMD ["application.py"]
