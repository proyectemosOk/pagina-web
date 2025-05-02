let contadorCotizaciones = 1;

document.addEventListener('DOMContentLoaded', () => {
    const btn = document.querySelector('button[onclick="mostrarResultados()"]');
    btn.addEventListener('click', cotizar);
});

function cotizar() {
    const potenciaRequerida = parseFloat(document.getElementById("potencia-requerida").value);
    const potenciaPanel = parseFloat(document.getElementById("potencia-paneles").value);
    const horasSol = parseFloat(document.getElementById("horas-sol").value);
    const autonomia = document.getElementById("autonomia").value;
    const perdidas = parseFloat(document.getElementById("factor-perdidas").value) || 0;

    if (isNaN(potenciaRequerida) || isNaN(potenciaPanel) || isNaN(horasSol)) {
        alert("Por favor completa todos los campos numéricos.");
        return;
    }

    const energiaDiaria = potenciaRequerida / horasSol;
    const factorTotal = 1 + (perdidas / 100);
    const energiaConPerdidas = energiaDiaria * factorTotal;
    const paneles = Math.ceil(energiaConPerdidas / potenciaPanel);

    const precioPanel = 680000;
    const costoPaneles = paneles * precioPanel;
    const tipoInversor = autonomia === "offgrid" ? "Inversor OffGrid 5kW" : "Inversor OnGrid 3.5kW";
    const numBaterias = autonomia === "offgrid" ? Math.ceil(potenciaRequerida / 1200) : 0;
    const precioInversor = autonomia === "offgrid" ? 4200000 : 2500000;
    const precioBateria = 950000;
    const costoBaterias = numBaterias * precioBateria;
    const instalacion = 1400000;

    const total = costoPaneles + precioInversor + costoBaterias + instalacion;

    const contenedor = document.getElementById("resultados");
    const nuevaCotizacion = document.createElement("div");
    nuevaCotizacion.classList.add("cotizacion-card");

    const idDetalle = `detalle-cotizacion-${contadorCotizaciones}`;
    nuevaCotizacion.innerHTML = `
        <div class="cotizacion-resumen">
            <h4>Cotización #${contadorCotizaciones}</h4>
            <p><strong>Total estimado:</strong> $${total.toLocaleString()} COP</p>
            <div>
                <button onclick="document.getElementById('${idDetalle}').classList.toggle('hidden')">
                    Ver Detalle
                </button>
                <button onclick="generarPDF('${idDetalle}', ${contadorCotizaciones}, ${paneles}, '${autonomia === "offgrid" ? "OffGrid" : "OnGrid"}', '${tipoInversor}', ${numBaterias}, ${precioPanel}, ${costoPaneles + precioInversor + costoBaterias}, ${instalacion}, ${total})">
                    Generar PDF
                </button>
            </div>
        </div>
        <div class="cotizacion-detalle hidden" id="${idDetalle}">
            <table class="tabla-cotizacion">
                <thead>
                    <tr>
                        <th>ITEM</th>
                        <th>DESCRIPCIÓN</th>
                        <th>UNID</th>
                        <th>CANT</th>
                        <th>VR UNITARIO</th>
                        <th>VR TOTAL</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>1.1</td>
                        <td>Panel solar 665W</td>
                        <td>und</td>
                        <td>${paneles}</td>
                        <td>$${precioPanel.toLocaleString()}</td>
                        <td>$${(paneles * precioPanel).toLocaleString()}</td>
                    </tr>
                    ${numBaterias > 0 ? `
                    <tr>
                        <td>1.2</td>
                        <td>Batería</td>
                        <td>und</td>
                        <td>${numBaterias}</td>
                        <td>$${precioBateria.toLocaleString()}</td>
                        <td>$${(numBaterias * precioBateria).toLocaleString()}</td>
                    </tr>` : ""}
                    <tr>
                        <td>1.3</td>
                        <td>Inversor (${tipoInversor})</td>
                        <td>und</td>
                        <td>1</td>
                        <td>$${precioInversor.toLocaleString()}</td>
                        <td>$${precioInversor.toLocaleString()}</td>
                    </tr>
                    <tr>
                        <td>1.4</td>
                        <td>Instalación</td>
                        <td>global</td>
                        <td>1</td>
                        <td>$${instalacion.toLocaleString()}</td>
                        <td>$${instalacion.toLocaleString()}</td>
                    </tr>
                    <tr>
                        <td colspan="5"><strong>Total</strong></td>
                        <td><strong>$${total.toLocaleString()}</strong></td>
                    </tr>
                </tbody>
            </table>
        </div>
        <hr>
    `;

    contenedor.style.display = "block";
    contenedor.appendChild(nuevaCotizacion);

    contadorCotizaciones++;
}

function generarPDF(idDetalle, numero, paneles, sistema, inversor, baterias, precioPanel, subtotal, instalacion, total) {
    const nombre = document.getElementById("cliente-nombre").value;
    const cedula = document.getElementById("cliente-cedula").value;
    const celular = document.getElementById("cliente-celular").value;
    const correo = document.getElementById("cliente-correo").value;
    const ciudad = document.getElementById("cliente-ciudad").value;
    const direccion = document.getElementById("cliente-direccion").value;


    const data = {
        nombre,
        cedula,
        celular,
        correo,
        numero,
        ciudad,
        direccion,
        paneles,
        sistema,
        inversor,
        baterias,
        precio_panel: precioPanel,
        subtotal,
        instalacion,
        total
    };

    fetch('/generar_cotizacion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(resp => resp.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `cotizacion_${numero}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        })
        .catch(err => console.error('Error al generar PDF:', err));
}
