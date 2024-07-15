FROM quay.io/jupyter/minimal-notebook:hub-4.1.3
USER root
ADD ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
COPY ./data /home/jovyan/work/competilearn/
RUN chmod -R 777 /home/jovyan/work/competilearn/
WORKDIR /home/jovyan/work
USER jovyan
EXPOSE 8000
EXPOSE 8888
CMD ["/bin/bash","-c", "jupyterhub-singleuser"]  