FROM python:3.9
ADD ampla.py .
# ADD pins_def.py .
ADD PUSA.py .
RUN pip install requests xlwt
RUN pip install requests pysimplegui

CMD [ "python","./PUSA.py" ]