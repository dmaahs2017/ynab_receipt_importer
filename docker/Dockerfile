FROM public.ecr.aws/lambda/python:3.11

WORKDIR /app

# Install system dependencies
RUN rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN yum update -y && \
    yum update -y python3 curl libcom_err ncurses expat libblkid libuuid libmount && \
    yum install ffmpeg libsm6 libxext6 python3-pip git -y && \
    yum clean all

RUN yum install tesseract -y && \
    yum clean all

# Install Python dependencies
RUN pip3 install --no-cache-dir --target "${LAMBDA_TASK_ROOT}" \
    pillow \
    pytesseract \
    requests \
    openai

ARG DEBIAN_FRONTEND=noninteractive
ENV LAMBDA=True

COPY main.py ${LAMBDA_TASK_ROOT}/lambda_function.py

CMD ["lambda_function.lambda_handler"]