FROM public.ecr.aws/lambda/python:3.12

RUN microdnf install -y file file-libs && microdnf clean all

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["main.main"]

