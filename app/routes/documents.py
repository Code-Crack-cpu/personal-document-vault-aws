import uuid
from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from app.config import Config
from app.models.document import (
    create_document,
    delete_for_user,
    find_for_user,
    list_for_user,
)
from app.routes.main import login_required
from app.storage import create_download_url, delete_file, upload_file

documents_bp = Blueprint("documents", __name__)


@documents_bp.route("/documents")
@login_required
def documents():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    items = list_for_user(session["user_id"], search, category)
    return render_template(
        "documents.html",
        documents=items,
        search=search,
        selected_category=category,
    )


@documents_bp.route("/documents/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        uploaded = request.files.get("file")
        if not name or not category or not uploaded or not uploaded.filename:
            flash("Document name, category, and file are required.", "error")
            return render_template("upload.html")

        extension = Path(secure_filename(uploaded.filename)).suffix.lower().lstrip(".")
        if extension not in Config.ALLOWED_EXTENSIONS:
            flash("Only PDF, JPG, JPEG, and PNG files are supported.", "error")
            return render_template("upload.html")
        if uploaded.mimetype not in Config.ALLOWED_MIME_TYPES:
            flash("The uploaded file type is not allowed.", "error")
            return render_template("upload.html")

        uploaded.seek(0, 2)
        file_size = uploaded.tell()
        uploaded.seek(0)
        if file_size == 0 or file_size > Config.MAX_CONTENT_LENGTH:
            flash("File must be non-empty and no larger than 10 MB.", "error")
            return render_template("upload.html")

        object_key = f"users/{session['user_id']}/{uuid.uuid4().hex}.{extension}"
        upload_file(uploaded, object_key, uploaded.mimetype)
        create_document(
            session["user_id"],
            name,
            category,
            object_key,
            uploaded.mimetype,
            file_size,
        )
        flash("Document uploaded securely.", "success")
        return redirect(url_for("documents.documents"))
    return render_template("upload.html")


@documents_bp.route("/documents/<int:document_id>/download")
@login_required
def download(document_id):
    document = find_for_user(document_id, session["user_id"])
    if not document:
        flash("Document not found.", "error")
        return redirect(url_for("documents.documents"))
    return redirect(create_download_url(document["object_key"]))


@documents_bp.route("/documents/<int:document_id>/delete", methods=["POST"])
@login_required
def delete(document_id):
    document = find_for_user(document_id, session["user_id"])
    if not document:
        flash("Document not found.", "error")
        return redirect(url_for("documents.documents"))
    delete_file(document["object_key"])
    delete_for_user(document_id, session["user_id"])
    flash("Document deleted.", "success")
    return redirect(url_for("documents.documents"))
