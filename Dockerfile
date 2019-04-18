FROM ubuntu:18.04

ENV VIRTUAL_ENV=/opt/venv APP_PORT=3000

RUN apt-get update && apt-get install \
  -y --no-install-recommends python3 python3-virtualenv

RUN python3 -m virtualenv --python=/usr/bin/python3 ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

# Install dependencies:
ADD requirements.txt .
RUN pip install -r requirements.txt

# Run the application:
ADD main.py .

EXPOSE ${APP_PORT}

ENTRYPOINT ["python", "main.py"]
