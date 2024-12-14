from flask import Flask, request, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from email.message import EmailMessage
import smtplib
import os
import random
import string

# Función para generar un PIN aleatorio de 6 dígitos
def generar_pin():
    return ''.join(random.choices(string.digits, k=6))

def guardar_pin_en_bd(correo, pin):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Verificar si el correo está registrado en la tabla usuarios
        query_verificar_correo = "SELECT COUNT(*) FROM usuarios WHERE email = %s"
        cursor.execute(query_verificar_correo, (correo,))
        resultado = cursor.fetchone()

        if resultado and resultado[0] > 0:
            # El correo está registrado, proceder a guardar el PIN
            query_insertar_pin = "INSERT INTO registro_pins (correo, pin) VALUES (%s, %s)"
            cursor.execute(query_insertar_pin, (correo, pin))
            connection.commit()
            print(f"PIN guardado correctamente para el correo: {correo}")
        else:
            print(f"El correo {correo} no está registrado en la base de datos.")

        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error al guardar el PIN en la base de datos: {err}")

# Función para enviar el correo usando un HTML externo
def enviar_correo_con_html_externo(remitente, contraseña, destino, ruta_carpeta, nombre_archivo, pin):
    # Construir la ruta completa al archivo HTML
    ruta_archivo = os.path.join(ruta_carpeta, nombre_archivo)
    
    # Leer el contenido del archivo HTML
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            mensaje_html = archivo.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo HTML en {ruta_archivo}.")
        return
    
    # Reemplazar el marcador de lugar por el PIN generado
    mensaje_html = mensaje_html.replace("{{ pin }}", pin)
    
    asunto = "Verifica tu correo"
    
    # Crear el correo
    email = EmailMessage()
    email["From"] = remitente
    email["To"] = destino
    email["Subject"] = asunto
    email.set_content(mensaje_html, subtype='html')  # Configurar contenido como HTML
    
    try:
        # Conectar al servidor SMTP y enviar el correo
        stmp = smtplib.SMTP_SSL("smtp.gmail.com")
        stmp.login(remitente, contraseña)
        stmp.sendmail(remitente, destino, email.as_string())
        stmp.quit()
        print(f"Correo enviado exitosamente a {destino}.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

# Configuración de la base de datos
DB_CONFIG = {
    "host": "asdadssadsadasddassadadsadsdassadadsadsasd",
    "port": 3306,
    "user": "sdadssadsadad",
    "password": "adasdad",
    "database": "asdasdadad"
}

# Inicializar la aplicación Flask
app = Flask(__name__)
app.secret_key = 'clave-secreta-unica-y-segura'

# Ruta de la carpeta templates y nombre del archivo HTML
ruta_carpeta = "templates"
nombre_archivo = "mensaje.html"  # Cambia esto al nombre de tu archivo HTML

# Configuración del remitente y contraseña
remitente = "hernadezken123@gmail.com"
contraseña = "asdaasdasdasddadsaasasasdasdadasdadasdsadasd"  # Reemplaza esto por la contraseña de aplicación de Google

# Crear conexión global a la base de datos
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as e:
        print("Error al conectar a la base de datos:", e)
        return None

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        connection = get_db_connection()  # Asegúrate de tener esta función para conectar con la base de datos
        if connection:
            try:
                cursor = connection.cursor(dictionary=True, buffered=True)
                query = "SELECT * FROM usuarios WHERE email = %s LIMIT 1"
                cursor.execute(query, (email,))
                user = cursor.fetchone()  # Obtiene solo una fila

                # Verificar si el usuario existe y la contraseña es correcta
                if user and user['contrasena'] and check_password_hash(user['contrasena'], password):
                    return redirect(url_for('home'))  # Redirigir a la página de inicio (home)
                else:
                    flash("Correo o contraseña incorrectos", "error")  # Mostrar alerta de error
                    return redirect(url_for('login'))  # Redirigir al login con mensaje de error
            except mysql.connector.Error as err:
                print(f"Error en la consulta: {err}")
                flash("Error interno del servidor", "error")
                return redirect(url_for('login'))
            finally:
                cursor.close()
                connection.close()
        else:
            flash("Error al conectar a la base de datos", "error")
            return redirect(url_for('login'))

    return render_template('Login.html')

@app.route('/registro', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Capturar datos del formulario
        email = request.form.get('email')
        nombre = request.form.get('nombre')

        # Validar que no haya campos vacíos
        if not email or not nombre:
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for('register'))

        try:
            # Conectar a la base de datos
            connection = get_db_connection()
            if connection is None:
                flash("Error al conectar a la base de datos", "error")
                return redirect(url_for('register'))

            cursor = connection.cursor()

            # cambiar esto ahora para decir ya esta registrado
            # Intentar insertar el usuario, ignorando si el correo ya existe
            try:
                query_insertar_usuario = "INSERT INTO usuarios (email, nombre) VALUES (%s, %s)"
                cursor.execute(query_insertar_usuario, (email, nombre))
                connection.commit()
            except mysql.connector.Error as e:
                if e.errno == 1062:  # Error de duplicado
                    print(f"El correo {email} ya está registrado. Continuando sin error.")
                    pass  # Continuar sin hacer nada si el correo ya está en la base de datos
                else:
                    raise  # Si es otro error, lo lanza

            flash("Registro exitoso. Se ha enviado un PIN a tu correo.", "success")
            return envio_pin(destino=email)# Redirigir a la página de validación

        except mysql.connector.Error as e:
            # Manejar otros errores de la base de datos
            print(f"Error al registrar usuario: {e}")
            flash("Error en el registro. Intenta nuevamente.", "error")
            return redirect(url_for('register'))

        finally:
            # Cerrar la conexión de base de datos
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # En el caso de un GET, simplemente se renderiza el formulario
    return render_template('Register.html')

@app.route('/envio_pin', methods=['GET', 'POST'])
def envio_pin(destino):
    if request.method == 'POST':
        destino = request.form['email']
        pin = generar_pin()  # Generar el PIN
        # Guardar el PIN en la base de datos
        guardar_pin_en_bd(destino, pin)
        # Enviar el correo con el PIN
        enviar_correo_con_html_externo(remitente, contraseña, destino, ruta_carpeta, nombre_archivo, pin)
        # Redirigir inmediatamente a la página de validación
        return redirect(url_for('validacion', correo=destino))  # Redirige a '/validacion' y pasa el correo como parámetro
    
    return render_template('Validacion.html')  # Renderiza el formulario de envío de PIN en GET

@app.route('/reenvio/<destino>', methods=['GET','POST'])
def reenvio(destino):
    pin = generar_pin()  # Generar el PIN
    
    # Guardar el PIN en la base de datos
    guardar_pin_en_bd(destino, pin)
    
    # Enviar el correo con el PIN
    enviar_correo_con_html_externo(remitente, contraseña, destino, ruta_carpeta, nombre_archivo, pin)
    
    # Redirigir inmediatamente a la página de validación
    return redirect(url_for('validacion', correo=destino))  # Redirige a '/validacion' y pasa el correo como parámetro

@app.route('/validacion', methods=['GET', 'POST'])
def validacion():
    correo = request.args.get('correo')  # Obtener el correo desde los parámetros de la URL
    
    if not correo:  # Verificar si no se recibe el correo
        flash("Correo no proporcionado.", "error")
        return redirect(url_for('validacion'))  # Redirigir a la página principal u otra de tu elección
    
    if request.method == 'POST':
        pin_ingresado = request.form.get('pin')  # Captura el PIN ingresado
        
        # Validar que el PIN no esté vacío
        if not pin_ingresado:
            flash("Por favor ingrese el PIN.", "error")
            return redirect(url_for('validacion', correo=correo))  # Redirigir al formulario de validación

        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)

            # Consultar el último PIN registrado para el correo
            query = "SELECT * FROM registro_pins WHERE correo = %s ORDER BY fecha_creacion DESC LIMIT 1"
            cursor.execute(query, (correo,))
            registro = cursor.fetchone()

            if registro:
                # Verificar si el PIN es correcto y aún no ha expirado
                if registro['pin'] == pin_ingresado:
                    # Aquí podrías agregar la lógica de expiración del PIN si es necesario
                    return redirect(url_for('contrasena', correo=correo))  # Redirigir a la página de cambio de contraseña
                else:
                    flash("PIN incorrecto o expirado.", "error")
            else:
                flash("No se encontró un PIN registrado para este correo.", "error")
                
        except mysql.connector.Error as err:
            print(f"Error al consultar la base de datos: {err}")
            flash("Error en la validación. Intenta nuevamente.", "error")
        
        return redirect(url_for('validacion', correo=correo))  # Redirigir al formulario de validación

    return render_template('Validacion.html', correo=correo)  # Pasa el correo a la plantilla

