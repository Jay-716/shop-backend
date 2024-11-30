FROM python:3.11

WORKDIR /code

RUN echo "deb https://mirrors.bfsu.edu.cn/debian/ bookworm main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
    echo "deb https://mirrors.bfsu.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.bfsu.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.bfsu.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list

RUN apt-get update && \
    apt-get install -y net-tools inetutils-ping iproute2 netcat-openbsd tcpdump vim nano

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt -i https://mirrors.ustc.edu.cn/pypi/web/simple

RUN mkdir -p /var/log/gunicorn

EXPOSE 8000

COPY ./ /code/

RUN chmod +x /code/docker-entrypoint.sh

ENTRYPOINT ["/code/docker-entrypoint.sh"]

CMD ["uvicorn", "--workers", "4", "--host", "0.0.0.0", "--port", "8000", "--log-config=log.yaml", "app:app"]

