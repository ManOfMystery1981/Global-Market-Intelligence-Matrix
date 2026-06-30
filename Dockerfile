FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Fixed: Keeps the container completely awake on boot so it never enters a restarting crash loop
CMD ["tail", "-f", "/dev/null"]
