FROM cicirello/pyaction:4.14.0

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt
RUN pip install git+https://github.com/Pycord-Development/pycord

CMD python -u main.py