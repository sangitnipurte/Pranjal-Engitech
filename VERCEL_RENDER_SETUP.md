# Pranjal Engitech — Vercel + Render + MongoDB Atlas + Cloudinary

## Architecture
- Vercel: `frontend/` static public website and `/admin` CMS UI
- Render: Flask backend in the project root (`app.py`)
- MongoDB Atlas: persistent products, clients, categories, enquiries and site settings
- Cloudinary: persistent logo, hero, product and client images

## Render
Build command: `pip install -r requirements.txt`
Start command: `gunicorn app:app`
Set environment variables from `.env.example`, including `REQUIRE_MONGO=true` and `REQUIRE_CLOUDINARY=true`.

## Vercel
Set Root Directory to `frontend`. No build command is required.
Before deployment, edit `frontend/config.js`:
`window.PRANJAL_CONFIG={API_BASE:'https://YOUR-RENDER-SERVICE.onrender.com'};`
The public website has no Admin link. The CMS is directly reachable at `/admin`.

## Local
Terminal 1: `pip install -r requirements.txt` then `python app.py`
Terminal 2: `cd frontend` then `python -m http.server 5500`
Website: `http://127.0.0.1:5500/`
Admin: `http://127.0.0.1:5500/admin/`
