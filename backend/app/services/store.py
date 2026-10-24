"""Firestore data access with a clear startup error when credentials are missing."""
import os
from functools import lru_cache
from typing import Any
from datetime import date, datetime

class StoreError(RuntimeError):
    pass

class FirestoreStore:
    def __init__(self):
        self._db = None
        self._init_error = None
        self._connect()

    def _connect(self):
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore
            from backend.app.config import FIREBASE_CREDENTIALS_PATH, FIREBASE_PROJECT_ID
            if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
                self._init_error = (
                    f"Firebase credentials file not found: {FIREBASE_CREDENTIALS_PATH}. "
                    "Copy your Firebase Admin service-account JSON to the project root and configure .env."
                )
                return
            try:
                app = firebase_admin.get_app()
            except ValueError:
                opts = {"projectId": FIREBASE_PROJECT_ID} if FIREBASE_PROJECT_ID else None
                cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
                app = firebase_admin.initialize_app(cred, opts)
            self._db = firestore.client(app=app)
        except Exception as exc:
            self._init_error = f"Firebase initialization failed: {exc}"

    @property
    def ready(self) -> bool:
        return self._db is not None

    @property
    def error(self):
        return self._init_error

    def _require(self):
        if self._db is None:
            raise StoreError(self._init_error or "Firebase is not configured.")

    def list(self, collection: str) -> list[dict[str, Any]]:
        self._require()
        return [self._serialize(d.to_dict() | {"id": d.id}) for d in self._db.collection(collection).stream()]

    def get(self, collection: str, item_id: str) -> dict[str, Any] | None:
        self._require()
        snap = self._db.collection(collection).document(item_id).get()
        return self._serialize(snap.to_dict() | {"id": snap.id}) if snap.exists else None

    def create(self, collection: str, data: dict[str, Any]) -> dict[str, Any]:
        self._require()
        payload = self._clean(data)
        payload["created_at"] = datetime.utcnow().isoformat() + "Z"
        payload["updated_at"] = payload["created_at"]
        ref = self._db.collection(collection).document()
        ref.set(payload)
        return self._serialize(payload | {"id": ref.id})

    def update(self, collection: str, item_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        self._require()
        ref = self._db.collection(collection).document(item_id)
        if not ref.get().exists:
            return None
        payload = self._clean(data)
        payload["updated_at"] = datetime.utcnow().isoformat() + "Z"
        ref.update(payload)
        current = ref.get().to_dict() or {}
        return self._serialize(current | {"id": item_id})

    def delete(self, collection: str, item_id: str) -> bool:
        self._require()
        ref = self._db.collection(collection).document(item_id)
        if not ref.get().exists:
            return False
        ref.delete()
        return True

    def _clean(self, value):
        if isinstance(value, dict):
            return {k: self._clean(v) for k, v in value.items() if v is not None}
        if isinstance(value, list):
            return [self._clean(v) for v in value]
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        return value

    def _serialize(self, value):
        if isinstance(value, dict):
            return {k: self._serialize(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._serialize(v) for v in value]
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return value

@lru_cache(maxsize=1)
def get_store() -> FirestoreStore:
    return FirestoreStore()
