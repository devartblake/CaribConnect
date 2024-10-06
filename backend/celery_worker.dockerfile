# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app/

# Copy the project file (pyproject.toml and poetry.lock if available)
COPY ./pyproject.toml ./uv.lock* /app/

# Copy the application code
COPY ./app /app/app

# Create the user inside the Dockerfile
RUN groupadd -r celery && useradd -r -g celery celeryuser && "celeryuser:carrot" | chpasswd

# Set permissions for the working directory
RUN chown -R celeryuser:celery /app/

# Switch to non-root user
USER celeryuser

# Run Celery worker with Redis
CMD ["celery", "-A", "app.worker.celery_worker", "worker", "--loglevel=info"]