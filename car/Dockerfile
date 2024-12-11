FROM python:3.13-alpine AS build
WORKDIR /tmp/deployment
COPY ./auth-library/dist/jwt_auth-1.0.0-py3-none-any.whl .

RUN pip3 install \
    --target . \
    redis \
    pyjwt \
    sqlalchemy \
    asyncpg \
    bcrypt \
    greenlet \
    jwt_auth-1.0.0-py3-none-any.whl \
    "fastapi[standard]"

FROM python:3.13-alpine AS runner
WORKDIR /application
COPY ./auth/src .
COPY --from=build /tmp/deployment/bin /usr/local/bin
COPY --from=build /tmp/deployment/ /usr/local/lib/python3.13
ENV PYTHONPATH='/application'
RUN chmod +x /application/entrypoint.sh

ENTRYPOINT ["/application/entrypoint.sh"]