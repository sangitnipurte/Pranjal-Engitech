import os
import sqlite3
import uuid
from functools import wraps
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify
)
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_DB = os.path.join(BASE_DIR, "pranjal_engitech.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    },
)

app.secret_key = os.getenv("SECRET_KEY", "change-this-secret")
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024

ALLOWED_EXT = {"png", "jpg", "jpeg", "webp", "gif", "svg"}


# ============================================================
# MONGODB / CLOUDINARY CONFIGURATION
# ============================================================

MONGO_URI = os.getenv("MONGO_URI", "").strip()
USE_MONGO = bool(MONGO_URI)

DB_NAME = os.getenv("DB_NAME", "pranjal_engitech")

cloudinary_ready = False
REQUIRE_MONGO = os.getenv("REQUIRE_MONGO", "false").lower() == "true"
REQUIRE_CLOUDINARY = os.getenv(
    "REQUIRE_CLOUDINARY", "false"
).lower() == "true"

cloudinary = None
cloudinary_uploader = None

if REQUIRE_MONGO and not MONGO_URI:
    raise RuntimeError(
        "MONGO_URI is required when REQUIRE_MONGO=true"
    )

if USE_MONGO:
    from pymongo import MongoClient

    mongo_client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=6000
    )

    mongo_db = mongo_client[DB_NAME]

else:
    mongo_client = None
    mongo_db = None


# ============================================================
# CLOUDINARY
# ============================================================

try:
    import cloudinary as _cloudinary
    import cloudinary.uploader as _cloudinary_uploader

    if (
        os.getenv("CLOUDINARY_CLOUD_NAME")
        and os.getenv("CLOUDINARY_API_KEY")
        and os.getenv("CLOUDINARY_API_SECRET")
    ):
        _cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET"),
            secure=True,
        )

        cloudinary = _cloudinary
        cloudinary_uploader = _cloudinary_uploader
        cloudinary_ready = True

except Exception:
    pass


if REQUIRE_CLOUDINARY and not cloudinary_ready:
    raise RuntimeError(
        "Cloudinary credentials are required when REQUIRE_CLOUDINARY=true"
    )


# ============================================================
# DEFAULT WEBSITE SETTINGS
# ============================================================

DEFAULT_SETTINGS = {
    "company_name": "Pranjal Engitech (OPC) Private Limited",
    "short_name": "PRANJAL ENGITECH",
    "tagline": "Industrial Safety, Engineering & Polymer Products",

    "hero_title": "Industrial Safety & Engineering Solutions",

    "hero_text": (
        "Explore flange guards, spray guards, earthing jumpers, "
        "gaskets, valve guards and other engineered protection products."
    ),

    "phone": "+91 XXXXX XXXXX",
    "email": "info@pranjalengitech.com",
    "address": "Maharashtra, India",
    "hours": "Monday – Saturday | 9:00 AM – 6:00 PM",

    "maps_url": "https://www.google.com/maps",
    "whatsapp": "",

    "facebook": "",
    "instagram": "",
    "linkedin": "",

    "about_title": "Engineering Products Built for Industrial Safety",

    "about_text": (
        "Pranjal Engitech (OPC) Private Limited provides industrial "
        "safety and engineering product solutions. Product information, "
        "specifications, images, contact details and company content can "
        "be managed from the admin panel."
    ),

    "logo_image": "images/logo.png",
    "hero_image": "",

    "footer_text": (
        "Pranjal Engitech (OPC) Private Limited. All Rights Reserved."
    ),

    "announcement": (
        "Welcome to Pranjal Engitech — Industrial Safety & Engineering Products."
    ),
}


# ============================================================
# PRODUCT CATALOGUE
# ============================================================

