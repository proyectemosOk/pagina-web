document.addEventListener("DOMContentLoaded", function () {
    const menuItems = document.querySelectorAll('#nav-menu li a');
    const cards = document.querySelectorAll('.service-card');
    const sections = document.querySelectorAll('section');
  
    function mostrarSeccion(id) {
      sections.forEach(sec => {
        if (sec.id === id) {
          sec.classList.remove('hidden');
        } else {
          sec.classList.add('hidden');
        }
      });
    }
  
    menuItems.forEach(item => {
      item.addEventListener('click', function (e) {
        e.preventDefault();
  
        // Activar clase visual en menú
        menuItems.forEach(i => i.classList.remove('active'));
        this.classList.add('active');
  
        const href = this.getAttribute('href').replace('#', '');
        if (href) {
          mostrarSeccion(href);
        }
      });
    });
  
    cards.forEach(card => {
      const title = card.querySelector('.card-front h3');
      card.addEventListener('click', function () {
        if (!title) return;
  
        const text = title.textContent.trim().toLowerCase();
        const id = text.replace(/\s+/g, '-'); // convierte "Personal y Empresa" -> "personal-y-empresa"
        mostrarSeccion(id);
      });
    });
  });
  