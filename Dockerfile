From tensorflow/tensorflow:latest-gpu-py3

RUN apt-get update -y && apt-get install -y git

# Create required directory in case (optional)
RUN mkdir -p $(jupyter --data-dir)/nbextensions
# Clone the repository
RUN cd $(jupyter --data-dir)/nbextensions && git clone https://github.com/lambdalisue/jupyter-vim-binding vim_binding
# Activate the extension
RUN jupyter nbextension enable vim_binding/vim_binding

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

CMD ["/run_jupyter.sh", "--allow-root"]
