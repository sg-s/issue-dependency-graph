# Container image that runs your code
FROM python:3.9

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY issue_dep_graph /issue_dep_graph

COPY setup.py /setup.py

RUN pip install -e .



COPY entrypoint.sh /entrypoint.sh

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["/entrypoint.sh"]
