(()=>{
  const BOOKING_URLS={all:"https://www.booking.com/hotel/ec/palmar-del-rio-gran.es-mx.html",gran:"https://www.booking.com/hotel/ec/palmar-del-rio-gran.es-mx.html"};
  const header=document.querySelector("[data-header]");
  const toggle=document.querySelector("[data-menu-toggle]");
  const menu=document.querySelector("[data-menu]");
  const track=(eventName,details={})=>{window.dataLayer=window.dataLayer||[];window.dataLayer.push({event:eventName,...details})};
  const closeMenu=()=>{if(!toggle||!menu)return;toggle.setAttribute("aria-expanded","false");menu.classList.remove("is-open");document.body.classList.remove("menu-open")};
  toggle?.addEventListener("click",()=>{const isOpen=toggle.getAttribute("aria-expanded")==="true";toggle.setAttribute("aria-expanded",String(!isOpen));menu?.classList.toggle("is-open",!isOpen);document.body.classList.toggle("menu-open",!isOpen)});
  menu?.querySelectorAll("a").forEach(link=>link.addEventListener("click",closeMenu));
  document.addEventListener("keydown",event=>{if(event.key==="Escape")closeMenu()});
  const updateHeader=()=>header?.classList.toggle("is-scrolled",window.scrollY>24);
  updateHeader();window.addEventListener("scroll",updateHeader,{passive:true});
  document.querySelectorAll("[data-booking]").forEach(link=>{const property=link.dataset.booking||"all";link.setAttribute("href",BOOKING_URLS[property]||BOOKING_URLS.all);link.addEventListener("click",()=>track("click_booking",{property,link_text:link.textContent.trim()}))});
  document.querySelectorAll("[data-whatsapp]").forEach(link=>link.addEventListener("click",()=>track("click_whatsapp",{link_text:link.textContent.trim()})));
  document.querySelectorAll("[data-call]").forEach(link=>link.addEventListener("click",()=>track("click_call")));
  document.querySelectorAll("[data-directions]").forEach(link=>link.addEventListener("click",()=>track("click_directions")));
  document.querySelectorAll("[data-resource]").forEach(link=>link.addEventListener("click",()=>track("click_resource",{resource:link.dataset.resource})));
  document.querySelectorAll("[data-social]").forEach(link=>link.addEventListener("click",()=>track("click_social",{network:link.dataset.social})));
  const contactForm=document.querySelector("[data-contact-form]");
  contactForm?.addEventListener("submit",event=>{
    event.preventDefault();
    const data=new FormData(contactForm);
    const hotels=data.getAll("hotel");
    const subject="Consulta desde hotelespalmardelrio.com";
    const body=["Nombre: "+data.get("name"),"Correo: "+data.get("email"),"Hotel: "+(hotels.length?hotels.join(", "):"Gran Hotel Palmar del Río"),"","Mensaje:",""+data.get("message")].join("\n");
    const status=contactForm.querySelector("[data-form-status]");
    if(status)status.textContent="Abriendo tu aplicación de correo…";
    track("submit_contact",{hotels:hotels.join("|")||"unspecified"});
    window.location.href="mailto:hotelespalmardelrio@hotmail.com?subject="+encodeURIComponent(subject)+"&body="+encodeURIComponent(body);
  });
  document.querySelectorAll("[data-year]").forEach(node=>{node.textContent=new Date().getFullYear()});
  const revealItems=document.querySelectorAll(".reveal");
  if("IntersectionObserver" in window&&!window.matchMedia("(prefers-reduced-motion: reduce)").matches){const observer=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add("is-visible");observer.unobserve(entry.target)}})},{threshold:.12,rootMargin:"0px 0px -40px"});revealItems.forEach(item=>observer.observe(item))}else{revealItems.forEach(item=>item.classList.add("is-visible"))}
  const parallaxItems=[...document.querySelectorAll("[data-parallax]")];
  if(parallaxItems.length&&!window.matchMedia("(prefers-reduced-motion: reduce)").matches&&!window.matchMedia("(max-width: 700px)").matches){
    let frame;
    const updateParallax=()=>{parallaxItems.forEach(item=>{const rect=item.parentElement.getBoundingClientRect();const progress=(rect.top+rect.height/2-window.innerHeight/2)/window.innerHeight;const distance=Number(item.dataset.parallax)||24;item.style.setProperty("--parallax-y",String(Math.max(-distance,Math.min(distance,-progress*distance)))+"px")});frame=null};
    const requestParallax=()=>{if(!frame)frame=requestAnimationFrame(updateParallax)};
    updateParallax();window.addEventListener("scroll",requestParallax,{passive:true});window.addEventListener("resize",requestParallax,{passive:true});
  }
})();
