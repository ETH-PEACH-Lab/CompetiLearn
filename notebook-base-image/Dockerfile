FROM quay.io/jupyter/minimal-notebook:hub-4.1.3
USER root
ADD ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
EXPOSE 8000
EXPOSE 8888
USER ${NB_USER}
CMD ["/bin/bash","-c", "jupyterhub-singleuser"]  