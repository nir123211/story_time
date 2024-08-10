FROM pytorch/pytorch:2.3.1-cuda11.8-cudnn8-runtime

RUN sudo apt-get update
RUN sudo apt-get install -y nvidia-container-toolkit

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN conda install transformers
COPY download_model.py download_model.py
RUN python download_model.py


COPY misc misc
COPY scripts scripts
COPY streamlit_main.py streamlit_main.py

EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health


ENTRYPOINT ["streamlit", "run", "streamlit_main.py", "--server.port=8501"]

