import os
import boto3
from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from flask_mail import Mail, Message
from dotenv import load_dotenv
import json
import logging
from logging.handlers import TimedRotatingFileHandler

app = Flask(__name__)

# Logging setup
log_dir = "./"
log_file = os.path.join(log_dir, "app.log")

if not os.path.exists(log_dir):
    os.makedirs(log_dir)


handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=0)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

load_dotenv()  # load environment variables from .env file

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Email sender dari environment variable
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Password dari environment variable
mail = Mail(app)

S3_BUCKET = os.getenv('S3_BUCKET')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')  # Tambahkan token sesi
AWS_REGION = os.getenv('AWS_REGION')
# Load prohibited words from the environment variables
PROHIBITED_WORDS = os.getenv("PROHIBITED_WORDS", "").split(",")


# Initialize S3 client with session token
s3_client = boto3.client(
    's3',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN  # Masukkan token sesi
)


def connect_db():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hobi')
def hobi():
    return render_template('hobi.html')

@app.route('/pekerjaan')
def pekerjaan():
    return render_template('pekerjaan.html')

@app.route('/kontak', methods=['GET', 'POST'])
def kontak():

    # Define global variable warning
    warning=""

    if request.method == 'POST':
        nama = request.form['nama']
        email = request.form['email']
        isi_pesan = request.form['isi_pesan']

        # Check if the message contains prohibited words
        if any(word in isi_pesan.lower() for word in PROHIBITED_WORDS):
            # Log the message but do not send an email
            app.logger.warning(f"Blocked message from {nama} ({email}): {isi_pesan}")
            warning="Pesan Anda mengandung kata terlarang dan tidak dapat diproses."

        else:
            # Store message in S3
            pesan_data = {
                'nama': nama,
                'email': email,
                'isi_pesan': isi_pesan
            }
            pesan_json = json.dumps(pesan_data)
            file_name = f"pesan_{nama}_{email}.json"
            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=file_name,
                Body=pesan_json,
                ContentType='application/json'
            )

            # Send email response
            msg = Message('Pesan Baru dari Kontak', sender='azzuriptr@gmail.com', recipients=[email])
            msg.body = f"Nama: {nama}\nEmail: {email}\nPesan: {'Terimakasih sudah submit pesanmu :) Nanti kubaca deh wkwk'}"
            mail.send(msg)

            # Log the successful message
            app.logger.info(f"Message from {nama} ({email}) stored and email sent: {isi_pesan}")

            # Provide a success message
            warning="Pesan Anda telah berhasil dikirim"

    # Get message from AWS S3 and append to pesan_list
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET)
    pesan_list = []

    for obj in response.get('Contents', []):
        file = s3_client.get_object(Bucket=S3_BUCKET, Key=obj['Key'])
        pesan_json = file['Body'].read().decode('utf-8')
        pesan_data = json.loads(pesan_json)
        pesan_list.append(pesan_data)

    return render_template('kontak.html', pesan_list=pesan_list, warning=warning)


@app.route('/pendidikan')
def pendidikan():
    return render_template('pendidikan.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