PRODUCTS = [
    ("SPRAY GUARDS", "PTFE BELOW GUARD"),
    ("FLANGE GUARDS", "PP FLANGE GUARDS"),
    ("SPRAY GUARDS", "PP FLANGE GUARDS"),
    ("FLANGE GUARDS", "PP BOX TYPE FLANGE GUARDS"),
    ("FLANGE GUARDS", "PP UNIVERSAL FLANGE GUARDS"),
    ("FLANGE SHIELD", "PTFE COATED FIBERGLASS FLANGE GUARDS SHIELDS"),
    ("FLANGE GUARDS", "SS304 STRIPS TYPE FLANGE GUARDS"),
    ("FLANGE SHIELD", "SS304 BOX TYPE FLANGE GUARDS"),
    ("FLANGE SHIELD", "SS316 STRIPS TYPE FLANGE GUARDS"),
    ("FLANGE GUARDS", "HDPE FLANGE GUARDS"),
    (
        "FLANGE SHIELD",
        "PTFE COATED FIBERGLASS FLANGE GUARDS SHIELDS WITH PVC TRANSPARENT COVER",
    ),
    ("FLANGE GUARDS", "PVC FLANGE GUARDS"),
    ("FLANGE GUARDS", "PVC FLANGE GUARDS WITH TRANSPARENT WINDOW"),
    ("FLANGE SHIELD", "PTFE VALVE GUARDS"),
    ("FLANGE SHIELD", "PVC VALVE GUARDS"),
    ("EARTHING JUMPERS", "COPPER EARTHING JUMPERS"),
    ("EARTHING JUMPERS", "COPPER BRAIDED EARTHING JUMPERS"),
    ("EARTHING JUMPERS", "SS 304 BRAIDED JUMPER"),
    (
        "EARTHING JUMPERS",
        "COPPER WIRE TYPE JUMPER WITH ALUMINIUM LUGS",
    ),
    ("EARTHING JUMPERS", "SS 304 JUMPER"),
    ("EARTHING JUMPERS", "ALUMINIUM JUMPER"),
    ("EARTHING JUMPERS", "COPPER WIRE TYPE JUMPER"),
    ("EARTHING JUMPERS", "COPPER BRAIDED JUMPER"),
    ("FLANGE GUARDS", "FRP FLANGE GUARDS"),
    ("NEW PRODUCTS", "FRP MOTOR CANOPY"),
    ("FLANGE GUARDS", "PP FLANGE GUARDS"),
    ("FLANGE GUARDS", "SS 304 COLLER TYPE FLANGE GUARDS"),
    ("FLANGE GUARDS", "SS 304 FLANGE GUARDS WITH SILICON ELASTOMERS"),
    ("NEW PRODUCTS", "PP LEG TYPE FLANGE COVERS"),
    ("NEW PRODUCTS", "PTFE BELLOWS"),
    ("NEW PRODUCTS", "PP PALL RING"),
    ("NEW PRODUCTS", "PTFE “TC” RING GASKET"),
    ("NEW PRODUCTS", "PP BALL VALVE FLANGE"),
    ("FLANGE GUARDS", "SS 304 FLANGE GUARDS WITH UNIVERSAL LOCK"),
    ("NEW PRODUCTS", "PP FOOT VALVE FLANGE END"),
    (
        "SPRAY GUARDS",
        "SS 304 FLANGE GUARDS WITH NOTCHE AND WING NUT",
    ),
    ("NEW PRODUCTS", "HDPE BALL VALVE FLANGE END"),
    ("SPRAY GUARDS", "SS 304 FLANGE GUARDS WITH NOTCHE"),
    ("NEW PRODUCTS", "PPRC BALL VALVE FLANGE END"),
    ("NEW PRODUCTS", "PP BALL VALVE NRV FLANGE END"),
    ("NEW PRODUCTS", "PP SCOOP"),
    ("SPRAY GUARDS", "SS FLANGE GUARDS SLOT AND NOTCHE"),
    ("NEW PRODUCTS", "PP SCRAPPER"),
    ("SPRAY GUARDS", "PTFE FLANGE GUARDS"),
    ("NEW PRODUCTS", "PP NUT AND BOLT"),
    ("NEW PRODUCTS", "PP SPADE"),
    ("NEW PRODUCTS", "PP STRAINER"),
    ("NEW PRODUCTS", "PTFE READY CUT GASKET"),
    ("NEW PRODUCTS", "PTFE ENVELOPE GASKET (0.5 + 0.5)"),
    ("NEW PRODUCTS", "SS 304 BOX TYPE VALVE GUARDS"),
    (
        "NEW PRODUCTS",
        "PTFE MILLED TYPE GASKET WITH 2MM AF GASKET",
    ),
    ("NEW PRODUCTS", "PP FLANGE END COVERS END"),
    (
        "NEW PRODUCTS",
        "PTFE MILLED TYPE ENVELOPE WITH AF GASKET WITH SERRETION RING",
    ),
]


# ============================================================
# CLIENTS
# ============================================================

CLIENTS = [
    "ITC Limited",
    "L&T Hydrocarbon Engineering",
    "LANXESS",
    "Aditya Birla Chemicals",
    "Asian Paints",
    "Aurobindo",
    "Cipla",
    "Coromandel",
    "Mylan",
    "Pidilite",
    "Piramal",
    "Rallis India",
    "Teva API",
    "Divi’s Laboratories",
    "Dr. Reddy’s Laboratories",
    "Finolex Industries",
    "Grasim",
    "Hindustan Unilever",
    "IndianOil",
]


# ============================================================
# SQLITE
# ============================================================

def sql_conn():
    con = sqlite3.connect(LOCAL_DB)
    con.row_factory = sqlite3.Row
    return con


