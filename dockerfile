FROM python:3.12-slim

WORKDIR /app

RUN groupadd -r app-group && useradd -r -g app-group app-user

RUN chown -R app-user:app-group /app

COPY . .

RUN python -m pip install --upgrade pip
# (add --no-cache-dir if no caching)
RUN pip install -r requirements.txt

RUN mkdir -p /app/logs && chown -R app-user:app-group /app/logs
RUN mkdir -p /app/reports && chown -R app-user:app-group /app/reports

USER app-user

ENV PYTHONUNBUFFERED=1
ENV TIMEZONE=Etc/UTC
ENV CONTAINER_MODE=True

# default command to run app (can be overridden)
CMD ["python", "app.py"]