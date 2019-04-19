FROM ubuntu:18.04

ENV VIRTUAL_ENV=/opt/venv APP_PORT=3000 FLASK_APP=main.py

RUN apt-get update && apt-get install \
  -y --no-install-recommends python3 python3-virtualenv

RUN python3 -m virtualenv --python=/usr/bin/python3 ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

# Install dependencies:
ADD requirements.txt .
RUN pip install -r requirements.txt

# Run the application:
ADD main.py .
ADD lru.py .

HEALTHCHECK --interval=5m --timeout=3s \
	CMD curl -f http://localhost:${APP_PORT} || exit 1

EXPOSE ${APP_PORT}

ENTRYPOINT ["python", "main.py"]

