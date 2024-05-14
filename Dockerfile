FROM python:3.12-slim
WORKDIR /target-rifle-scores
COPY ./requirements.txt /target-rifle-scores/
RUN pip3 install --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
#Production Server
# '-w' is the number of workers, set to 4* cores available
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000", "-w", "4"]
#Dev Server
#ENV FLASK_APP=app.py
#CMD ["flask", "run", "--host", "127.0.0.1"]