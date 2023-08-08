FROM python:3.9

LABEL name="wt-wxpush" auth="gwt"

WORKDIR /app

COPY . /app

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

CMD [ "python", "main.py" ]

RUN echo 'wt-wxpusher build successfuly...'