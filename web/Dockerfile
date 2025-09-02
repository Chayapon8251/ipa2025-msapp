FROM python

WORKDIR /app
COPY requirements.txt .
RUN pip install flask
RUN pip install pymongo
# RUN pip install --no-cache-dir -r requirements.txt

# COPY  ./static /home/ubuntu/Desktop/IPAMSAPP/static/

COPY  . /app

EXPOSE 8080
CMD ["python", "app.py"]

