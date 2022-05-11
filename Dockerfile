FROM python:3.7-stretch

RUN python3 --version
RUN pip3 --version

WORKDIR /usr/src/demandsensing

COPY . .

RUN pip install --no-cache-dir -r requirements.txt