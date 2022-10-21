FROM python:3.9 as builder
RUN mkdir -p /vpsmon
WORKDIR /vpsmon
COPY pyproject.toml poetry.lock /vpsmon/
ENV POETRY_VIRTUALENVS_CREATE false
RUN pip3 install pip --upgrade && pip3 install poetry --upgrade --pre && poetry install --no-root --only main

FROM python:3.9-slim
WORKDIR /vpsmon
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY . /vpsmon
CMD ["uvicorn" ,"vpsmon.app:app", "--host", "0.0.0.0"]
