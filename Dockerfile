FROM python:3

ADD . /usr/app
WORKDIR /usr/app

# workaround for scikit-bio
RUN pip install numpy
RUN pip install -r requirements.txt
RUN wget https://github.com/aaronmck/FlashFry/releases/download/1.6/FlashFry-assembly-1.6.jar
RUN apt-get update
RUN apt-get install -y default-jre

# download data, do all preprocessing
CMD ["python", "-m", "pavooc.pipeline"]
