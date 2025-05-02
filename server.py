from flask import Flask, request, send_file, render_template, jsonify
from fpdf import FPDF
import json, os
from datetime import datetime

app = Flask(__name__)

EMPRESA_PATH = 'datos/empresa.json'
COTIZACIONES_PATH = 'cotizaciones/cotizaciones.json'
FACURAS_PATH = 'facturaciones/facturaciones.json'


def cargar_cotizaciones(ruta):
    if not os.path.exists(ruta):
        return []
    with open(ruta, 'r') as archivo:
        return json.load(archivo)
    
# Buscar cotización por ID
def obtener_cotizacion_por_id(cotizacion_id):
    cotizaciones = cargar_cotizaciones(COTIZACIONES_PATH)
    for cot in cotizaciones:
        if cot["id"] == cotizacion_id:
            return cot
    return None
# Obtener todas las facturas
def cargar_facturas(ruta):
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Generar un nuevo ID de factura
def generar_nuevo_id_factura():
    facturas = cargar_facturas(FACURAS_PATH)
    if not facturas:
        return 1
    return max(f["id"] for f in facturas) + 1

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

def marcar_cotizacion_como_facturada(cotizacion_id):
    with open(COTIZACIONES_PATH, 'r', encoding='utf-8') as f:
        cotizaciones = json.load(f)

    for cot in cotizaciones:
        if cot.get('id') == cotizacion_id:
            cot['facturada'] = True
            break

    with open(COTIZACIONES_PATH, 'w', encoding='utf-8') as f:
        json.dump(cotizaciones, f, indent=4, ensure_ascii=False)

def guardar_factura(nueva_factura):
    # Cargar las facturas existentes
    facturas = cargar_facturas(FACURAS_PATH)
    
    # Agregar la nueva factura a la lista
    facturas.append(nueva_factura)
    
    # Asegurarse de que el directorio existe
    os.makedirs(os.path.dirname(FACURAS_PATH), exist_ok=True)
    
    # Guardar todas las facturas de nuevo en el archivo
    with open(FACURAS_PATH, 'w', encoding='utf-8') as f:
        json.dump(facturas, f, indent=4, ensure_ascii=False)

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
        no_facturadas = [c for c in cotizaciones if not c.get('facturada', False)]
        return jsonify(no_facturadas)
    except FileNotFoundError:
        return jsonify({"mensaje": "No se encontraron cotizaciones."}), 404

# Ruta para cambiar una cotización existente (por ejemplo, cambiar su estado)
@app.route('/api/facturar/<int:cotizacion_id>', methods=['POST'])
def facturar_cotizacion(cotizacion_id):
    cotizacion = obtener_cotizacion_por_id(cotizacion_id)
    if not cotizacion:
        return jsonify({"mensaje": "Cotización no encontrada"}), 404

    nueva_factura = cotizacion
    guardar_factura(nueva_factura)
    marcar_cotizacion_como_facturada(cotizacion_id)
    return jsonify({"mensaje": "Factura generada exitosamente", "factura": nueva_factura}), 200

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

@app.route('/api/factura/pdf/<int:factura_id>', methods=['GET'])
def generar_pdf_factura(factura_id):
    from fpdf import FPDF
    from flask import send_file
    import os

    # Cargar facturas
    with open('facturaciones/facturaciones.json', 'r', encoding='utf-8') as f:
        facturas = json.load(f)

    factura = next((f for f in facturas if f['id'] == factura_id), None)
    if not factura:
        return jsonify({"error": "Factura no encontrada"}), 404

    pdf = FPDF()
    pdf.add_page()

    # Logo
    if os.path.exists("static/img/logo.png"):
        pdf.image("static/img/logo.png", x=10, y=8, w=40)

    # Encabezado de empresa
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "Eco Energy Latin America", ln=True, align='R')
    pdf.set_font("Arial", '', 10)
    pdf.cell(200, 5, "contacto@ecoenergyla.com", ln=True, align='R')
    pdf.cell(200, 5, "Tel: +57 300 123 4567", ln=True, align='R')
    pdf.cell(200, 5, "www.ecoenergyla.com", ln=True, align='R')
    pdf.ln(10)

    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"FACTURA #{factura['id']}", ln=True, align='C')
    pdf.ln(5)

    # Datos del cliente y fecha
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, f"Cliente: {factura['cliente']}", ln=True)
    pdf.cell(100, 10, f"Fecha: {factura['fecha']}", ln=True)
    pdf.ln(5)

    # Encabezados tabla
    pdf.set_font("Arial", 'B', 10)
    col_widths = [15, 70, 20, 20, 30, 30]
    headers = ["ITEM", "DESCRIPCIÓN", "UNID", "CANT", "VR UNITARIO", "VR TOTAL"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1, align='C')
    pdf.ln()

    # Detalles
    pdf.set_font("Arial", size=10)
    for item in factura["detalle"]:
        pdf.cell(col_widths[0], 10, str(item["item"]), border=1)
        pdf.cell(col_widths[1], 10, item["descripcion"], border=1)
        pdf.cell(col_widths[2], 10, item["unid"], border=1)
        pdf.cell(col_widths[3], 10, str(item["cantidad"]), border=1)
        pdf.cell(col_widths[4], 10, f"${item['vr_unitario']:,}", border=1, align='R')
        pdf.cell(col_widths[5], 10, f"${item['total']:,}", border=1, align='R')
        pdf.ln()

    # Total general
    total_general = sum(item["total"] for item in factura["detalle"])
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(sum(col_widths[:-1]), 10, "TOTAL GENERAL", border=1, align='R')
    pdf.cell(col_widths[-1], 10, f"${total_general:,}", border=1, align='R')
    pdf.ln(15)

    nombre_pdf = f"factura_{factura_id}.pdf"
    pdf.output(nombre_pdf)
    return send_file(nombre_pdf, as_attachment=True)

if __name__ == '__main__':
    import socket
    host_ip = socket.gethostbyname(socket.gethostname())  # Obtiene IP automáticamente
    app.run(debug=True, host=host_ip, port=5000)
    print(f"Servidor corriendo en http://{host_ip}:5000")