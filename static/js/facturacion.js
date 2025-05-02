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
            <span>${c.nombre} - ${c.fecha}</span>
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
      console.log("Datos recibidos de la API:", data); // <-- Esto muestra la respuesta completa
      
      const contenedor = document.getElementById('lista-facturas');
      contenedor.innerHTML = '';
      
      // Verifica si data es un array antes de ordenar
      if (Array.isArray(data)) {
        data.sort((a, b) => new Date(b.fecha) - new Date(a.fecha));
        
        data.forEach(factura => {
          console.log("Procesando factura:", factura); // <-- Muestra cada factura individual
          
          const fila = document.createElement('div');
          fila.className = 'factura-item';
          fila.innerHTML = `
            <strong>Factura #${factura.id}</strong><br>
            Cliente: ${factura.cliente}<br>
            Fecha: ${factura.fecha}<br>
            <button onclick="verFactura(${factura.id})">👁️ Ver</button>
            <button onclick="descargarFacturaPDF(${factura.id})">📄 PDF</button>
          `;
          contenedor.appendChild(fila);
        });
      } else {
        console.LOG("La respuesta no es un array:", data);
      }
    })
    .catch(error => {
      console.LOG("Error cargando facturas:", error);
    });
}

document.addEventListener('DOMContentLoaded', () => {
  cargarCotizaciones();
  cargarFacturas();

});