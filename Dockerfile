FROM harbor.hgj.net/library/yunlsp-python3.10.10-chrome:1.2

ARG SERVICE_NAME
ARG BUILD_ENV
# 服务名称
ENV APP_NAME $SERVICE_NAME
# 当前运行环境
ENV SERVER_ENV $BUILD_ENV

ADD .  $APP_NAME

RUN pip3 install -r $APP_NAME/requirements.txt && mkdir $APP_NAME/logs

WORKDIR /$APP_NAME

EXPOSE 8090 8090

CMD ["/bin/bash", "-c", "set -e && gunicorn main:app"]


