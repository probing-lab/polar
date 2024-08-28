FROM python:latest
WORKDIR /polar
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "polar.py"]
