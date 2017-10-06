FROM hbpmip/python-base:0.2.0

MAINTAINER mirco.nasuti@chuv.ch

ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

COPY ehr_to_i2b2/ /ehr_to_i2b2/
COPY requirements.txt /requirements.txt

RUN pip install -r requirements.txt

VOLUME /input_folder

WORKDIR /

ENTRYPOINT ["python", "/ehr_to_i2b2/main.py", "/input_folder"]

LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="hbpmip/ehr-to-i2b2" \
      org.label-schema.description="Import EHR (electronic health record) data into an I2B2 database" \
      org.label-schema.url="https://github.com/LREN-CHUV/ehr-to-i2b2" \
      org.label-schema.vcs-type="git" \
      org.label-schema.vcs-url="https://github.com/LREN-CHUV/ehr-to-i2b2" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.version="$VERSION" \
      org.label-schema.vendor="LREN CHUV" \
      org.label-schema.license="Apache2.0" \
      org.label-schema.docker.dockerfile="Dockerfile" \
      org.label-schema.schema-version="1.0"