def init_sqlite():
    con = sql_conn()

    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            name TEXT,
            description TEXT,
            specs TEXT,
            image TEXT,
            active INTEGER DEFAULT 1,
            sort_order INTEGER DEFAULT 0,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            product TEXT,
            message TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            image TEXT,
            description TEXT,
            active INTEGER DEFAULT 1,
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            text TEXT,
            image TEXT,
            button_text TEXT,
            button_url TEXT,
            active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            logo TEXT,
            active INTEGER DEFAULT 1,
            sort_order INTEGER DEFAULT 0,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            event_date TEXT,
            location TEXT,
            description TEXT,
            image TEXT,
            active INTEGER DEFAULT 1,
            sort_order INTEGER DEFAULT 0,
            created_at TEXT
        );
        """
    )

    for k, v in DEFAULT_SETTINGS.items():
        con.execute(
            "INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)",
            (k, v),
        )

    if con.execute(
        "SELECT COUNT(*) c FROM products"
    ).fetchone()["c"] == 0:

        for i, (cat, name) in enumerate(PRODUCTS, 1):

            con.execute(
                """
                INSERT INTO products
                (
                    category,
                    name,
                    description,
                    specs,
                    image,
                    active,
                    sort_order,
                    created_at
                )
                VALUES (?,?,?,?,?,?,?,?)
                """,
                (
                    cat,
                    name,
                    "Product details and specifications can be updated from the admin panel.",
                    "Available sizes and dimensions as per customer requirement.",
                    "",
                    1,
                    i,
                    datetime.utcnow().isoformat(),
                ),
            )

    if con.execute(
        "SELECT COUNT(*) c FROM categories"
    ).fetchone()["c"] == 0:

        cats = sorted(set(c for c, _ in PRODUCTS))

        for i, c in enumerate(cats, 1):
            con.execute(
                """
                INSERT INTO categories
                (name, description, sort_order)
                VALUES (?,?,?)
                """,
                (
                    c,
                    "Product category",
                    i,
                ),
            )

    if con.execute(
        "SELECT COUNT(*) c FROM clients"
    ).fetchone()["c"] == 0:

        for i, name in enumerate(CLIENTS, 1):

            con.execute(
                """
                INSERT INTO clients
                (name, logo, active, sort_order, created_at)
                VALUES (?,?,?,?,?)
                """,
                (
                    name,
                    "",
                    1,
                    i,
                    datetime.utcnow().isoformat(),
                ),
            )

    con.commit()
    con.close()


init_sqlite()


# ============================================================
# MONGODB HELPERS
# ============================================================

def mongo_col(name):
    return mongo_db[name]


def init_mongo():

    if not USE_MONGO:
        return

    # Never overwrite existing cloud content.
    # Seed only empty collections.

    if mongo_col("settings").count_documents({}) == 0:

        mongo_col("settings").insert_one(
            {
                "_id": "site",
                "data": dict(DEFAULT_SETTINGS),
            }
        )

    if mongo_col("products").count_documents({}) == 0:

        docs = []

        for i, (cat, name) in enumerate(PRODUCTS, 1):

            docs.append(
                {
                    "category": cat,
                    "name": name,
                    "description": (
                        "Product details and specifications "
                        "can be updated from the admin panel."
                    ),
                    "specs": (
                        "Available sizes and dimensions "
                        "as per customer requirement."
                    ),
                    "image": "",
                    "active": True,
                    "sort_order": i,
                    "created_at": datetime.utcnow().isoformat(),
                }
            )

        mongo_col("products").insert_many(docs)

    if mongo_col("categories").count_documents({}) == 0:

        for i, c in enumerate(
            sorted(set(c for c, _ in PRODUCTS)), 1
        ):

            mongo_col("categories").insert_one(
                {
                    "name": c,
                    "description": "Product category",
                    "image": "",
                    "active": True,
                    "sort_order": i,
                }
            )

    if mongo_col("clients").count_documents({}) == 0:

        mongo_col("clients").insert_many(
            [
                {
                    "name": n,
                    "logo": "",
                    "active": True,
                    "sort_order": i,
                    "created_at": datetime.utcnow().isoformat(),
                }
                for i, n in enumerate(CLIENTS, 1)
            ]
        )


init_mongo()


# ============================================================
# IMPORTANT MONGODB FIX
# ============================================================

def normalize(doc):

    if not doc:
        return None

    d = dict(doc)

    if "_id" in d:
        d["id"] = str(d["_id"])

        # IMPORTANT:
        # Remove MongoDB ObjectId before jsonify()
        del d["_id"]

    return d


# ============================================================
# SETTINGS
# ============================================================

def get_settings():

    if USE_MONGO:

        doc = mongo_col("settings").find_one(
            {"_id": "site"}
        ) or {}

        out = dict(DEFAULT_SETTINGS)
        out.update(doc.get("data", {}))

        return out

    con = sql_conn()

    rows = con.execute(
        "SELECT key,value FROM settings"
    ).fetchall()

    con.close()

    out = dict(DEFAULT_SETTINGS)

    out.update(
        {
            r["key"]: r["value"]
            for r in rows
        }
    )

    return out


def set_settings(values):

    if USE_MONGO:

        mongo_col("settings").update_one(
            {"_id": "site"},
            {"$set": {"data": values}},
            upsert=True,
        )

        return

    con = sql_conn()

    for k, v in values.items():

        con.execute(
            """
            INSERT OR REPLACE INTO settings(key,value)
            VALUES(?,?)
            """,
            (k, str(v)),
        )

    con.commit()
    con.close()


# ============================================================
# GENERIC DOCUMENT FUNCTIONS
# ============================================================

def list_docs(collection, active_only=False):

    if USE_MONGO:

        q = {"active": True} if active_only else {}

        sort_field = (
            "sort_order"
            if collection in {
                "products",
                "categories",
                "clients",
                "events",
            }
            else "created_at"
        )

        return [
            normalize(x)
            for x in mongo_col(collection)
            .find(q)
            .sort(sort_field, 1)
        ]

    con = sql_conn()

    table = collection

    where = (
        " WHERE active=1"
        if active_only and collection != "enquiries"
        else ""
    )

    order = (
        " ORDER BY sort_order ASC, id DESC"
        if collection in {
            "products",
            "categories",
            "clients",
            "events",
        }
        else " ORDER BY id DESC"
    )

    q = f"SELECT * FROM {table}{where}{order}"

    rows = [
        dict(x)
        for x in con.execute(q).fetchall()
    ]

    con.close()

    return rows


def get_doc(collection, ident):

    if USE_MONGO:

        from bson import ObjectId

        q = (
            {"_id": ObjectId(ident)}
            if ObjectId.is_valid(ident)
            else {"_id": ident}
        )

        return normalize(
            mongo_col(collection).find_one(q)
        )

    con = sql_conn()

    row = con.execute(
        f"SELECT * FROM {collection} WHERE id=?",
        (ident,),
    ).fetchone()

    con.close()

    return dict(row) if row else None


def save_doc(collection, data, ident=None):

    data = dict(data)

    # id and _id are transport fields only.
    # They must never be inserted into the database.

    data.pop("id", None)
    data.pop("_id", None)

    if USE_MONGO:

        from bson import ObjectId

        if ident:

            q = (
                {"_id": ObjectId(ident)}
                if ObjectId.is_valid(str(ident))
                else {"_id": ident}
            )

            mongo_col(collection).update_one(
                q,
                {"$set": data},
            )

            return ident

        data["created_at"] = datetime.utcnow().isoformat()

        return str(
            mongo_col(collection)
            .insert_one(data)
            .inserted_id
        )

    con = sql_conn()

    try:

        if ident:

            sets = ", ".join(
                f"{k}=?"
                for k in data
            )

            con.execute(
                f"""
                UPDATE {collection}
                SET {sets}
                WHERE id=?
                """,
                list(data.values()) + [ident],
            )

            rid = ident

        else:

            fields = ", ".join(data.keys())
            vals = list(data.values())

            if not fields:
                raise ValueError(
                    f"No fields supplied for {collection}"
                )

            cur = con.execute(
                f"""
                INSERT INTO {collection}
                ({fields})
                VALUES ({",".join("?" for _ in vals)})
                """,
                vals,
            )

            rid = cur.lastrowid

        con.commit()

        return rid

    except Exception:

        con.rollback()
        raise

    finally:

        con.close()


def delete_doc(collection, ident):

    if USE_MONGO:

        from bson import ObjectId

        q = (
            {"_id": ObjectId(ident)}
            if ObjectId.is_valid(ident)
            else {"_id": ident}
        )

        mongo_col(collection).delete_one(q)

        return

    con = sql_conn()

    con.execute(
        f"DELETE FROM {collection} WHERE id=?",
        (ident,),
    )

    con.commit()
    con.close()


# ============================================================
# FILE UPLOADS
# ============================================================

def save_upload(file, folder="general"):

    if not file or not file.filename:
        return ""

    ext = file.filename.rsplit(".", 1)[-1].lower()

    if ext not in ALLOWED_EXT:
        return ""

    # Cloudinary
    if cloudinary_ready:

        result = cloudinary_uploader.upload(
            file,
            folder=f"pranjal-engitech/{folder}",
        )

        return result.get("secure_url", "")

    # Local storage
    folder_path = os.path.join(
        UPLOAD_DIR,
        secure_filename(folder),
    )

    os.makedirs(
        folder_path,
        exist_ok=True,
    )

    filename = (
        f"{uuid.uuid4().hex[:12]}_"
        f"{secure_filename(file.filename)}"
    )

    path = os.path.join(
        folder_path,
        filename,
    )

    file.save(path)

    return (
        f"uploads/"
        f"{secure_filename(folder)}/"
        f"{filename}"
    )


def image_url(value):

    if not value:
        return url_for(
            "static",
            filename="images/product-placeholder.svg",
        )

    if str(value).startswith(
        ("http://", "https://", "data:")
    ):
        return value

    return url_for(
        "static",
        filename=value,
    )


app.jinja_env.globals["image_url"] = image_url


# ============================================================
# TEMPLATE CONTEXT
# ============================================================

@app.context_processor
def inject():

    return {
        "site": get_settings(),
        "cloud_mode": USE_MONGO,
        "cloudinary_ready": cloudinary_ready,
    }


# ============================================================
# ADMIN AUTHENTICATION
# ============================================================

def admin_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if not session.get("admin"):

            return redirect(
                url_for(
                    "admin_login",
                    next=request.path,
                )
            )

        return f(*args, **kwargs)

    return wrapper


# ============================================================
# PUBLIC WEBSITE
# ============================================================

@app.route("/")
def home():

    products = list_docs(
        "products",
        True
    )[:12]

    categories = list_docs(
        "categories",
        True
    )

    offers = [
        o
        for o in list_docs("offers", True)
        if o.get("active")
    ]

    clients = list_docs(
        "clients",
        True
    )

    events = list_docs(
        "events",
        True
    )

    return render_template(
        "index.html",
        products=products,
        categories=categories,
        offers=offers,
        clients=clients,
        events=events,
    )


@app.route("/products")
def products():

    cat = request.args.get(
        "category",
        ""
    ).strip()

    all_products = list_docs(
        "products",
        True
    )

    if cat:

        all_products = [
            p
            for p in all_products
            if p.get("category") == cat
        ]

    return render_template(
        "products.html",
        products=all_products,
        categories=list_docs(
            "categories",
            True
        ),
        selected=cat,
    )


@app.route("/product/<ident>")
def product_detail(ident):

    p = get_doc(
        "products",
        ident
    )

    if not p:
        return (
            "Product not found",
            404
        )

    return render_template(
        "product.html",
        product=p,
    )


@app.route("/about")
def about():

    return render_template(
        "about.html"
    )


@app.route(
    "/contact",
    methods=["GET", "POST"]
)
def contact():

    if request.method == "POST":

        data = {
            k: request.form.get(
                k,
                ""
            ).strip()
            for k in [
                "name",
                "email",
                "phone",
                "product",
                "message",
            ]
        }

        data["created_at"] = (
            datetime.utcnow().isoformat()
        )

        if USE_MONGO:

            mongo_col(
                "enquiries"
            ).insert_one(data)

        else:

            save_doc(
                "enquiries",
                data
            )

        flash(
            "Thank you. Your enquiry has been submitted.",
            "success",
        )

        return redirect(
            url_for("contact")
        )

    return render_template(
        "contact.html"
    )


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        u = request.form.get(
            "username",
            ""
        )

        p = request.form.get(
            "password",
            ""
        )

        if (
            u == os.getenv(
                "ADMIN_USERNAME",
                "admin"
            )
            and
            p == os.getenv(
                "ADMIN_PASSWORD",
                "admin123"
            )
        ):

            session["admin"] = True

            return redirect(
                request.args.get(
                    "next"
                )
                or url_for(
                    "admin_dashboard"
                )
            )

        flash(
            "Invalid username or password.",
            "error",
        )

    return render_template(
        "admin/login.html"
    )


@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin")
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():

    stats = {
        c: len(list_docs(c))
        for c in [
            "products",
            "categories",
            "clients",
            "events",
            "enquiries",
            "offers",
        ]
    }

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        enquiries=list_docs(
            "enquiries"
        )[-8:][::-1],
    )


# ============================================================
# ADMIN SETTINGS
# ============================================================

@app.route(
    "/admin/settings",
    methods=["GET", "POST"]
)
@admin_required
def admin_settings():

    s = get_settings()

    if request.method == "POST":

        values = {
            k: request.form.get(
                k,
                ""
            ).strip()
            for k in DEFAULT_SETTINGS.keys()
            if k not in [
                "logo_image",
                "hero_image",
            ]
        }

        for field, folder in [
            ("logo_image", "branding"),
            ("hero_image", "hero"),
        ]:

            uploaded = save_upload(
                request.files.get(field),
                folder,
            )

            values[field] = (
                uploaded
                or s.get(field, "")
            )

        set_settings(values)

        flash(
            "Website settings saved successfully.",
            "success",
        )

        return redirect(
            url_for("admin_settings")
        )

    return render_template(
        "admin/settings.html",
        s=s,
    )


# ============================================================
# ADMIN PRODUCTS
# ============================================================

@app.route("/admin/products")
@admin_required
def admin_products():

    return render_template(
        "admin/products.html",
        products=list_docs(
            "products",
            False
        ),
        categories=list_docs(
            "categories",
            False
        ),
    )


@app.route(
    "/admin/products/save",
    methods=["POST"]
)
@admin_required
def admin_product_save():

    ident = (
        request.form.get(
            "id",
            ""
        ).strip()
        or None
    )

    old = (
        get_doc(
            "products",
            ident
        )
        if ident
        else {}
    )

    data = {
        "category": request.form.get(
            "category",
            ""
        ).strip(),

        "name": request.form.get(
            "name",
            ""
        ).strip(),

        "description": request.form.get(
            "description",
            ""
        ).strip(),

        "specs": request.form.get(
            "specs",
            ""
        ).strip(),

        "active": bool(
            request.form.get("active")
        ),

        "sort_order": int(
            request.form.get(
                "sort_order"
            )
            or 0
        ),
    }

    img = save_upload(
        request.files.get("image"),
        "products",
    )

    data["image"] = (
        img
        or old.get("image", "")
    )

    if not data["name"]:

        flash(
            "Product name is required.",
            "error",
        )

    else:

        save_doc(
            "products",
            data,
            ident
        )

        flash(
            "Product saved.",
            "success",
        )

    return redirect(
        url_for("admin_products")
    )


@app.route(
    "/admin/products/delete/<ident>",
    methods=["POST"]
)
@admin_required
def admin_product_delete(ident):

    delete_doc(
        "products",
        ident
    )

    flash(
        "Product deleted.",
        "success",
    )

    return redirect(
        url_for("admin_products")
    )


# ============================================================
# ADMIN CATEGORIES
# ============================================================

@app.route(
    "/admin/categories",
    methods=["GET", "POST"]
)
@admin_required
def admin_categories():

    if request.method == "POST":

        ident = (
            request.form.get(
                "id",
                ""
            ).strip()
            or None
        )

        old = (
            get_doc(
                "categories",
                ident
            )
            if ident
            else {}
        )

        data = {
            "name": request.form.get(
                "name",
                ""
            ).strip(),

            "description": request.form.get(
                "description",
                ""
            ).strip(),

            "active": bool(
                request.form.get(
                    "active"
                )
            ),

            "sort_order": int(
                request.form.get(
                    "sort_order"
                )
                or 0
            ),
        }

        img = save_upload(
            request.files.get("image"),
            "categories",
        )

        data["image"] = (
            img
            or old.get("image", "")
        )

        if data["name"]:

            save_doc(
                "categories",
                data,
                ident
            )

            flash(
                "Category saved.",
                "success",
            )

        return redirect(
            url_for(
                "admin_categories"
            )
        )

    return render_template(
        "admin/categories.html",
        categories=list_docs(
            "categories",
            False
        ),
    )


@app.route(
    "/admin/categories/delete/<ident>",
    methods=["POST"]
)
@admin_required
def admin_category_delete(ident):

    delete_doc(
        "categories",
        ident
    )

    flash(
        "Category deleted.",
        "success",
    )

    return redirect(
        url_for(
            "admin_categories"
        )
    )


# ============================================================
# ADMIN OFFERS
# ============================================================

@app.route(
    "/admin/offers",
    methods=["GET", "POST"]
)
@admin_required
def admin_offers():

    if request.method == "POST":

        ident = (
            request.form.get(
                "id",
                ""
            ).strip()
            or None
        )

        old = (
            get_doc(
                "offers",
                ident
            )
            if ident
            else {}
        )

        data = {
            "title": request.form.get(
                "title",
                ""
            ).strip(),

            "text": request.form.get(
                "text",
                ""
            ).strip(),

            "button_text": request.form.get(
                "button_text",
                ""
            ).strip(),

            "button_url": request.form.get(
                "button_url",
                ""
            ).strip(),

            "active": bool(
                request.form.get(
                    "active"
                )
            ),
        }

        img = save_upload(
            request.files.get("image"),
            "offers",
        )

        data["image"] = (
            img
            or old.get("image", "")
        )

        save_doc(
            "offers",
            data,
            ident
        )

        flash(
            "Offer saved.",
            "success",
        )

        return redirect(
            url_for("admin_offers")
        )

    return render_template(
        "admin/offers.html",
        offers=list_docs(
            "offers",
            False
        ),
    )


@app.route(
    "/admin/offers/delete/<ident>",
    methods=["POST"]
)
@admin_required
def admin_offer_delete(ident):

    delete_doc(
        "offers",
        ident
    )

    flash(
        "Offer deleted.",
        "success",
    )

    return redirect(
        url_for("admin_offers")
    )


# ============================================================
# ADMIN ENQUIRIES
# ============================================================

@app.route("/admin/enquiries")
@admin_required
def admin_enquiries():

    return render_template(
        "admin/enquiries.html",
        enquiries=list_docs(
            "enquiries"
        ),
    )


@app.route(
    "/admin/enquiries/delete/<ident>",
    methods=["POST"]
)
@admin_required
def admin_enquiry_delete(ident):

    delete_doc(
        "enquiries",
        ident
    )

    flash(
        "Enquiry deleted.",
        "success",
    )

    return redirect(
        url_for("admin_enquiries")
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    status = {
        "app": "ok",
        "storage": "sqlite",
    }

    if USE_MONGO:

        try:

            mongo_client.admin.command(
                "ping"
            )

            status["storage"] = "mongodb"

        except Exception as e:

            return (
                jsonify(
                    {
                        "app": "ok",
                        "storage": "mongodb",
                        "error": str(e),
                    }
                ),
                500,
            )

    status["cloudinary"] = cloudinary_ready

    return jsonify(status)


# ============================================================
# JSON API
# ============================================================

def api_token_ok():

    auth = request.headers.get(
        "Authorization",
        ""
    )

    token = (
        auth.replace(
            "Bearer ",
            "",
            1
        ).strip()
        if auth.startswith(
            "Bearer "
        )
        else ""
    )

    expected = os.getenv(
        "API_ADMIN_TOKEN",
        ""
    )

    return bool(
        expected
        and token == expected
    )


def api_admin_required(fn):

    @wraps(fn)
    def wrapped(*args, **kwargs):

        if not api_token_ok():

            return (
                jsonify(
                    {
                        "error": (
                            "Admin authentication required"
                        )
                    }
                ),
                401,
            )

        return fn(*args, **kwargs)

    return wrapped


# ============================================================
# SITE API
# ============================================================

@app.get("/api/site")
def api_site():

    return jsonify(
        get_settings()
    )


@app.post("/api/auth/login")
def api_login():

    data = request.get_json(
        silent=True
    ) or {}

    if (
        str(data.get("username", ""))
        == os.getenv(
            "ADMIN_USERNAME",
            "admin"
        )
        and
        str(data.get("password", ""))
        == os.getenv(
            "ADMIN_PASSWORD",
            "admin123"
        )
    ):

        token = os.getenv(
            "API_ADMIN_TOKEN",
            ""
        )

        if not token:

            return (
                jsonify(
                    {
                        "error": (
                            "API_ADMIN_TOKEN "
                            "is not configured"
                        )
                    }
                ),
                500,
            )

        return jsonify(
            {
                "token": token
            }
        )

    return (
        jsonify(
            {
                "error": (
                    "Invalid username or password"
                )
            }
        ),
        401,
    )


# ============================================================
# PRODUCTS API
# ============================================================

@app.get("/api/products")
def api_products():

    cat = request.args.get(
        "category",
        ""
    ).strip()

    docs = list_docs(
        "products",
        True
    )

    if cat:

        docs = [
            x
            for x in docs
            if x.get("category") == cat
        ]

    return jsonify(docs)


@app.get("/api/products/<ident>")
def api_product(ident):

    p = get_doc(
        "products",
        ident
    )

    if p:

        return jsonify(p), 200

    return (
        jsonify(
            {
                "error": "Product not found"
            }
        ),
        404,
    )


# ============================================================
# CATEGORIES API
# ============================================================

@app.get("/api/categories")
def api_categories():

    return jsonify(
        list_docs(
            "categories",
            True
        )
    )


@app.get("/api/admin/categories")
@api_admin_required
def api_admin_categories():

    return jsonify(
        list_docs(
            "categories",
            False
        )
    )


@app.post("/api/categories")
@api_admin_required
def api_create_category():

    data = request.form.to_dict()
    f = request.files.get("image")

    data["name"] = data.get(
        "name",
        ""
    ).strip()

    data["description"] = data.get(
        "description",
        ""
    ).strip()

    data["active"] = (
        data.get(
            "active",
            "true"
        ).lower()
        in ("1", "true", "on", "yes")
    )

    data["sort_order"] = int(
        data.get(
            "sort_order"
        )
        or 0
    )

    if not data["name"]:

        return (
            jsonify(
                {
                    "error": (
                        "Category name is required"
                    )
                }
            ),
            400,
        )

    if f and f.filename:

        data["image"] = save_upload(
            f,
            "categories"
        )

    rid = save_doc(
        "categories",
        data
    )

    return (
        jsonify(
            get_doc(
                "categories",
                rid
            )
        ),
        201,
    )


@app.put("/api/categories/<ident>")
@api_admin_required
def api_update_category(ident):

    old = (
        get_doc(
            "categories",
            ident
        )
        or {}
    )

    data = request.form.to_dict()
    f = request.files.get("image")

    data["name"] = data.get(
        "name",
        ""
    ).strip()

    data["description"] = data.get(
        "description",
        ""
    ).strip()

    data["active"] = (
        data.get(
            "active",
            "false"
        ).lower()
        in ("1", "true", "on", "yes")
    )

    data["sort_order"] = int(
        data.get(
            "sort_order"
        )
        or 0
    )

    data["image"] = old.get(
        "image",
        ""
    )

    if not data["name"]:

        return (
            jsonify(
                {
                    "error": (
                        "Category name is required"
                    )
                }
            ),
            400,
        )

    old_name = old.get(
        "name",
        ""
    )

    if f and f.filename:

        data["image"] = save_upload(
            f,
            "categories"
        )

    save_doc(
        "categories",
        data,
        ident
    )

    # Keep product catalogue consistent
    # when category is renamed.

    if (
        old_name
        and old_name != data["name"]
    ):

        if USE_MONGO:

            mongo_col(
                "products"
            ).update_many(
                {
                    "category": old_name
                },
                {
                    "$set": {
                        "category": data["name"]
                    }
                },
            )

        else:

            con = sql_conn()

            con.execute(
                """
                UPDATE products
                SET category=?
                WHERE category=?
                """,
                (
                    data["name"],
                    old_name,
                ),
            )

            con.commit()
            con.close()

    return jsonify(
        get_doc(
            "categories",
            ident
        )
    )


@app.delete("/api/categories/<ident>")
@api_admin_required
def api_delete_category(ident):

    delete_doc(
        "categories",
        ident
    )

    return jsonify(
        {
            "message": "Category deleted"
        }
    )


# ============================================================
# CLIENTS API
# ============================================================

@app.get("/api/clients")
def api_clients():

    return jsonify(
        list_docs(
            "clients",
            True
        )
    )


@app.post("/api/clients")
@api_admin_required
def api_create_client():

    data = request.form.to_dict()
    f = request.files.get("logo")

    data["active"] = (
        data.get(
            "active",
            "true"
        ).lower()
        in ("1", "true", "on", "yes")
    )

    data["sort_order"] = int(
        data.get(
            "sort_order"
        )
        or 0
    )

    if f and f.filename:

        data["logo"] = save_upload(
            f,
            "clients"
        )

    rid = save_doc(
        "clients",
        data
    )

    return (
        jsonify(
            get_doc(
                "clients",
                rid
            )
        ),
        201,
    )


@app.put("/api/clients/<ident>")
@api_admin_required
def api_update_client(ident):

    old = (
        get_doc(
            "clients",
            ident
        )
        or {}
    )

    data = request.form.to_dict()
    f = request.files.get("logo")

    data["active"] = (
        data.get(
            "active",
            "false"
        ).lower()
        in ("1", "true", "on", "yes")
    )

    data["sort_order"] = int(
        data.get(
            "sort_order"
        )
        or 0
    )

    data["logo"] = old.get(
        "logo",
        ""
    )

    if f and f.filename:

        data["logo"] = save_upload(
            f,
            "clients"
        )

    save_doc(
        "clients",
        data,
        ident
    )

    return jsonify(
        get_doc(
            "clients",
            ident
        )
    )


@app.delete("/api/clients/<ident>")
@api_admin_required
def api_delete_client(ident):

    delete_doc(
        "clients",
        ident
    )

    return jsonify(
        {
            "message": "Client deleted"
        }
    )


# ============================================================
# EVENTS API
# ============================================================

@app.get("/api/events")
def api_events():

    return jsonify(
        list_docs(
            "events",
            True
        )
    )


@app.post("/api/events")
@api_admin_required
def api_create_event():

    data = request.form.to_dict()
    f = request.files.get("image")

    data["title"] = data.get(
        "title",
        ""
    ).strip()

    data["event_date"] = data.get(
        "event_date",
        ""
    ).strip()

    data["location"] = data.get(
        "location",
        ""
    ).strip()

    data["description"] = data.get(
        "description",
        ""
    ).strip()

    data["active"] = (
        data.get(
            "active",
            "true"
        ).lower()
        in ("1", "true", "on", "yes")
    )

    data["sort_order"] = int(
        data.get(
            "sort_order"
        )
        or 0
    )

    if not data["title"]:

        return (
            jsonify(
                {
                    "error": (
                        "Event title is required"
                    )
                }
            ),
            400,
        )

    if f and f.filename:

        data["image"] = save_upload(
            f,
            "events"
        )

    rid = save_doc(
        "events",
        data
    )

    return (
        jsonify(
            get_doc(
                "events",
                rid
            )
        ),
        201,
    )


@app.put("/api/events/<ident>")
@api_admin_required
def api_update_event(ident):

    old = (
        get_doc(
            "events",
            ident
        )
        or {}
    )

    data = request.form.to_dict()
    f = request.files.get("image")

    data["title"] = data.get(
        "title",
        ""
    ).strip()

    data["event_date"] = data.get(
        "event_date",
        ""
    ).strip()

    data["location"] = data.get(
        "location",
        ""
    ).strip()

    data["description"] = data.get(
        "description",
        ""
    ).strip()

    data["active"] = (
        data.get(
            "active",
            "false"
        ).lower()
        in ("1", "true", "on", "yes")
    )

    data["sort_order"] = int(
        data.get(
            "sort_order"
        )
        or 0
    )

    data["image"] = old.get(
        "image",
        ""
    )

    if not data["title"]:

        return (
            jsonify(
                {
                    "error": (
                        "Event title is required"
                    )
                }
            ),
            400,
        )

    if f and f.filename:

        data["image"] = save_upload(
            f,
            "events"
        )

    save_doc(
        "events",
        data,
        ident
    )

    return jsonify(
        get_doc(
            "events",
            ident
        )
    )


@app.delete("/api/events/<ident>")
@api_admin_required
def api_delete_event(ident):

    delete_doc(
        "events",
        ident
    )

    return jsonify(
        {
            "message": "Event deleted"
        }
    )


# ============================================================
# OFFERS API
# ============================================================

@app.get("/api/offers")
def api_offers():

    return jsonify(
        [
            x
            for x in list_docs(
                "offers",
                True
            )
            if x.get("active")
        ]
    )


# ============================================================
# ENQUIRIES API
# ============================================================

@app.post("/api/enquiries")
def api_enquiry():

    data = request.get_json(
        silent=True
    ) or {}

    clean = {
        k: str(
            data.get(
                k,
                ""
            )
        ).strip()
        for k in [
            "name",
            "email",
            "phone",
            "product",
            "message",
        ]
    }

    if (
        not clean["name"]
        or not clean["email"]
        or not clean["message"]
    ):

        return (
            jsonify(
                {
                    "error": (
                        "Name, email and message "
                        "are required"
                    )
                }
            ),
            400,
        )

    clean["created_at"] = (
        datetime.utcnow().isoformat()
    )

    save_doc(
        "enquiries",
        clean
    )

    return (
        jsonify(
            {
                "message": (
                    "Enquiry submitted successfully"
                )
            }
        ),
        201,
    )


@app.get("/api/enquiries")
@api_admin_required
def api_enquiries():

    return jsonify(
        list_docs(
            "enquiries"
        )
    )


@app.delete("/api/enquiries/<ident>")
@api_admin_required
def api_delete_enquiry(ident):

    delete_doc(
        "enquiries",
        ident
    )

    return jsonify(
        {
            "message": "Enquiry deleted"
        }
    )


# ============================================================
# WEBSITE SETTINGS API
# ============================================================

@app.put("/api/site")
@api_admin_required
def api_update_site():

    values = get_settings()

    payload = request.form.to_dict()

    if not payload:

        payload = (
            request.get_json(
                silent=True
            )
            or {}
        )

    for k in DEFAULT_SETTINGS:

        if (
            k not in (
                "logo_image",
                "hero_image",
            )
            and k in payload
        ):

            values[k] = str(
                payload[k]
            )

    for field, folder in [
        ("logo_image", "branding"),
        ("hero_image", "hero"),
    ]:

        f = request.files.get(field)

        if f and f.filename:

            values[field] = save_upload(
                f,
                folder
            )

    set_settings(values)

    return jsonify(values)


# ============================================================
# PRODUCTS ADMIN API
# ============================================================

@app.post("/api/products")
@api_admin_required
def api_create_product():

    data = request.form.to_dict()
    f = request.files.get("image")

    data["active"] = (
        data.get(
            "active",
            "true"
        ).lower()
        in ("1", "true", "on", "yes")
    )

    data["sort_order"] = int(
        data.get(
            "sort_order"
        )
        or 0
    )

    if f and f.filename:

        data["image"] = save_upload(
            f,
            "products"
        )

    rid = save_doc(
        "products",
        data
    )

    return (
        jsonify(
            get_doc(
                "products",
                rid
            )
        ),
        201,
    )


@app.put("/api/products/<ident>")
@api_admin_required
def api_update_product(ident):

    old = (
        get_doc(
            "products",
            ident
        )
        or {}
    )

    data = request.form.to_dict()
    f = request.files.get("image")

    data["active"] = (
        data.get(
            "active",
            "false"
        ).lower()
        in ("1", "true", "on", "yes")
    )

    data["sort_order"] = int(
        data.get(
            "sort_order"
        )
        or 0
    )

    data["image"] = old.get(
        "image",
        ""
    )

    if f and f.filename:

        data["image"] = save_upload(
            f,
            "products"
        )

    save_doc(
        "products",
        data,
        ident
    )

    return jsonify(
        get_doc(
            "products",
            ident
        )
    )


@app.delete("/api/products/<ident>")
@api_admin_required
def api_delete_product(ident):

    delete_doc(
        "products",
        ident
    )

    return jsonify(
        {
            "message": "Product deleted"
        }
    )


# ============================================================
# ADMIN STATS
# ============================================================

@app.get("/api/admin/stats")
@api_admin_required
def api_stats():

    return jsonify(
        {
            c: len(list_docs(c))
            for c in [
                "products",
                "categories",
                "clients",
                "events",
                "offers",
                "enquiries",
            ]
        }
    )


# ============================================================
# ERROR HANDLER
# ============================================================

@app.errorhandler(413)
def too_large(e):

    return (
        "File too large. Maximum upload size is 12 MB.",
        413,
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )