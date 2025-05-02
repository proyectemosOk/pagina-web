from flask import Flask, request, send_file, render_template, jsonify
from fpdf import FPDF
import json, os
from datetime import datetime

app = Flask(__name__)

EMPRESA_PATH = 'datos/empresa.json'
COTIZACIONES_PATH = 'cotizaciones/cotizaciones.json'
FACURAS_PATH = 'cotizaciones/facturas.json'

def cargar_cotizaciones(ruta):
    if not os.path.exists(ruta):
        return []
    with open(ruta, 'r') as archivo:
        return json.load(archivo)

def guardar_cotizacion(data):
    cotizaciones = cargar_cotizaciones(COTIZACIONES_PATH)
    id_cotizacion = len(cotizaciones) + 1
    data['id'] = id_cotizacion
    cotizaciones.append(data)

    with open(COTIZACIONES_PATH, 'w') as archivo:
        json.dump(cotizaciones, archivo, indent=4)

    return id_cotizacion

def cargar_datos_empresa():
    if os.path.exists(EMPRESA_PATH):
        with open(EMPRESA_PATH, 'r') as archivo:
            return json.load(archivo)[0]
    return {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generar_cotizacion', methods=['POST'])
def generar_cotizacion():
    data = request.get_json()
    fecha_generacion = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    data["fecha"] = fecha_generacion
    id_cotizacion = guardar_cotizacion(data)
    empresa = cargar_datos_empresa()
    
    pdf = FPDF()
    pdf.add_page()

    # Fondo negro del encabezado
    pdf.set_fill_color(0, 0, 0)  # Negro
    pdf.rect(0, 0, 210, 30, 'F')  # Rectángulo fondo (A4 = 210mm ancho)

    # Logo centrado verticalmente en el fondo negro
    pdf.image(empresa.get("logo"), x=10, y=5, h=20)  # Ajusta 'h' para centrarlo en 30mm

    pdf.set_xy(10, 35)  # Baja todo lo demás

    # Datos Empresa vs Cliente
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(95, 8, empresa.get('Empresa', 'Nombre de la Empresa'), border=0)
    pdf.cell(95, 8, f"Nombre: {data.get('nombre', '').capitalize()}", ln=True, border=0)

    pdf.set_font("Arial", '', 11)
    pdf.set_x(10)
    pdf.cell(95, 8, f"NIT: {empresa.get('NIT', '')}", border=0)
    pdf.cell(95, 8, f"Cédula: {data.get('cedula', '')}", ln=True, border=0)

    pdf.set_x(10)
    pdf.cell(95, 8, f"Correo: {empresa.get('correo', '')}", border=0)
    pdf.cell(95, 8, f"Correo: {data.get('correo', '')}", ln=True, border=0)

    pdf.set_x(10)
    pdf.cell(95, 8, f"Celular: {empresa.get('celular', '')}", border=0)
    pdf.cell(95, 8, f"Celular: {data.get('celular', '')}", ln=True, border=0)

    pdf.set_x(10)
    pdf.cell(95, 8, f"ciudad: {empresa.get('ciudad', '')}", border=0)
    pdf.cell(95, 8, f"ciudad: {data.get('ciudad', '')}", ln=True, border=0)

    pdf.set_x(10)
    pdf.cell(95, 8, f"Dirección: {empresa.get('direccion', '')}", border=0)
    pdf.cell(95, 8, f"Dirección: {data.get('direccion', '')}", ln=True, border=0)

    fecha_generacion = datetime.now().strftime("%Y-%m-%d %H:%M")
    pdf.set_x(10)
    pdf.cell(95, 8, f"Fecha Generación: {fecha_generacion}", border=0)

    pdf.ln(10)

    # Título centrado
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"COTIZACIÓN #{id_cotizacion}", ln=True, align='C')
    pdf.ln(5)


    # Tabla
    # Encabezado de tabla
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(15, 8, "ITEM", 1, 0, 'C', 1)
    pdf.cell(85, 8, "DESCRIPCIÓN", 1, 0, 'C', 1)
    pdf.cell(15, 8, "UNID", 1, 0, 'C', 1)
    pdf.cell(20, 8, "CANT", 1, 0, 'C', 1)
    pdf.cell(25, 8, "VR UNIT", 1, 0, 'C', 1)
    pdf.cell(30, 8, "VR TOTAL", 1, 1, 'C', 1)

    # Filas con contenido
    pdf.set_font("Arial", '', 10)
    def celda(text, width, align='C'):
        pdf.cell(width, 8, str(text), 1, 0, align)

    celda("1.1", 15)
    celda("Panel solar 665W", 85, 'L')
    celda("und", 15)
    celda(data.get("paneles", 0), 20)
    celda(f"$ {data.get('precio_panel', 0):,.0f}", 25, 'R')
    celda(f"$ {data.get('paneles', 0) * data.get('precio_panel', 0):,.0f}", 30, 'R')
    pdf.ln()

    if data.get("baterias", 0):
        celda("1.2", 15)
        celda("Baterías", 85, 'L')
        celda("und", 15)
        celda(data.get("baterias", 0), 20)
        celda("$ 950,000", 25, 'R')
        celda(f"$ {data.get('baterias', 0) * 950000:,.0f}", 30, 'R')
        pdf.ln()

    celda("1.3", 15)
    celda(data.get("inversor", ""), 85, 'L')
    celda("und", 15)
    celda(1, 20)
    celda(f"$ {data.get('precio_inversor', 0):,.0f}", 25, 'R')
    celda(f"$ {data.get('precio_inversor', 0):,.0f}", 30, 'R')
    pdf.ln()

    celda("1.4", 15)
    celda("Instalación", 85, 'L')
    celda("global", 15)
    celda("1", 20)
    celda(f"$ {data.get('instalacion', 0):,.0f}", 25, 'R')
    celda(f"$ {data.get('instalacion', 0):,.0f}", 30, 'R')
    pdf.ln()

    # Total
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(160, 8, "TOTAL", 1, 0, 'R')
    pdf.cell(30, 8, f"$ {data.get('total', 0):,.0f}", 1, 1, 'R')

    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 8, "Observaciones: Incluye estructura, monitoreo y garantía por 5 años.")

    nombre_archivo = f"cotizacion_{id_cotizacion}_{data.get('nombre', '')}.pdf"
    ruta_pdf = os.path.join("cotizaciones", nombre_archivo)
    pdf.output(ruta_pdf)

    return send_file(ruta_pdf, as_attachment=True)


