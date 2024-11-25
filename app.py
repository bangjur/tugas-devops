import os
import boto3
from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from flask_mail import Mail, Message
from dotenv import load_dotenv
import json

load_dotenv()  # load environment variables from .env file

app = Flask(__name__)

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Email sender dari environment variable
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Password dari environment variable
mail = Mail(app)

S3_BUCKET = 'tugas-devops'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')  # Tambahkan token sesi
AWS_REGION = os.getenv('AWS_REGION')

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
    if request.method == 'POST':
        nama = request.form['nama']
        email = request.form['email']
        isi_pesan = request.form['isi_pesan']

        # Prepare message data as a dictionary
        pesan_data = {
            'nama': nama,
            'email': email,
            'isi_pesan': isi_pesan
        }

        # Convert message data to JSON
        pesan_json = json.dumps(pesan_data)

        # Upload JSON data as an object in S3
        file_name = f"pesan_{nama}_{email}.json"  # Unique file name for each message
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

    # Retrieve data from S3 to display in the table
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET)
    pesan_list = []
    for obj in response.get('Contents', []):
        # Retrieve object content from S3
        file = s3_client.get_object(Bucket=S3_BUCKET, Key=obj['Key'])
        pesan_json = file['Body'].read().decode('utf-8')  # Decode content as string
        pesan_data = json.loads(pesan_json)  # Convert JSON string to dictionary
        pesan_list.append(pesan_data)

    return render_template('kontak.html', pesan_list=pesan_list)


@app.route('/pendidikan')
def pendidikan():
    return render_template('pendidikan.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
