
FROM python:3.9-slim


ENV ACCEPT_EULA=Y


RUN apt-get update -y && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    gnupg \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends --allow-unauthenticated \
    msodbcsql17 \
    mssql-tools \
    && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile \
    && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc \
    && apt-get clean


WORKDIR /app


COPY . .


RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install pyodbc


EXPOSE 8000


CMD ["python", "app.py"]
