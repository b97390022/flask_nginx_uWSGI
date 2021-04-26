# FROM python:alpine
# Use the Python3.7.2 image
# 指定一個 image 來源
FROM python:3.7.2-stretch

# Set the working directory to /app
WORKDIR /flask

# Copy the current directory contents into the container at /app 
# ADD：將檔案加到 images 內
ADD . /flask

# 設定環境變數

ENV MAIL_USERNAME=r01442018@g.ntu.edu.tw
ENV MAIL_PASSWORD=Ff574E0D2J8L
ENV NLTK_DATA=/root/nltk_data

# Install the dependencies
# build 時使用，會執行此命令
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python app/nltk_download.py
RUN apt-get update && apt-get install -y curl tree iputils-ping

# run the command to start uWSGI
# run container 時要執行的命令
CMD ["uwsgi", "app.ini"]
