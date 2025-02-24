# Use an official Python base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the application files to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the FastAPI port
EXPOSE 7777

# Command to run FastAPI with Uvicorn
CMD ["uvicorn", "qrcreation:app", "--host", "0.0.0.0", "--port", "7777"]
