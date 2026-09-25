document.addEventListener('click',e=>{const el=e.target.closest('[data-confirm]');if(el&&!confirm(el.dataset.confirm))e.preventDefault();});
document.addEventListener('DOMContentLoaded',()=>{const t=document.getElementById('serverClients');if(t){setInterval(()=>{if(!document.hidden){t.scrollLeft+=1;if(t.scrollLeft+t.clientWidth>=t.scrollWidth-2)t.scrollLeft=0}},35)}});
