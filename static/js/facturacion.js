function cargarCotizaciones() {
    fetch('/api/cotizaciones', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
      .then(res => res.json())
      .then(data => {
        const contenedor = document.getElementById('lista-cotizaciones');
        contenedor.innerHTML = '';
        data.sort((a, b) => new Date(b.fecha) - new Date(a.fecha));
        data.forEach(c => {
          const item = document.createElement('div');
          item.className = 'item-cotizacion';
          item.innerHTML = `
            <span>${c.nombre_cliente} - ${c.fecha}</span>
            <div class="acciones">
              <button onclick="verCotizacion(${c.id})">Ver</button>
              <button onclick="facturarCotizacion(${c.id})">Facturar</button>
            </div>`;
          contenedor.appendChild(item);
        });
      })
      .catch(err => console.error("Error cargando cotizaciones:", err));
  }
  
  function cargarFacturas() {
    fetch('/api/facturas', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
      .then(res => res.json())
      .then(data => {
        const contenedor = document.getElementById('lista-facturas');
        contenedor.innerHTML = '';
        data.sort((a, b) => new Date(b.fecha) - new Date(a.fecha));
        data.forEach(f => {
          const item = document.createElement('div');
          item.className = 'item-factura';
          item.innerHTML = `
            <span>${f.nombre_cliente} - ${f.fecha}</span>
            <div class="acciones">
              <button onclick="verFactura(${f.id})">Ver</button>
            </div>`;
          contenedor.appendChild(item);
        });
      })
      .catch(err => console.error("Error cargando facturas:", err));
  }
  