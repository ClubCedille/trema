# Light based python image 
FROM cicirello/pyaction:4.14.0

# Work in /app for the application from container
WORKDIR /app
# Copy actual directory in /app
COPY . .

# run necessary command to install all modules
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/Pycord-Development/pycord
# run trema
CMD python -u trema.py