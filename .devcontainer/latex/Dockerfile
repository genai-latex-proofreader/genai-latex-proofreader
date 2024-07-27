FROM ubuntu:24.04

USER root

# --- Ubuntu setup with basic tools ---

ENV DEBIAN_FRONTEND "noninteractive"
RUN apt-get -qq -y update && \
        apt-get -qq -y upgrade && \
        apt-get install -qq -y --no-install-recommends \
        make \
        jq \
        git \
        curl \
        entr

# --- Install Latex ---

# As of 5/2023 Arxiv is using TexLive 2023
# https://blog.arxiv.org/2023/05/12/tex-live-2023-upgrade-to-occur-may-22nd-2023/
#
# A comparison of docker/VSCode environments:
# https://towardsdatascience.com/three-ways-to-create-dockernized-latex-environment-2534163ee0c4

# v---
# The below install instructions are based on the following sources:
#
#   https://tug.org/texlive/quickinstall.html
#
# See also for references on installation of perl-dependencies:
#
#   https://github.com/qdm12/latexdevcontainer/blob/master/Dockerfile#L37 (MIT licensed)
#   https://github.com/alexwlchan/tex-dockerfile/blob/development/Dockerfile#L18 (MIT licensed)
RUN apt-get install -qq -y --no-install-recommends \
        wget \
        openssl \
        ca-certificates \
        cpanminus

RUN cd /tmp && \
        wget --quiet https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz && \
        zcat < install-tl-unx.tar.gz | tar xf - && \
        TEXLIVE_YEAR=$(date +%Y) && \
        cd install-tl-${TEXLIVE_YEAR}* && \
        export TEXLIVE_INSTALL_NO_CONTEXT_CACHE=1 && \
        export TEXLIVE_INSTALL_NO_WELCOME=1 && \
        perl ./install-tl \
        --no-interaction \
        --scheme=basic

# Ensure this works both on x64 (on eg Github runners) and Mac M1/M2 hardware
ENV PATH=${PATH}:/usr/local/texlive/2024/bin/x86_64-linux/
ENV PATH=${PATH}:/usr/local/texlive/2024/bin/aarch64-linux/

# # ^---

# Install any Latex packages that are needed
#
#  - https://ctan.org/pkg/mathrsfs?lang=en
#  - https://ctan.org/pkg/tikz-cd
#  - https://www.ctan.org/pkg/pgf
RUN tlmgr install collection-fontsrecommended   # installs rsfs
RUN tlmgr install jknapltx stmaryrd             # is jknapltx needed?
RUN tlmgr install tensor tikz-cd pgf float changepage

# --- Install Python for checking the paper/results with LLM ---
RUN apt-get install -qq -y --no-install-recommends \
        python3 \
        gcc \
        python3-dev \
        python3-pip

COPY requirements.txt /dev-setup/
# RUN pip install --upgrade pip==23.1.2 && \
RUN pip install --break-system-packages \
        -r /dev-setup/requirements.txt

# Set location of __cache__ directories
ENV PYTHONPYCACHEPREFIX=/dev-setup/.cache/python
