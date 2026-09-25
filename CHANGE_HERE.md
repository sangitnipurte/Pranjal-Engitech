# Where to change everything

## No-code changes — use Admin Panel
Open `/admin/login`.

### Admin → Website Settings
Change:
- Company name
- Short name
- Tagline
- Phone
- Email
- Address
- Business hours
- Announcement bar
- Hero title/text
- About title/text
- Google Maps URL
- WhatsApp
- Facebook / Instagram / LinkedIn
- Footer text
- Logo image
- Hero image

### Admin → Products
- Add product
- Edit product
- Change category
- Change description/specifications
- Upload product image
- Hide/show product
- Change sort order
- Delete product
- Discard by using the New/Cancel action

### Admin → Categories
- Add/edit category
- Add category image
- Hide/show category
- Delete category

### Admin → Offers
- Add/edit offer
- Offer image
- Offer text
- Button text/link
- Activate/deactivate
- Delete

An active offer is displayed as a homepage popup.

### Admin → Enquiries
View and delete customer quote requests.

## Code changes
- `app.py` — backend, routes, database logic, default data
- `templates/index.html` — home page
- `templates/products.html` — catalogue
- `templates/product.html` — product detail
- `templates/about.html` — about page
- `templates/contact.html` — enquiry form
- `templates/base.html` — header/footer
- `templates/admin/` — admin UI
- `static/css/style.css` — colors, layout, spacing, fonts
- `static/js/app.js` — small browser interactions

## Product names
The seeded catalogue uses the product names/range shown on the public Pranjal Polymers site. Verify every specification, certification, warranty and company claim before publishing it under Pranjal Engitech.