#modificar para que sea mas simple
@app.route('/contrasena', methods=['GET', 'POST'])
def contrasena():
    # Captura el correo desde los parámetros de la URL
    correo = request.args.get('correo')

    # Verificar que el correo esté presente en los parámetros de la URL
    if not correo:
        print("Correo no proporcionado en la URL")
        message = "Correo no proporcionado"
        message_color = "red"
        return render_template('Password.html', message=message, message_color=message_color)

    print(f"Correo recibido: {correo}")
    
    cursor = None
    connection = None
    if request.method == 'POST':
        # Capturar la nueva contraseña y la confirmación
        nueva_contrasena = request.form.get('password')
        confirmar_contrasena = request.form.get('confirm-password')

        print(f"Contraseña nueva: {nueva_contrasena}")
        print(f"Confirmar contraseña: {confirmar_contrasena}")

        # Validar que las contraseñas coincidan
        if nueva_contrasena != confirmar_contrasena:
            print("Las contraseñas no coinciden")
            message = "Las contraseñas no coinciden"
            message_color = "red"
            return render_template('Password.html', correo=correo, message=message, message_color=message_color)

        # Validar que la contraseña cumpla con los requisitos
        if len(nueva_contrasena) < 8:
            print("La contraseña no cumple con el requisito de longitud")
            message = "La contraseña debe tener al menos 8 caracteres"
            message_color = "red"
            return render_template('Password.html', correo=correo, message=message, message_color=message_color)

        # Aquí puedes agregar más validaciones si es necesario

        try:
            # Generar el hash de la nueva contraseña
            hashed_password = generate_password_hash(nueva_contrasena)
            print(f"Contraseña hasheada: {hashed_password}")

            # Conectar a la base de datos
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()

            print("Conexión a la base de datos establecida")

            # Buscar el usuario por correo
            query_select = "SELECT id, email, nombre FROM usuarios WHERE email = %s"
            cursor.execute(query_select, (correo,))
            user = cursor.fetchone()

            if not user:
                # Si no se encuentra el usuario, mostrar mensaje de error
                print(f"Usuario no encontrado para el correo: {correo}")
                message = "Usuario no encontrado"
                message_color = "red"
                return render_template('Password.html', correo=correo, message=message, message_color=message_color)

            print(f"Usuario encontrado: {user}")

            # Leer cualquier resultado pendiente para evitar el error de 'Unread result'
            cursor.fetchall()  # Esto asegura que cualquier resultado pendiente se procese

            # Actualizar la contraseña en la base de datos
            query_contra = "UPDATE usuarios SET contrasena=%s WHERE email = %s"
            cursor.execute(query_contra, (hashed_password, correo))
            connection.commit()

            print(f"{cursor.rowcount} filas afectadas por la actualización")

            # Verificar si se actualizó la contraseña
            if cursor.rowcount > 0:
                message = "Contraseña actualizada con éxito"
                message_color = "green"
                # Redirigir al login ("/")
                return redirect('/', code=302)  # Redirige al login con código de redirección permanente

            else:
                message = "No se pudo actualizar la contraseña. Intenta nuevamente."
                message_color = "red"

            return render_template('Password.html', correo=correo, message=message, message_color=message_color)

        except mysql.connector.Error as err:
            # Manejar errores de base de datos
            print(f"Error en la base de datos: {err}")
            message = f"Error en la base de datos: {err}"
            message_color = "red"
            return render_template('Password.html', correo=correo, message=message, message_color=message_color)

        finally:
            # Cerrar la conexión y el cursor de la base de datos
            if cursor:
                cursor.close()
                print("Cursor cerrado")
            if connection:
                connection.close()
                print("Conexión cerrada")

    # Si la solicitud es GET, renderizar el formulario con el correo
    print("Método GET, mostrando formulario con correo")
    return render_template('Password.html', correo=correo)

@app.route("/olvido", methods=['GET', 'POST'])
def olvido():
    if request.method == 'POST':
        destino = request.form['email']
        pin = generar_pin()  # Generar el PIN
        # Guardar el PIN en la base de datos
        guardar_pin_en_bd(destino, pin)
        # Enviar el correo con el PIN
        enviar_correo_con_html_externo(remitente, contraseña, destino, ruta_carpeta, nombre_archivo, pin)
        # Redirigir inmediatamente a la página de validación
        return redirect(url_for('validacion', correo=destino))  # Redirige a '/validacion' y pasa el correo como parámetro
    
    return render_template('olvido.html')  # Renderiza el formulario de envío de PIN en GET

@app.route("/home", methods= ['POST','GET'])
def home():
    return render_template("home.html")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
