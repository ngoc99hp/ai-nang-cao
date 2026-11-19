FROM ubuntu:24.04
ARG UID=1000
ARG GID=1000
ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential python3 python3-venv tmux indent git ca-certificates \
    && rm -rf /var/lib/apt/lists/*
# ubuntu:24.04 có sẵn user 'ubuntu' UID 1000 → xóa để aai dùng UID 1000 (trùng tuyendv trên host)
RUN userdel -r ubuntu 2>/dev/null || true; \
    groupadd -g ${GID} aai && useradd -m -u ${UID} -g ${GID} -s /bin/bash aai
USER aai
RUN python3 -m venv /home/aai/venv
ENV PATH=/home/aai/venv/bin:$PATH
COPY --chown=aai:aai requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
WORKDIR /home/aai/aai_misconception
