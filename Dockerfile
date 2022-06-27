FROM golang:1.18

RUN apt update && apt install git python3-pip -y

WORKDIR /code

COPY . /code

RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]
