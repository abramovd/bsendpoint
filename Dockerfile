FROM python:3-alpine AS base

RUN apk update && apk add --no-cache build-base tzdata

RUN adduser -S bsendpoint

ADD requirements /bsendpoint/requirements

WORKDIR /bsendpoint

RUN pip config set global.index-url "https://pypi.python.org/simple"
RUN pip install dumb-init==1.2.2
RUN pip install -r requirements/requirements.txt

FROM base as app
ADD app /bsendpoint/app

FROM app AS release

ENV PYTHONUNBUFFERED=1 PYTHONHASHSEED=random PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

EXPOSE 8000

FROM release AS dev-base
RUN apk add --no-cache bash

FROM dev-base as test-base
RUN pip install -r requirements/test-requirements.txt --no-deps

USER bsendpoint
CMD ["uvicorn", "app.main:app", "--reload", "--host=0.0.0.0", "--port=8000"]

FROM test-base As local
USER bsendpoint
CMD ["uvicorn", "app.main:app", "--reload", "--host=0.0.0.0", "--port=8000"]

FROM release As production
USER bsendpoint
ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]
CMD ["uvicorn", "app.main:app", "--workers=2", "--host=0.0.0.0", "--port=8000"]
