FROM python:3.10.7-bullseye


COPY requirements.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh

ENTRYPOINT ["moods-dna.py"]
CMD [""]
