# Menggunakan image resmi Python sebagai base image
FROM python:3.12-slim

# Set direktori kerja di dalam container
WORKDIR /app

# Menyalin file requirements.txt ke dalam container
COPY requirements.txt /app/

# Install dependencies dari requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh kode Python ke dalam container
COPY . /app/

# Menjalankan bot
CMD ["python", "bot.py"]

