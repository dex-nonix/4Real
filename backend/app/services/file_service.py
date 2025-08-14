from __future__ import annotations

import os
import hashlib
from typing import Any

from flask import current_app, jsonify, Request
from werkzeug.utils import secure_filename

from .crud_service import CrudService
from ..decorators import expose
from ..models.file import File
from .. import db


class FileService(CrudService):
    model = File
    config = {
        'filters': {
            'fields': ['category_id', 'mime_type', 'title', 'original_filename'],
        },
        'sorting': {
            'default_sort': 'created_at',
            'allowed_fields': ['created_at', 'title', 'original_filename', 'size_bytes'],
        },
        'validation': {
            'required_fields': ['original_filename', 'mime_type', 'size_bytes', 'storage_url'],
            'unique_fields': [],
        },
        'selector': {
            'fields': ['title', 'original_filename'],
            'display_format': None,
            'search_fields': ['title', 'original_filename', 'mime_type'],
            'order_by': 'created_at',
        },
    }

    @expose('/upload', methods=['POST'])
    def upload(self, req: Request) -> Any:
        try:
            if 'file' not in req.files:  # type: ignore[attr-defined]
                return jsonify({'error': 'file is required'}), 400

            file_storage = req.files['file']  # type: ignore[attr-defined]
            if not file_storage or file_storage.filename is None:
                return jsonify({'error': 'invalid file'}), 400

            filename = secure_filename(file_storage.filename)
            if not filename:
                return jsonify({'error': 'invalid filename'}), 400

            # Configured upload directory
            upload_dir = getattr(current_app.config, 'UPLOAD_DIR', None)
            if not upload_dir:
                # fallback: backend/app/uploads under current file
                base_dir = os.path.dirname(os.path.dirname(__file__))
                upload_dir = os.path.join(base_dir, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)

            # Ensure unique filename
            base, ext = os.path.splitext(filename)
            safe_name = filename
            counter = 1
            while os.path.exists(os.path.join(upload_dir, safe_name)):
                safe_name = f"{base}_{counter}{ext}"
                counter += 1

            # Save file
            file_path = os.path.join(upload_dir, safe_name)
            file_storage.save(file_path)

            # Derive metadata
            size_bytes = os.path.getsize(file_path)
            mime_type = getattr(file_storage, 'mimetype', 'application/octet-stream')
            sha256 = self._file_sha256(file_path)

            # Dev URL mapping
            storage_url = f"/uploads/{safe_name}"

            title = (req.form.get('title') or '').strip()  # type: ignore[attr-defined]
            category_id_raw = req.form.get('category_id')  # type: ignore[attr-defined]
            category_id = int(category_id_raw) if category_id_raw else None

            rec = File(
                category_id=category_id,
                title=title or None,
                original_filename=filename,
                mime_type=mime_type,
                size_bytes=size_bytes,
                storage_url=storage_url,
                sha256=sha256,
            )
            db.session.add(rec)
            db.session.commit()

            return jsonify({'data': rec.to_dict()}), 201
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

    def _file_sha256(self, path: str) -> str:
        try:
            h = hashlib.sha256()
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return ''


