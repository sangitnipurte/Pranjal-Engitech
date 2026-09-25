const API=(window.PRANJAL_CONFIG?.API_BASE||'').replace(/\/$/,'');
const api=async(path,opts={})=>{const r=await fetch(API+path,opts);let d={};try{d=await r.json()}catch{}if(!r.ok)throw new Error(d.error||`Request failed (${r.status})`);return d};

const fallbackProducts=[
['SPRAY GUARDS','PTFE BELOW GUARD'],['FLANGE GUARDS','PP FLANGE GUARDS'],['SPRAY GUARDS','PP FLANGE GUARDS'],['FLANGE GUARDS','PP BOX TYPE FLANGE GUARDS'],['FLANGE GUARDS','PP UNIVERSAL FLANGE GUARDS'],['FLANGE SHIELD','PTFE COATED FIBERGLASS FLANGE GUARDS SHIELDS'],['FLANGE GUARDS','SS304 STRIPS TYPE FLANGE GUARDS'],['FLANGE SHIELD','SS304 BOX TYPE FLANGE GUARDS'],['FLANGE SHIELD','SS316 STRIPS TYPE FLANGE GUARDS'],['FLANGE GUARDS','HDPE FLANGE GUARDS'],['FLANGE SHIELD','PTFE COATED FIBERGLASS FLANGE GUARDS SHIELDS WITH PVC TRANSPARENT COVER'],['FLANGE GUARDS','PVC FLANGE GUARDS'],['FLANGE GUARDS','PVC FLANGE GUARDS WITH TRANSPARENT WINDOW'],['FLANGE SHIELD','PTFE VALVE GUARDS'],['FLANGE SHIELD','PVC VALVE GUARDS'],['EARTHING JUMPERS','COPPER EARTHING JUMPERS'],['EARTHING JUMPERS','COPPER BRAIDED EARTHING JUMPERS'],['EARTHING JUMPERS','SS 304 BRAIDED JUMPER'],['EARTHING JUMPERS','COPPER WIRE TYPE JUMPER WITH ALUMINIUM LUGS'],['EARTHING JUMPERS','SS 304 JUMPER'],['EARTHING JUMPERS','ALUMINIUM JUMPER'],['EARTHING JUMPERS','COPPER WIRE TYPE JUMPER'],['EARTHING JUMPERS','COPPER BRAIDED JUMPER'],['FLANGE GUARDS','FRP FLANGE GUARDS'],['NEW PRODUCTS','FRP MOTOR CANOPY'],['FLANGE GUARDS','PP FLANGE GUARDS'],['FLANGE GUARDS','SS 304 COLLER TYPE FLANGE GUARDS'],['FLANGE GUARDS','SS 304 FLANGE GUARDS WITH SILICON ELASTOMERS'],['NEW PRODUCTS','PP LEG TYPE FLANGE COVERS'],['NEW PRODUCTS','PTFE BELLOWS'],['NEW PRODUCTS','PP PALL RING'],['NEW PRODUCTS','PTFE “TC” RING GASKET'],['NEW PRODUCTS','PP BALL VALVE FLANGE'],['FLANGE GUARDS','SS 304 FLANGE GUARDS WITH UNIVERSAL LOCK'],['NEW PRODUCTS','PP FOOT VALVE FLANGE END'],['SPRAY GUARDS','SS 304 FLANGE GUARDS WITH NOTCHE AND WING NUT'],['NEW PRODUCTS','HDPE BALL VALVE FLANGE END'],['SPRAY GUARDS','SS 304 FLANGE GUARDS WITH NOTCHE'],['NEW PRODUCTS','PPRC BALL VALVE FLNAGE END'],['NEW PRODUCTS','PP BALL VALVE NRV FLANGE END'],['NEW PRODUCTS','PP SCOOP'],['SPRAY GUARDS','SS FLANGE GUARDS SLOT AND NOTCHE'],['NEW PRODUCTS','PP SCRAPPER'],['SPRAY GUARDS','PTFE FLANGE GUARDS'],['NEW PRODUCTS','PP NUT AND BOLT'],['NEW PRODUCTS','PP SPADE'],['NEW PRODUCTS','PP STRAINER'],['NEW PRODUCTS','PTFE READY CUT GASKET'],['NEW PRODUCTS','PTFE ENVELOPE GASKET (0.5 + 0.5)'],['NEW PRODUCTS','SS 304 BOX TYPE VALVE GUARDS'],['NEW PRODUCTS','PTFE MILLED TYPE GASKET WITH 2MM AF GASKET'],['NEW PRODUCTS','PP FLANGE END COVERS END'],['NEW PRODUCTS','PTFE MILLED TYPE ENVELOPE WITH AF GASKET WITH SERRETION RING']
].map((x,i)=>({id:`local-${i+1}`,category:x[0],name:x[1],image:''}));

