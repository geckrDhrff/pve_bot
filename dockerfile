FROM python:3.11.6-alpine3.18

# 设置 python 环境变量
ENV PYTHONUNBUFFERED 1
ENV http_proxy http://192.168.124.25:7890
ENV https_proxy http://192.168.124.25:7890
# 设置清华源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

#下载项目
RUN apk add git
RUN git clone -b v2 https://github.com/geckrDhrff/pve_bot.git

WORKDIR pve_bot

RUN	git checkout v2
RUN python3 -m venv venv \
    && source venv/bin/activate \
    && pip install -r requirements.txt

#获取环境变量
ENV PVE_IP ${PVE_IP}
ENV PVE_TOKEN_NAME ${PVE_TOKEN_NAME}
ENV PVE_TOKEN_VALUE ${PVE_TOKEN_VALUE}
ENV BOT_TOKEN ${BOT_TOKEN}
EXPOSE ${PVE_IP}
EXPOSE ${PVE_TOKEN_NAME}
EXPOSE ${PVE_TOKEN_VALUE}
EXPOSE ${BOT_TOKEN}

#启动
CMD source venv/bin/activate && python bot.py



