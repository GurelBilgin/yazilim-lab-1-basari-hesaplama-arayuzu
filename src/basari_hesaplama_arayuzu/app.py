"""Flask web arayüzü."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from flask import Flask, abort, flash, redirect, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename

from .excel_utils import dataframe_to_html, read_excel, validate_numeric_values_between_zero_and_one
from .storage import ensure_directory, read_json, write_json

ALLOWED_EXTENSIONS = {".xls", ".xlsx"}
GRADE_LABELS = ["Öd1", "Öd2", "Quiz", "Vize", "Fin"]


def allowed_excel(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def safe_course_code(course_code: str) -> str:
    return secure_filename(course_code).replace(" ", "_") or "ders"


def create_app(base_dir: str | Path | None = None) -> Flask:
    """Flask uygulamasını oluşturur."""
    app = Flask(__name__)
    app.secret_key = "dev-secret-key"

    root = Path(base_dir) if base_dir else Path.cwd()
    upload_dir = ensure_directory(root / "uploads")
    storage_dir = ensure_directory(root / "storage")

    app.config["UPLOAD_FOLDER"] = upload_dir
    app.config["STORAGE_FOLDER"] = storage_dir

    def courses_path() -> Path:
        return storage_dir / "dersler.json"

    def students_path() -> Path:
        return storage_dir / "ogrenci_listesi.json"

    def program_outcomes_json_path() -> Path:
        return storage_dir / "program_ciktilari.json"

    def load_courses() -> list[dict[str, str]]:
        return read_json(courses_path(), [])

    def save_courses(courses: list[dict[str, str]]) -> None:
        write_json(courses_path(), courses)

    def find_course(course_code: str) -> dict[str, str] | None:
        return next((course for course in load_courses() if course.get("Ders Kodu") == course_code), None)

    def course_file(course_code: str, suffix: str) -> Path:
        return upload_dir / f"{safe_course_code(course_code)}_{suffix}"

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/ders_ekle", methods=["GET", "POST"])
    def ders_ekle():
        courses = load_courses()
        if request.method == "POST":
            course_name = request.form.get("ders_adı", "").strip()
            course_code = request.form.get("ders_kodu", "").strip()
            if course_name and course_code:
                if not any(course.get("Ders Kodu") == course_code for course in courses):
                    courses.append({"Ders Adı": course_name, "Ders Kodu": course_code})
                    save_courses(courses)
                    flash("Ders başarıyla eklendi.", "success")
                else:
                    flash("Bu ders kodu zaten kayıtlı.", "warning")
            return redirect(url_for("ders_ekle"))
        return render_template("ders_ekle.html", dersler=courses)

    @app.route("/ders_sil/<int:ders_index>", methods=["POST"])
    def ders_sil(ders_index: int):
        courses = load_courses()
        if 0 <= ders_index < len(courses):
            courses.pop(ders_index)
            save_courses(courses)
            flash("Ders silindi.", "success")
        return redirect(url_for("ders_ekle"))

    @app.route("/ders_sec", methods=["POST"])
    def ders_sec():
        course_code = request.form.get("secilen_ders", "")
        return redirect(url_for("ders_detay", ders_kodu=course_code))

    @app.route("/ders_sayfasi", methods=["POST"])
    def ders_sayfasi():
        return ders_sec()

    @app.route("/ogrenci_listesi", methods=["GET", "POST"])
    def ogrenci_listesi():
        students = read_json(students_path(), [])
        if request.method == "POST":
            file = request.files.get("file")
            if file and file.filename and allowed_excel(file.filename):
                path = upload_dir / secure_filename(file.filename)
                file.save(path)
                df = read_excel(path)
                if "Öğrenci_No" not in df.columns:
                    flash("Excel dosyasında 'Öğrenci_No' kolonu bulunmalıdır.", "danger")
                else:
                    students = df["Öğrenci_No"].astype(str).tolist()
                    write_json(students_path(), students)
                    flash("Öğrenci listesi yüklendi.", "success")
            return redirect(url_for("ogrenci_listesi"))
        return render_template("ogrenci_listesi.html", ogrenciler=students)

    @app.route("/program_ciktilari", methods=["GET", "POST"])
    def program_ciktilari():
        df = None
        json_path = program_outcomes_json_path()
        if json_path.exists():
            df = pd.read_json(json_path)
        if request.method == "POST":
            file = request.files.get("file")
            if file and file.filename and allowed_excel(file.filename):
                path = upload_dir / secure_filename(file.filename)
                file.save(path)
                df = read_excel(path)
                df.to_json(json_path, orient="records", force_ascii=False)
                flash("Program çıktıları yüklendi.", "success")
            return redirect(url_for("program_ciktilari"))
        return render_template("program_ciktilari.html", ciktilar=df)

    @app.route("/ders_detay/<string:ders_kodu>", methods=["GET", "POST"])
    def ders_detay(ders_kodu: str):
        course = find_course(ders_kodu)
        if not course:
            return "Ders bulunamadı.", 404

        message = ""
        weights_path = storage_dir / f"{safe_course_code(ders_kodu)}_agirliklar.json"
        weights = read_json(weights_path, {label: 0 for label in GRADE_LABELS})

        if request.method == "POST":
            file = request.files.get("excel_dosyasi")
            if file and file.filename and allowed_excel(file.filename):
                path = course_file(ders_kodu, "ogrenme_ciktilari.xlsx")
                file.save(path)
                message = "Öğrenme çıktıları yüklendi."
            elif any(f"agirlik_{label}" in request.form for label in GRADE_LABELS):
                weights = {label: float(request.form.get(f"agirlik_{label}", 0) or 0) for label in GRADE_LABELS}
                write_json(weights_path, weights)
                message = "Ağırlıklar kaydedildi."

        output = None
        learning_path = course_file(ders_kodu, "ogrenme_ciktilari.xlsx")
        if learning_path.exists():
            output = dataframe_to_html(read_excel(learning_path))
        total_weight = sum(float(value) for value in weights.values())
        return render_template(
            "ders_detay.html",
            ders=course,
            output=output,
            agirliklar=weights,
            toplam_agirlik=total_weight,
            mesaj=message,
        )

    @app.route("/tablolar/<string:ders_kodu>", methods=["GET", "POST"])
    def tablolar(ders_kodu: str):
        course = find_course(ders_kodu)
        if not course:
            return "Ders bulunamadı.", 404
        return render_template("tablolar.html", ders=course, mesaj="")

    @app.route("/tablo_detay/<string:ders_kodu>/<int:tablo_id>", methods=["GET", "POST"])
    def tablo_detay(ders_kodu: str, tablo_id: int):
        course = find_course(ders_kodu)
        if not course:
            return "Ders bulunamadı.", 404

        message = ""
        table_path = course_file(ders_kodu, f"tablo{tablo_id}.xlsx")
        if request.method == "POST":
            file = request.files.get("excel_tablo")
            if file and file.filename and allowed_excel(file.filename):
                file.save(table_path)
                df = read_excel(table_path)
                if tablo_id in {1, 2} and not validate_numeric_values_between_zero_and_one(df):
                    message = "Dosya yüklendi ancak sayısal değerlerin 0-1 aralığında olup olmadığı kontrol edilmelidir."
                else:
                    message = f"Tablo {tablo_id} başarıyla yüklendi."
        table_html = dataframe_to_html(read_excel(table_path)) if table_path.exists() else None
        return render_template("tablo_detay.html", ders=course, mesaj=message, tablo=table_html, tablo_id=tablo_id)

    @app.route("/tablo_notlar/<string:ders_kodu>", methods=["GET", "POST"])
    def tablo_notlar(ders_kodu: str):
        course = find_course(ders_kodu)
        if not course:
            return "Ders bulunamadı.", 404

        message = ""
        notes_path = course_file(ders_kodu, "tablo_notlar.xlsx")
        json_path = course_file(ders_kodu, "tablo_notlar.json")
        if request.method == "POST":
            file = request.files.get("excel_dosyasi")
            if file and file.filename and allowed_excel(file.filename):
                file.save(notes_path)
                message = "Excel dosyası yüklendi."
            elif "save_json" in request.form and notes_path.exists():
                df = read_excel(notes_path)
                df.to_json(json_path, orient="records", force_ascii=False)
                message = "Notlar JSON formatında kaydedildi."
        table_html = dataframe_to_html(read_excel(notes_path)) if notes_path.exists() else None
        return render_template("tablo_notlar.html", ders=course, mesaj=message, tablo=table_html, indir_link=notes_path)

    @app.route("/download_excel/<string:ders_kodu>")
    def download_excel(ders_kodu: str):
        path = course_file(ders_kodu, "tablo_notlar.xlsx")
        if path.exists():
            return send_file(path, as_attachment=True)
        return abort(404, description="İndirilecek dosya bulunamadı.")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