const fallbackClients=['ITC Limited','L&T Hydrocarbon Engineering','LANXESS','Aditya Birla Chemicals','Asian Paints','Aurobindo','Cipla','Coromandel','Mylan','Pidilite','Piramal','Rallis India','Teva API','Divi’s Laboratories','Dr. Reddy’s Laboratories','Finolex Industries','Grasim','Hindustan Unilever','IndianOil'].map((name,i)=>({id:`c-${i}`,name,logo:''}));

function productPlaceholder(name,category){
  const n=escapeHtml(name||'Industrial Product');
  const c=escapeHtml(category||'PRODUCT');
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="900" height="650"><rect width="100%" height="100%" fill="#f3f6fa"/><rect x="45" y="45" width="810" height="560" rx="24" fill="#fff" stroke="#d9e1ea"/><circle cx="450" cy="235" r="92" fill="#e8eef6"/><path d="M410 305L450 150L490 305" fill="none" stroke="#214b93" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/><path d="M418 270H482" stroke="#f36b21" stroke-width="18" stroke-linecap="round"/><text x="450" y="410" text-anchor="middle" font-family="Arial" font-size="24" font-weight="700" fill="#18345d">${c}</text><text x="450" y="455" text-anchor="middle" font-family="Arial" font-size="22" font-weight="700" fill="#1a2433">${n}</text><text x="450" y="505" text-anchor="middle" font-family="Arial" font-size="16" fill="#6b7787">PRODUCT IMAGE</text></svg>`)}`;
}
function img(v,name,category){
  if(!v)return productPlaceholder(name,category);
  if(String(v).startsWith('data:')||/^https?:\/\//i.test(v))return v;
  if(String(v).startsWith('/static/'))return API+v;
  if(String(v).startsWith('static/'))return API+'/'+v;
  if(String(v).startsWith('images/'))return API+'/static/'+v;
  if(String(v).startsWith('uploads/'))return API+'/static/'+v;
  if(String(v).startsWith('/uploads/'))return API+'/static'+v;
  return v;
}
function esc(s){return String(s??'').replace(/[&<>'"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[m]))}
const escapeHtml=esc;

async function loadSite(){
  try{const s=await api('/api/site');
    document.querySelectorAll('[data-company]').forEach(e=>e.textContent=s.company_name||'Pranjal Engitech (OPC) Private Limited');
    document.querySelectorAll('[data-short]').forEach(e=>e.textContent=s.short_name||'PRANJAL ENGITECH');
    document.querySelectorAll('[data-logo]').forEach(e=>e.src=img(s.logo_image,'Pranjal Engitech','LOGO'));
    const hero=document.querySelector('[data-hero]'); if(hero)hero.src=img(s.hero_image,'Industrial Safety & Engineering','HERO');
    document.querySelectorAll('[data-phone]').forEach(e=>e.textContent=s.phone||'');
    document.querySelectorAll('[data-email]').forEach(e=>e.textContent=s.email||'');
    document.querySelectorAll('[data-address]').forEach(e=>e.textContent=s.address||'');
    document.querySelectorAll('[data-hours]').forEach(e=>e.textContent=s.hours||'');
    const ann=document.querySelector('[data-announcement]');if(ann)ann.textContent=s.announcement||'Industrial Safety & Engineering Products';
    const h=document.querySelector('[data-hero-title]');if(h)h.textContent=s.hero_title||'Industrial Safety & Engineering Solutions';
    const ht=document.querySelector('[data-hero-text]');if(ht)ht.textContent=s.hero_text||'';
    const ax=document.querySelector('[data-about-text]');if(ax)ax.textContent=s.about_text||'';
    const ft=document.querySelector('[data-footer]');if(ft)ft.textContent=s.footer_text||'';
  }catch(e){console.warn('Site API unavailable:',e.message)}
}
async function loadHeaderCategories(){
  const nav=document.querySelector('[data-category-nav]'); if(!nav)return;
  let cs=[]; try{cs=await api('/api/categories')}catch(e){cs=[...new Set(fallbackProducts.map(p=>p.category))].map(name=>({name}))}
  nav.innerHTML=cs.map(c=>`<a href="products.html?category=${encodeURIComponent(c.name)}">${esc(c.name)}</a>`).join('');
}
function productCard(p){return `<a class="product-card" href="product.html?id=${encodeURIComponent(p.id)}"><div class="product-img"><img src="${img(p.image,p.name,p.category)}" alt="${esc(p.name)}" loading="lazy"></div><div class="product-body"><div class="product-cat">${esc(p.category||'')}</div><h3>${esc(p.name)}</h3><span class="small">View product details <b>→</b></span></div></a>`}
async function getProducts(category=''){
  try{return await api('/api/products'+(category?'?category='+encodeURIComponent(category):''))}catch(e){console.warn('Products API unavailable:',e.message);return category?fallbackProducts.filter(p=>p.category===category):fallbackProducts}
}
async function loadProducts(){const wrap=document.querySelector('[data-products]');if(!wrap)return;const cat=new URLSearchParams(location.search).get('category')||'';const ps=await getProducts(cat);wrap.innerHTML=ps.map(productCard).join('');const count=document.querySelector('[data-product-count]');if(count)count.textContent=ps.length}
async function loadCategories(){/* category cards removed from public homepage; kept as compatibility hook */}
function renderEventCard(e){return `<article class="event-card"><div class="event-image">${e.image?`<img src="${img(e.image,e.title,'EVENT')}" alt="${esc(e.title)}" loading="lazy">`:`<div class="event-placeholder"><span>EVENT &amp; EXHIBITION</span></div>`}</div><div class="event-body"><div class="event-date">${esc(e.event_date||'Event')}</div><h3>${esc(e.title)}</h3>${e.location?`<div class="event-location">${esc(e.location)}</div>`:''}<p>${esc(e.description||'')}</p></div></article>`}
async function loadEvents(){
  const page=document.querySelector('[data-events]'); const preview=document.querySelector('[data-events-preview]'); if(!page&&!preview)return;
  let es=[]; try{es=await api('/api/events')}catch(e){console.warn('Events API unavailable:',e.message)}
  if(page) page.innerHTML=es.length?es.map(renderEventCard).join(''):'<div class="notice">No events have been published yet.</div>';
  if(preview) preview.innerHTML=es.slice(0,3).map(renderEventCard).join('') || '<div class="notice">No events have been published yet.</div>';
}
async function loadClients(){
  const track=document.querySelector('[data-clients]');if(!track)return;let cs;
  try{cs=await api('/api/clients')}catch(e){cs=fallbackClients}
  // Render a duplicated track for seamless, non-jittery auto-scroll.
  const cards=cs.map(c=>`<div class="client-card">${c.logo?`<img src="${img(c.logo,c.name,'CLIENT')}" alt="${esc(c.name)}" loading="lazy">`:`<div class="client-name">${esc(c.name)}</div>`}</div>`).join('');
  track.innerHTML=cards+cards;
  const wrap=track.parentElement;
  document.querySelector('.client-prev')?.addEventListener('click',()=>track.scrollBy({left:-420,behavior:'smooth'}));
  document.querySelector('.client-next')?.addEventListener('click',()=>track.scrollBy({left:420,behavior:'smooth'}));
  let paused=false; wrap.addEventListener('mouseenter',()=>paused=true);wrap.addEventListener('mouseleave',()=>paused=false);wrap.addEventListener('touchstart',()=>paused=true,{passive:true});wrap.addEventListener('touchend',()=>setTimeout(()=>paused=false,1200),{passive:true});
  let last=performance.now(); const speed=34; function tick(now){const dt=Math.min(50,now-last);last=now;if(!document.hidden&&!paused&&track.scrollWidth>track.clientWidth){track.scrollLeft+=speed*dt/1000;const half=track.scrollWidth/2;if(track.scrollLeft>=half)track.scrollLeft-=half}requestAnimationFrame(tick)} requestAnimationFrame(tick);
}
async function loadProductDetail(){const el=document.querySelector('[data-product-detail]');if(!el)return;const id=new URLSearchParams(location.search).get('id');if(!id)return;try{const p=await api('/api/products/'+encodeURIComponent(id));el.innerHTML=detailHtml(p)}catch(e){const p=fallbackProducts.find(x=>x.id===id)||fallbackProducts.find(x=>x.name===id);el.innerHTML=p?detailHtml(p):'<div class="notice error">Product not found.</div>'}}
function detailHtml(p){return `<div class="about-grid"><div class="product-detail-image"><img src="${img(p.image,p.name,p.category)}" alt="${esc(p.name)}"></div><div><div class="eyebrow">${esc(p.category||'')}</div><h1>${esc(p.name)}</h1><p>${esc(p.description||'Product details and specifications can be updated from the admin panel.')}</p><h3>Specifications / Notes</h3><p style="white-space:pre-line">${esc(p.specs||'Available sizes and dimensions as per customer requirement.')}</p><a class="btn btn-primary" href="contact.html?product=${encodeURIComponent(p.name)}">Request Quote</a></div></div>`}
async function submitEnquiry(form){form.addEventListener('submit',async e=>{e.preventDefault();const data=Object.fromEntries(new FormData(form));const note=document.querySelector('[data-form-note]');try{await api('/api/enquiries',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});form.reset();if(note){note.className='notice success';note.textContent='Thank you. Your enquiry has been submitted.'}}catch(err){if(note){note.className='notice error';note.textContent='Unable to submit right now. Please contact us directly.'}}})}
document.addEventListener('DOMContentLoaded',()=>{loadSite();loadHeaderCategories();loadProducts();loadClients();loadEvents();loadProductDetail();const f=document.querySelector('[data-enquiry-form]');if(f)submitEnquiry(f);const y=document.querySelector('[data-year]');if(y)y.textContent=new Date().getFullYear();});
