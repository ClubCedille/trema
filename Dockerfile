# Light based python image 
FROM python:3.9-alpine

# Work in /app for the application from container
WORKDIR /app
# Copy actual directory in /app
COPY . .

# Read token from argument
ARG token
# Define an environnement Variable
ENV JETON=${token}

# run necessary command to install all modules
RUN pip install -r requirements.txt

# run trema
CMD ["python","trema.py","-j", "$JETON"]