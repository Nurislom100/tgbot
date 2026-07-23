import base64
import sys
import uuid
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.append(str(Path(__file__).parent.parent / "bot"))
import database as db  # noqa: E402
from auth import validate_init_data  # noqa: E402

BASE_DIR = Path(__file__).parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    db.init_db()


def get_user_or_403(init_data: str):
    user = validate_init_data(init_data)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid initData")
    return user


class RecordIn(BaseModel):
    init_data: str
    shop_name: str
    address_text: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    phone: str | None = None
    product_name: str | None = None
    quantity: str | None = None
    photo_base64: str | None = None  # "data:image/jpeg;base64,...."


@app.post("/api/record")
def add_record(payload: RecordIn):
    user = get_user_or_403(payload.init_data)
    distributor = db.get_distributor(user["id"])
    if not distributor:
        raise HTTPException(status_code=404, detail="Distributor not found")

    if not payload.shop_name or not payload.shop_name.strip():
        raise HTTPException(status_code=400, detail="shop_name is required")

    photo_path = None
    if payload.photo_base64:
        try:
            header, data = payload.photo_base64.split(",", 1)
            ext = "jpg" if "jpeg" in header or "jpg" in header else "png"
            filename = f"{uuid.uuid4().hex}.{ext}"
            (UPLOADS_DIR / filename).write_bytes(base64.b64decode(data))
            photo_path = filename
        except Exception:
            photo_path = None

    with db.get_conn() as conn:
        conn.execute(
            """INSERT INTO records
               (distributor_id, shop_name, address_text, latitude, longitude,
                phone, product_name, quantity, photo_path)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                distributor["id"], payload.shop_name.strip(), payload.address_text,
                payload.latitude, payload.longitude, payload.phone,
                payload.product_name, payload.quantity, photo_path,
            ),
        )
    return {"ok": True}


@app.get("/api/stats")
def get_stats(init_data: str, year: int, month: int):
    user = get_user_or_403(init_data)
    distributor = db.get_distributor(user["id"])
    if not distributor:
        raise HTTPException(status_code=404, detail="Distributor not found")

    month_str = f"{year:04d}-{month:02d}"
    with db.get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM records
               WHERE distributor_id = ? AND strftime('%Y-%m', created_at) = ?
               ORDER BY created_at DESC""",
            (distributor["id"], month_str),
        ).fetchall()

    records = [dict(r) for r in rows]
    unique_shops = len({r["shop_name"] for r in records})
    total_qty = 0
    for r in records:
        try:
            total_qty += float(r["quantity"]) if r["quantity"] else 0
        except ValueError:
            pass

    return {
        "distributor_name": distributor["full_name"],
        "total_records": len(records),
        "unique_shops": unique_shops,
        "total_quantity": total_qty,
        "records": records,
    }


app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
app.mount("/", StaticFiles(directory=BASE_DIR / "webapp", html=True), name="webapp")