@app.route('/api/cotizaciones', methods=['GET'])
def obtener_cotizaciones():
    try:
        cotizaciones = cargar_cotizaciones(COTIZACIONES_PATH)
        
        # Ordenar cotizaciones por fecha (lo más reciente primero)
        cotizaciones = sorted(cotizaciones, key=lambda x: x['fecha'], reverse=True)

        return jsonify(cotizaciones)
    except FileNotFoundError:
        return jsonify({"mensaje": "No se encontraron cotizaciones."}), 404

# Ruta para cambiar una cotización existente (por ejemplo, cambiar su estado)
@app.route('/cambiar_cotizacion/<int:id>', methods=['POST'])
def cambiar_cotizacion(id):
    try:
        # Obtener los datos que se desean modificar desde la solicitud
        data_modificada = request.get_json()

        # Cargar las cotizaciones existentes
        with open('cotizaciones.json', 'r') as file:
            cotizaciones = json.load(file)

        # Buscar la cotización por ID
        cotizacion = next((c for c in cotizaciones if c['id'] == id), None)

        if cotizacion:
            # Modificar los datos de la cotización
            cotizacion.update(data_modificada)

            # Guardar las cotizaciones actualizadas
            with open('cotizaciones.json', 'w') as file:
                json.dump(cotizaciones, file, indent=4)

            return jsonify({"mensaje": "Cotización actualizada correctamente."}), 200
        else:
            return jsonify({"mensaje": "Cotización no encontrada."}), 404
    except Exception as e:
        return jsonify({"mensaje": str(e)}), 500

# Ruta para cargar facturas desde un archivo JSON
@app.route('/api/facturas', methods=['GET'])
def obtener_facturas():
    try:
        # Cargar las facturas desde un archivo JSON
        facturas = cargar_cotizaciones(FACURAS_PATH)
        
        # Ordenar facturas por fecha (lo más reciente primero)
        facturas = sorted(facturas, key=lambda x: x['fecha'], reverse=True)

        return jsonify(facturas)
    except FileNotFoundError:
        return jsonify({"mensaje": "No se encontraron facturas."}), 404

# Ruta para generar una nueva factura (ejemplo de cómo se agregan datos)
@app.route('/api/factura', methods=['POST'])
def agregar_factura():
    try:
        # Obtener los datos de la factura desde la petición
        data = request.get_json()

        # Cargar las facturas existentes
        with open('facturas.json', 'r') as file:
            facturas = json.load(file)

        # Agregar la nueva factura a la lista
        facturas.append(data)

        # Guardar las facturas actualizadas
        with open('facturas.json', 'w') as file:
            json.dump(facturas, file, indent=4)

        return jsonify({"mensaje": "Factura agregada correctamente."}), 201
    except Exception as e:
        return jsonify({"mensaje": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
