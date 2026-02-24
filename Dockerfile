FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY models.py .
COPY config.py .
COPY nagios_writer.py .

# Create directory for nagios.cmd (will be mounted as volume)
RUN mkdir -p /var/nagios/rw

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
