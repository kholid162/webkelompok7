from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pyodbc
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Konfigurasi koneksi ke SQL Server menggunakan SQLAlchemy
server = 'kholid-server.database.windows.net'
database = 'webprofil7-db'
username = 'kholid7'
password = 'Kholid162'
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

# Konfigurasi SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc:///?odbc_connect=' + connection_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Menonaktifkan fitur modifikasi otomatis
db = SQLAlchemy(app)

# Configuration for file uploads
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Definisi model untuk tabel tbl_anggota
class Anggota(db.Model):
    __tablename__ = 'tbl_anggota'
    id_anggota = db.Column(db.Integer, primary_key=True, server_default="0", nullable=False)
    nama = db.Column(db.String(255))
    kelas = db.Column(db.String(255))
    jabatan = db.Column(db.String(255))
    foto_profil = db.Column(db.String(255))  # Ensure this line is present


# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route untuk halaman utama
@app.route('/')
def home():
    return render_template('index.html')

# Route untuk menampilkan dan menambah data anggota
@app.route('/data_anggota', methods=['GET', 'POST'])
def dataa():
    try:
        # Menggunakan SQLAlchemy untuk mengambil data dari tabel
        # Selecting specific columns: id_anggota, nama, kelas, jabatan
        data = db.session.query(Anggota.id_anggota, Anggota.nama, Anggota.kelas, Anggota.jabatan).all()
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('data_anggota.html', tbl_anggota=data)

# Route untuk menambah data anggota
# Route untuk menambah data anggota
@app.route('/tambahanggota', methods=['GET', 'POST'])
def tambah():
    if request.method == 'POST':
        try:
            # Extract data from the form
            id_anggota = request.form['id_anggota']
            nama = request.form['nama']
            kelas = request.form['kelas']
            jabatan = request.form['jabatan']

            # Handle file upload
            foto_profil_path = None  # Default value if no file is uploaded
            if 'foto_profil' in request.files:
                file = request.files['foto_profil']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    foto_profil_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Create a new Anggota instance
            anggota = Anggota(id_anggota=id_anggota, nama=nama, kelas=kelas, jabatan=jabatan, foto_profil=foto_profil_path)
            
            # Add the instance to the session
            db.session.add(anggota)
            
            # Commit changes to the database
            db.session.commit()

            return redirect(url_for('dataa'))

        except Exception as e:
            # Handle specific exceptions if needed
            print(f"Error: {e}")
            db.session.rollback()
            # You might want to provide feedback to the user about the error

        finally:
            # Always close the session in the 'finally' block
            db.session.close()

    return render_template('isi_anggota.html')




# Route to display individual profiles
@app.route('/profile/<int:id_anggota>')
def profile(id_anggota):
    try:
        # Menggunakan SQLAlchemy untuk mengambil data anggota berdasarkan ID
        anggota = Anggota.query.get(id_anggota)
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('profil.html', anggota=anggota)




# Route untuk mengupdate data anggota
@app.route('/update2/<int:id_anggota>', methods=['GET', 'POST'])
def update2(id_anggota):
    if request.method == 'POST':
        try:
            nama = request.form['nama']
            kelas = request.form['kelas']
            jabatan = request.form['jabatan']

            # Menggunakan SQLAlchemy untuk melakukan pembaruan data
            anggota = Anggota.query.get(id_anggota)
            anggota.nama = nama
            anggota.kelas = kelas
            anggota.jabatan = jabatan
            db.session.commit()

            return redirect('/data_anggota')

        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()
        finally:
            db.session.close()

    anggota = Anggota.query.get(id_anggota)
    return render_template('edit2.html', anggota=anggota)

# Route untuk menghapus data anggota
@app.route('/delete/<int:id_anggota>')
def delete(id_anggota):
    try:
        # Menggunakan SQLAlchemy untuk menghapus data
        anggota = Anggota.query.get(id_anggota)
        db.session.delete(anggota)
        db.session.commit()

        return redirect(url_for('dataa'))

    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
    finally:
        db.session.close()

if __name__ == '__main__':
    # Menggunakan SQLAlchemy untuk membuat tabel jika belum ada
    db.create_all()
    app.run(debug=True)
