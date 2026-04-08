# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environmental variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port (Cloud Run uses PORT env var)
EXPOSE 8080

# Command to run the application
# Configure streamlit to listen on port 8080
CMD ["sh", "-c", "streamlit run app.py --server.port ${PORT:-8080} --server.address 0.0.0.0 --server.headless true"]
