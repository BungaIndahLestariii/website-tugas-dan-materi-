from pathlib import Path
from uuid import uuid4
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)

# Batas total request 1 GB. Untuk beberapa file sekaligus, total request juga
# harus tidak melebihi batas ini.
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024

UPLOAD_FOLDER = Path(app.root_path) / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {
    "pdf", "doc", "docx", "ppt", "pptx", "zip", "png", "jpg", "jpeg",
    "xlsx", "txt"
}

app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify(error="Tidak ada file yang diterima."), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify(error="Silakan pilih file terlebih dahulu."), 400

    original_name = secure_filename(file.filename)
    if not original_name:
        original_name = "lampiran"

    extension = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""
    if extension not in ALLOWED_EXTENSIONS:
        return jsonify(error="Jenis file tidak didukung."), 400

    # Nama penyimpanan unik agar file dengan nama sama tidak saling menimpa.
    stored_name = f"{uuid4().hex}_{original_name}"
    destination = UPLOAD_FOLDER / stored_name
    file.save(destination)

    return jsonify(
        name=file.filename,
        url=f"/uploads/{stored_name}"
    ), 201


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)


@app.errorhandler(RequestEntityTooLarge)
def file_too_large(_error):
    return jsonify(error="Ukuran unggahan melebihi batas 1 GB."), 413


if __name__ == "__main__":
    print("Server berjalan! Buka http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
