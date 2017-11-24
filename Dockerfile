FROM python:3

RUN sh -c 'curl -sL https://deb.nodesource.com/setup_8.x | bash -'
RUN apt-get update
RUN apt-get install -y default-jre nodejs
# workaround for scikit-bio
RUN pip install numpy
ADD requirements.txt /usr/app/requirements.txt
WORKDIR /usr/app
RUN pip install -r requirements.txt

ADD . /usr/app
RUN wget https://github.com/aaronmck/FlashFry/releases/download/1.7/FlashFry-assembly-1.7.jar

# download data, do all preprocessing
CMD ["python", "-m", "pavooc.server.main"]
