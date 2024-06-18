FROM ubuntu:latest

# Install dependencies
RUN apt-get update
RUN apt-get install -y python3 python3-pip python3-venv

# Install GDAL dependencies
RUN apt-get install -y gdal-bin libgdal-dev

# Create a virtual environment
RUN python3 -m venv /var/venv
RUN /var/venv/bin/pip install --upgrade pip
RUN /var/venv/bin/pip install wheel
RUN /var/venv/bin/pip install GDAL==$(gdal-config --version | awk -F'[.]' '{print $1"."$2}')


# Install meteohub
RUN mkdir -p /var/tmp/meteohub
COPY src /var/tmp/meteohub/src
COPY setup.py /var/tmp/meteohub/
WORKDIR /var/tmp/meteohub 
RUN /var/venv/bin/pip install .
# link /var/venv/bin/meteohub to /usr/local/bin/meteohub
RUN ln -s /var/venv/bin/meteohub /usr/local/bin/meteohub
WORKDIR /var/task
RUN rm -rf /var/tmp/meteohub
