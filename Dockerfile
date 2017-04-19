FROM hbpmip/python-base:a2b201e

MAINTAINER mirco.nasuti@chuv.ch

COPY ehr_to_i2b2/ /ehr_to_i2b2/
COPY requirements.txt /requirements.txt

RUN pip install -r requirements.txt

VOLUME /input_folder

WORKDIR /

ENTRYPOINT ["python", "/ehr_to_i2b2/main.py", "/input_folder"]
