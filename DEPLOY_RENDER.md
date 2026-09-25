# Render deployment — MongoDB Atlas + Cloudinary

## 1. MongoDB Atlas
Create a free Atlas project and database. Create a database user and copy the Python/PyMongo connection string.
For a Render-hosted app, add a network access entry that allows the Render service to reach Atlas (for a simple setup, Atlas commonly uses `0.0.0.0/0`; restrict it further if your deployment architecture allows).

## 2. Cloudinary
Create a Cloudinary account and copy:
- Cloud name
- API key
- API secret

The admin panel uploads product, category, offer, logo and hero images to Cloudinary when these values are configured.

## 3. GitHub
Push this project to your GitHub repository. Never commit `.env`.

## 4. Render Web Service
Create a Web Service from the GitHub repository.

Build Command:
```text
pip install -r requirements.txt
```

Start Command:
```text
gunicorn app:app
```

## 5. Environment Variables on Render
Add:
```text
SECRET_KEY=long-random-secret
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-strong-password
MONGO_URI=mongodb+srv://...
DB_NAME=pranjal_engitech
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
```

## 6. Test
After deployment open:
```text
https://YOUR-RENDER-URL/health
```
Expected cloud mode response contains:
```json
{"app":"ok","storage":"mongodb","cloudinary":true}
```
Then open `/admin/login` and upload a test image/product.

## Important
Do not use Render's local `static/uploads` as the permanent production image store. In cloud mode the website stores uploaded images in Cloudinary and information in MongoDB.
