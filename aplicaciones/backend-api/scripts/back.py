import os
import json
import datetime
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, send_from_directory, Response
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId


# Obtenemos la ruta absoluta de la carpeta donde está el script actual
base_dir = os.path.dirname(os.path.abspath(__file__))
# Subimos un nivel para que pueda reconocer las carpetas templates y static
template_dir = os.path.join(base_dir, '..', 'templates')
static_dir = os.path.join(base_dir, '..', 'static')

app = Flask(__name__, template_folder = template_dir, static_folder = static_dir)


# Configuración de MongoDB
cliente = MongoClient('mongodb+srv://cristianxp_db_user:wpZqcQKcnUl4kGk4@cluster0.mdf0qyj.mongodb.net/')
db = cliente['gestora']


# RUTAS INTERNAS PARA ENLAZAR CARPETAS templates Y static
@app.route('/')
def vista_principal():
    return render_template('index.html', usuario="Programador")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, '..', 'static'),
        'favicon-32x32.png', mimetype='image/vnd.microsoft.icon')


#### MÉTODOS POST ####

## USUARIO
@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    coleccion = db['usuarios']
    datos = request.json

    # COMIENZO VALIDACIONES
    # Extraemos contraseña y los campos que deben ser únicos
    nombre_usuario = datos.get('nombre_usuario')
    email = datos.get('email')
    dni = datos.get('dni')
    passPlana = datos.get('contraseña')

    # Validación de existencia en formulario de campos obligatorios
    if not nombre_usuario or not passPlana or not email or not dni:
        return jsonify({"ERROR": "Debe rellenar los campos obligatorios (nombre de usuario, contraseña, email, dni)"}), 400

    # Comprobación de existencia en base de datos de los campos únicos anteriores
    usuario_existente = coleccion.find_one({
        "$or": [ # El operador $or devuelve un documento si coincide cualquiera de las condiciones 
            {"nombre_usuario": nombre_usuario},
            {"email": email},
            {"dni": dni}
        ]
    })

    # Si ya existe un usuario personalizamos el mensaje según qué campo falló
    if usuario_existente:
        if usuario_existente.get('email') == email:
            mensaje = "Ese email ya está registrado"
        elif usuario_existente.get('dni') == dni:
            mensaje = "Ese DNI ya está registrado"
        else:
            mensaje = "El nombre de usuario ya está en uso"
        
        return jsonify({"ERROR": mensaje}), 400

    # Si pasamos validaciones procedemos normalmente
    # Generamos el hash
    passHasheada = generate_password_hash(passPlana)

    # Creamos nuevo usuario
    nuevoUsuario = {
        "nombre_usuario": nombre_usuario,
        "contraseña": passHasheada,
        "nombre": datos.get('nombre'),
        "apellidos": datos.get('apellidos'),
        "dni": dni,
        "telefono": datos.get('telefono'),
        "email": email,
        "rol": datos.get('rol'),
        "fecha_alta": datetime.now(),
        "estado_suscripcion": True
    }

    # Insertarmos nuevo registro en la base de datos
    id_insertado = coleccion.insert_one(nuevoUsuario).inserted_id

    return jsonify({
        "mensaje": "Usuario creado",
        "id": str(id_insertado),
        "fecha_alta": nuevoUsuario["fecha_alta"].isoformat()
    }), 201

## ACTIVIDAD
@app.route('/actividades', methods=['POST'])
def crear_actividad():
    coleccion = db['actividades']
    datos = request.json

    # COMIENZO VALIDACIONES
    # Extraemos los campos que deben ser únicos
    nombre = datos.get('nombre')
    horariosRecibidos = datos.get('horario')
    capacidad_maxima = datos.get('capacidad_maxima')

    # Validación de existencia en formulario de campos obligatorios
    if not nombre or not horariosRecibidos or not capacidad_maxima:
        return jsonify({"ERROR": "Debe rellenar los campos obligatorios (nombre de actividad, horario, capacidad máxima)"}), 400
    
    # Comprobamos que 'horario' sea una lista
    if not isinstance(horariosRecibidos, list):
        return jsonify({"ERROR": "El campo 'horario' debe ser una lista de horarios"}), 400
    
    # Procesamos la lista de horarios
    listaHorariosProcesada = []

    for horario in horariosRecibidos:
        listaHorariosProcesada.append({
            "dia": horario.get('dia'),
            "hora_inicio": horario.get('hora_inicio'),
            "hora_fin": horario.get('hora_fin')
        })
    
    # Estructuramos el nuevo documento
    nuevaActividad = {
        "nombre": nombre,
        "descripcion": datos.get('descripcion', ""),
        "capacidad_maxima": capacidad_maxima,
        "horario": listaHorariosProcesada
    }

    try:
        # Insertarmos nuevo registro en la base de datos
        id_insertado = coleccion.insert_one(nuevaActividad).inserted_id

        return jsonify({
            "mensaje": "Actividad creada",
            "id": str(id_insertado)
        }), 201
    
    except Exception as ex:
        return jsonify({"ERROR": "No se pudo crear la actividad", "Detalle": str(ex)}), 500    

## SESIONES
@app.route('/actividades/<id>/sesiones', methods=['POST'])
def crear_sesion(id):
    actividad = db['actividades'].find_one({"_id": ObjectId(id)})

    if not actividad:
        return jsonify({"ERROR": "Actividad no encontrada"}), 404
    
    # Mapeo de días para Python
    diasSemana = {"Lunes": 0, "Martes": 1, "Miércoles": 2, "Jueves": 3, "Viernes": 4, "Sábado": 5, "Domingo": 6}
    horarios = actividad.get('horario', [])
    hoy = datetime.now().replace(hour = 0, minute = 0, second = 0, microsecond = 0)
    sesionesCreadas = 0

    # Generamos sesiones para los próximos 15 días
    for i in range(15):
        fecha_analizada = hoy + timedelta(days = i)
        dia_semana_str = list(diasSemana.keys())[list(diasSemana.values()).index(fecha_analizada.weekday())]

        for h in horarios:
            if h['dia'] == dia_semana_str:
                # Datos de la sesión individual
                nueva_sesion = {
                    "id_actividad": ObjectId(id),
                    "nombre": actividad['nombre'],
                    "fecha": fecha_analizada,
                    "hora_inicio": h['hora_inicio'],
                    "hora_fin": h['hora_fin'],
                    "capacidad_maxima": actividad['capacidad_maxima'],
                    "capacidad_actual": 0,
                    "estado": "programada" # cancelada, finalizada
                }
                
                # Evitar duplicados (mismo día y hora para esa actividad)
                filtro = {"actividad_id": ObjectId(id), "fecha": fecha_analizada, "hora_inicio": h['hora_inicio']}

                if not db['sesiones'].find_one(filtro):
                    db['sesiones'].insert_one(nueva_sesion)
                    sesionesCreadas += 1

    return jsonify({"mensaje": f"Se han generado {sesionesCreadas} sesiones"}), 201

## RESERVA
@app.route('/reservas', methods=['POST'])
def crear_reserva():
    coleccion = db['reservas']
    coleccionSesiones = db['sesiones']
    coleccionAsistencias = db['asistencias']
    datos = request.json

    id_usuario = datos.get('id_usuario')
    id_sesion = datos.get('id_sesion')

    if not id_usuario or not id_sesion:
        return jsonify({"ERROR": "Faltan datos (id_usuario, id_sesion)"}), 400

    try:
        # Validación preventiva de formato de IDs
        if not ObjectId.is_valid(id_usuario) or not ObjectId.is_valid(id_sesion):
            return jsonify({"ERROR": "El formato de los IDs enviados no es válido"}), 400

        # Comprobamos si el usuario ya ha reservado para evitar duplicados
        reservaPrevia = coleccion.find_one({
            "id_usuario": ObjectId(id_usuario),
            "id_sesion": ObjectId(id_sesion),
            "estado": "Confirmada"
        })

        if reservaPrevia:
            # Si existiese la reserva devolvemos un error 409
            return jsonify({"ERROR": "Se ha prevenido duplicado de reserva para misma sesión"}), 409
        
        # Buscamos sesión
        sesion = coleccionSesiones.find_one({"_id": ObjectId(id_sesion)})

        if not sesion:
            return jsonify({"ERROR": "La sesión no existe"}), 404

        # Comprobamos si hay capacidad disponible
        if sesion['capacidad_actual'] >= sesion['capacidad_maxima']:
            return jsonify({"ERROR": "La sesión está llena"}), 400

        # Creamos la reserva
        nuevaReserva = {
            "id_usuario": ObjectId(id_usuario),
            "id_sesion": ObjectId(id_sesion),
            "fecha_reserva": datetime.now(),
            "estado": "Confirmada" # Confirmada/Cancelada
        }
        
        id_reserva = coleccion.insert_one(nuevaReserva).inserted_id

        # Generamos automáticamente el registro de asistencia
        nuevaAsistencia = {
            "id_usuario": ObjectId(id_usuario),
            "id_sesion": ObjectId(id_sesion),
            "id_reserva": id_reserva,
            "estado": "Presente" # Presente/No presente/Cancelada
        }

        coleccionAsistencias.insert_one(nuevaAsistencia)

        # INCREMENTAMOS +1 A capacidad_actual EN LA SESIÓN USANDO $inc
        coleccionSesiones.update_one(
            {"_id": ObjectId(id_sesion)},
            {"$inc": {"capacidad_actual": 1}}
        )

        return jsonify({
            "mensaje": "Reserva realizada con éxito",
            "id_reserva": str(id_reserva),
        }), 201

    except Exception as e:
        return jsonify({"ERROR": "Ha ocurrido un error al intentar hacer la reserva", "Detalle": str(e)}), 400

## ASISTENCIA
@app.route('/asistencias', methods=['POST'])
def crear_asistencia():
    coleccion = db['asistencias']
    coleccionReservas = db['reservas']
    datos = request.json

    id_usuario = datos.get('id_usuario')
    id_sesion = datos.get('id_sesion')

    if not id_usuario or not id_sesion:
        return jsonify({"ERROR": "Faltan datos (id_usuario, id_sesion)"}), 400

    try:
        # Verificamos si existe reserva para este usuario y sesión
        reserva = coleccionReservas.find_one({
            "id_usuario": ObjectId(id_usuario),
            "id_sesion": ObjectId(id_sesion),
            "estado": "Confirmada"
        })

        if not reserva:
            return jsonify({"ERROR": "No existe una reserva para este usuario/sesión"}), 404
        
        # Evitamos duplicados
        asistenciaPrevia = coleccion.find_one({
            "id_usuario": ObjectId(id_usuario),
            "id_sesion": ObjectId(id_sesion)
        })

        if asistenciaPrevia:
            return jsonify({"ERROR": "La asistencia ya fue registrada anteriormente"}), 400
        
        # Si se superan las validaciones anteriores creamos registro de asistencia
        nuevaAsistencia = {
            "id_usuario": ObjectId(id_usuario),
            "id_sesion": ObjectId(id_sesion),
            "id_reserva": reserva['_id'],
            "estado": "Presente" # Presente/No presente/Cancelada
        }

        id_insertado = coleccion.insert_one(nuevaAsistencia).inserted_id

        return jsonify({
            "mensaje": "Asistencia registrada correctamente",
            "id_asistencia": str(id_insertado)
        }), 201
    
    except Exception as ex:
        return jsonify({"ERROR": "No se pudo registrar asistencia", "Detalle": str(ex)}), 400


#### MÉTODOS GET ####

## USUARIOS
@app.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    coleccion = db['usuarios']
    usuarios = []

    for doc in coleccion.find():
        # Extraemos la fecha y la formateamos si existe
        fecha_alta = doc.get('fecha_alta')
        # Comprobamos si la variable es de tipo datetime y la convertimos a String
        if isinstance(fecha_alta, datetime):
            fecha_alta = fecha_alta.isoformat()

        usuarios.append({
            "id": str(doc['_id']),
            "nombre_usuario": doc.get('nombre_usuario'),
            "nombre": doc.get('nombre'),
            "apellidos": doc.get('apellidos'),
            "dni": doc.get('dni'),
            "telefono": doc.get('telefono'),
            "email": doc.get('email'),
            "rol": doc.get('rol'),
            "fecha_alta": fecha_alta,
            "estado_suscripcion": doc.get('estado_suscripcion')
        })

    # Devuelve json con campos ordenados alfabéticamente
    return Response(
        json.dumps(usuarios, sort_keys=False),
        mimetype='application/json'
    ), 200

## USUARIO/ID
@app.route('/usuarios/<id>', methods=['GET'])
def obtener_usuario(id):
    coleccion = db['usuarios']

    try:
        # Convertimos el string que viene de la URL a un ObjectId de MongoDB
        usuario = coleccion.find_one({"_id": ObjectId(id)})
        
        if usuario:
            # Extraemos la fecha y la formateamos si existe
            fecha_alta = usuario.get('fecha_alta')
            # Comprobamos si la variable es de tipo datetime y la convertimos a String
            if isinstance(fecha_alta, datetime):
                fecha_alta = fecha_alta.isoformat()

            respuesta = {
                "id": str(usuario['_id']),
                "nombre_usuario": usuario.get('nombre_usuario'),
                "nombre": usuario.get('nombre'),
                "apellidos": usuario.get('apellidos'),
                "dni": usuario.get('dni'),
                "telefono": usuario.get('telefono'),
                "email": usuario.get('email'),
                "rol": usuario.get('rol'),
                "fecha_alta": fecha_alta,
                "estado_suscripcion": usuario.get('estado_suscripcion')
            }

            return Response(
                json.dumps(respuesta, sort_keys=False),
                mimetype='application/json'
            ), 200
        
        else:
            return jsonify({"ERROR": "Usuario no encontrado"}), 404
            
    except Exception as e:
        # Esto captura errores si el ID enviado no tiene el formato válido de MongoDB
        return jsonify({"ERROR": "ID no válido"}), 400

## ACTIVIDADES
@app.route('/actividades', methods=['GET'])
def obtener_actividades():
    coleccion = db['actividades']
    actividades = []

    for doc in coleccion.find():
        actividades.append({
            "id": str(doc['_id']),
            "nombre": doc.get('nombre'),
            "descripcion": doc.get('descripcion'),
            "capacidad_maxima": doc.get('capacidad_maxima'),
            "horario": doc.get('horario')
        })

    # Devuelve json con campos ordenados alfabéticamente
    return Response(
        json.dumps(actividades, sort_keys=False),
        mimetype='application/json'
    ), 200

## ACTIVIDAD/ID
@app.route('/actividades/<id>', methods=['GET'])
def obtener_actividad(id):
    coleccion = db['actividades']

    try:
        actividad = coleccion.find_one({"_id": ObjectId(id)})

        if actividad:
            respuesta = {
                "id": str(actividad['_id']),
                "nombre": actividad.get('nombre'),
                "descripcion": actividad.get('descripcion'),
                "capacidad_maxima": actividad.get('capacidad_maxima'),
                "horario": actividad.get('horario')
            }

            return Response(
                json.dumps(respuesta, sort_keys=False),
                mimetype='application/json'
            ), 200
        
        else:
            return jsonify({"ERROR": "Actividad no encontrada"}), 404
    
    except Exception as e:
        # Esto captura errores si el ID enviado no tiene el formato válido de MongoDB
        return jsonify({"ERROR": "ID no válido"}), 400

## SESIONES
@app.route('/sesiones', methods=['GET'])
def obtener_sesiones():
    coleccion = db['sesiones']
    sesiones = []

    for documento in coleccion.find():
        # Extraemos la fecha y la formateamos si existe
        fechaSesion = documento.get('fecha')
        # Comprobamos si la variable es de tipo datetime y la convertimos a String
        if isinstance(fechaSesion, datetime):
            fechaSesion = fechaSesion.isoformat()

        sesiones.append({
            "id": str(documento['_id']),
            "id_actividad": str(documento['id_actividad']),
            "nombre": documento['nombre'],
            "fecha": fechaSesion,
            "hora_inicio": documento['hora_inicio'],
            "hora_fin": documento['hora_fin'],
            "capacidad_maxima": documento['capacidad_maxima'],
            "capacidad_actual": documento['capacidad_actual'],
            "estado": documento['estado']
        })
    
    return Response(
        json.dumps(sesiones, sort_keys=False),
        mimetype='application/json'
    ), 200

## SESION/ID
@app.route('/sesiones/<id>', methods=['GET'])
def obtener_sesion(id):
    coleccion = db['sesiones']
    
    try:
        sesion = coleccion.find_one({"_id": ObjectId(id)})
        # Extraemos la fecha y la formateamos si existe
        fechaSesion = sesion.get('fecha')
        # Comprobamos si la variable es de tipo datetime y la convertimos a String
        if isinstance(fechaSesion, datetime):
            fechaSesion = fechaSesion.isoformat()

        if sesion:
            respuesta = {
                "id": str(sesion['_id']),
                "id_actividad": str(sesion['id_actividad']),
                "nombre": sesion['nombre'],
                "fecha": fechaSesion,
                "hora_inicio": sesion['hora_inicio'],
                "hora_fin": sesion['hora_fin'],
                "capacidad_maxima": sesion['capacidad_maxima'],
                "capacidad_actual": sesion['capacidad_actual'],
                "estado": sesion['estado']
            }

            return Response(
                json.dumps(respuesta, sort_keys=False),
                mimetype='application/json'
            ), 200
        
        else:
            return jsonify({"ERROR": "Sesión no encontrada"}), 404
    
    except Exception as e:
        # Esto captura errores si el ID enviado no tiene el formato válido de MongoDB
        return jsonify({"ERROR": "ID no válido"}), 400

## RESERVAS
@app.route('/reservas', methods=['GET'])
def obtener_reservas():
    coleccion = db['reservas']
    reservas = []

    for documento in coleccion.find():
        # Extraemos la fecha y la formateamos si existe
        fechaReserva = documento.get('fecha_reserva')
        # Comprobamos si la variable es de tipo datetime y la convertimos a String
        if isinstance(fechaReserva, datetime):
            fechaReserva = fechaReserva.isoformat()

        reservas.append({
            "id": str(documento['_id']),
            "id_usuario": str(documento['id_usuario']),
            "id_sesion": str(documento['id_sesion']),
            "fecha_reserva": fechaReserva,
            "estado": documento.get('estado')
        })

    return Response(
        json.dumps(reservas, sort_keys=False),
        mimetype='application/json'
    ), 200

## RESERVA/ID
@app.route('/reservas/<id>', methods=['GET'])
def obtener_reserva(id):
    coleccion = db['reservas']
    
    try:
        reserva = coleccion.find_one({"_id": ObjectId(id)})
        # Extraemos la fecha y la formateamos si existe
        fechaReserva = reserva.get('fecha_reserva')
        # Comprobamos si la variable es de tipo datetime y la convertimos a String
        if isinstance(fechaReserva, datetime):
            fechaReserva = fechaReserva.isoformat()

        if reserva:
            respuesta = {
                "id": str(reserva['_id']),
                "id_usuario": str(reserva['id_usuario']),
                "id_sesion": str(reserva['id_sesion']),
                "fecha_reserva": fechaReserva,
                "estado": reserva.get('estado')
            }

            return Response(
                json.dumps(respuesta, sort_keys=False),
                mimetype='application/json'
            ), 200
        
        else:
            return jsonify({"ERROR": "Reserva no encontrada"}), 404
    
    except Exception as e:
        # Esto captura errores si el ID enviado no tiene el formato válido de MongoDB
        return jsonify({"ERROR": "ID no válido"}), 400

## ASISTENCIAS
@app.route('/asistencias', methods=['GET'])
def obtener_asistencias():
    coleccion = db['asistencias']
    asistencias = []

    for documento in coleccion.find():
        # Extraemos la fecha y la formateamos si existe
        check_in = documento.get('check_in')
        # Comprobamos si la variable es de tipo datetime y la convertimos a String
        if isinstance(check_in, datetime):
            check_in = check_in.isoformat()

        asistencias.append({
            "id": str(documento['_id']),
            "id_usuario": str(documento['id_usuario']),
            "id_sesion": str(documento['id_sesion']),
            "id_reserva": str(documento['id_reserva']),
            "check_in": check_in
        })

    return Response(
        json.dumps(asistencias, sort_keys=False),
        mimetype='application/json'
    ), 200

## ASISTENCIA/ID
@app.route('/asistencias/<id>', methods=['GET'])
def obtener_asistencia(id):
    coleccion = db['asistencias']
    
    try:
        asistencia = coleccion.find_one({"_id": ObjectId(id)})
        # Extraemos la fecha y la formateamos si existe
        check_in = asistencia.get('check_in')
        # Comprobamos si la variable es de tipo datetime y la convertimos a String
        if isinstance(check_in, datetime):
            check_in = check_in.isoformat()

        if asistencia:
            respuesta = {
                "id": str(asistencia['_id']),
                "id_usuario": str(asistencia['id_usuario']),
                "id_sesion": str(asistencia['id_sesion']),
                "id_reserva": str(asistencia['id_reserva']),
                "check_in": check_in
            }

            return Response(
                json.dumps(respuesta, sort_keys=False),
                mimetype='application/json'
            ), 200
        
        else:
            return jsonify({"ERROR": "Asistencia no encontrada"}), 404
    
    except Exception as e:
        # Esto captura errores si el ID enviado no tiene el formato válido de MongoDB
        return jsonify({"ERROR": "ID no válido"}), 400


#### MÉTODOS PUT ####

## USUARIO/ID
@app.route('/usuarios/<id>', methods=['PUT'])
def actualizar_usuario(id):
    coleccion = db['usuarios']

    try:
        # Obtener los nuevos datos del cuerpo de la petición
        datosActualizados = request.json

        if not datosActualizados:
            return jsonify({"ERROR": "No se proporcionaron datos para actualizar"}), 400

        # Si el usuario envía una nueva contraseña, debemos hashearla
        if 'password' in datosActualizados:
            datosActualizados['password'] = generate_password_hash(datosActualizados['password'])

        # Ejecutar la actualización en MongoDB
        # Usamos $set para modificar solo los campos enviados sin borrar el resto
        resultado = coleccion.update_one(
            {"_id": ObjectId(id)},
            {"$set": datosActualizados}
        )

        # Verificar si se encontró y actualizó
        if resultado.matched_count == 0:
            return jsonify({"ERROR": "Usuario no encontrado"}), 404
        
        return jsonify({
            "mensaje": "Usuario actualizado correctamente",
            "modificado": resultado.modified_count
        }), 200

    except Exception as ex:
        return jsonify({"ERROR": "ID no válido o error interno", "Detalle": str(ex)}), 400

## ACTIVIDAD/ID
@app.route('/actividades/<id>', methods=['PUT'])
def actualizar_actividad(id):
    coleccion = db['actividades']
    
    try:
        # Obtener datos del cuerpo de la petición
        datosActualizados = request.json

        if not datosActualizados:
            return jsonify({"ERROR": "No se proporcionaron datos para actualizar"}), 400

        # Preprocesar datos si es necesario
        # Si envían capacidad_max, nos aseguramos de que sea entero
        if 'capacidad_maxima' in datosActualizados:
            datosActualizados['capacidad_maxima'] = int(datosActualizados['capacidad_maxima'])

        # Si envían horario, validamos que sea una lista (el nuevo formato que definimos)
        if 'horario' in datosActualizados:
            if not isinstance(datosActualizados['horario'], list):
                return jsonify({"ERROR": "El campo 'horario' debe ser una lista"}), 400

        # Ejecutar la actualización
        resultado = coleccion.update_one(
            {"_id": ObjectId(id)},
            {"$set": datosActualizados}
        )

        # Verificar resultado
        if resultado.matched_count == 0:
            return jsonify({"ERROR": "Actividad no encontrada"}), 404
        
        return jsonify({
            "mensaje": "Actividad actualizada con éxito",
            "detalles": {
                "encontrados": resultado.matched_count,
                "modificados": resultado.modified_count
            }
        }), 200

    except Exception as ex:
        return jsonify({"ERROR": "ID no válido o error interno", "Detalle": str(ex)}), 400

## SESION/ID
@app.route('/sesiones/<id>', methods=['PUT'])
def actualizar_sesion(id):
    coleccion = db['sesiones']
    
    try:
        datos = request.json

        if not datos:
            return jsonify({"ERROR": "No hay datos para actualizar"}), 400

        # Si actualizan capacidad, forzar valor entero
        if 'capacidad_maxima' in datos:
            datos['capacidad_maxima'] = int(datos['capacidad_maxima'])

        resultado = coleccion.update_one({"_id": ObjectId(id)}, {"$set": datos})

        if resultado.matched_count == 0:
            return jsonify({"ERROR": "Sesión no encontrada"}), 404
        
        # Lo normal es actualizar estado (programada, finalizada, cancelada)
        return jsonify({"mensaje": "Sesión actualizada correctamente"}), 200
    
    except Exception as ex:
        return jsonify({"ERROR": "ID no válido o error interno", "Detalle": str(ex)}), 400

## RESERVA/ID
@app.route('/reservas/<id>', methods=['PUT'])
def actualizar_reserva(id):
    coleccion = db['reservas']
    coleccionSesiones = db['sesiones']
    coleccionAsistencias = db['asistencias']
    
    try:
        datos = request.json

        if not datos:
            return jsonify({"ERROR": "No hay datos para actualizar"}), 400

        # Buscamos reserva actual para conocer su estado y la sesión vinculada
        reservaActual = coleccion.find_one({"_id": ObjectId(id)})
        
        if not reservaActual:
            return jsonify({"ERROR": "Reserva no encontrada"}), 404

        nuevoEstadoReserva = datos.get('estado')
        anteriorEstadoReserva = reservaActual.get('estado')
        id_sesion = reservaActual.get('id_sesion')

        # Esta variable determinará si al final del filtrado se cancela o no la reserva
        seCancelaReserva = True

        # Actualización de plazas ($inc)
        # Si la reserva cambia de 'Confirmada' a 'Cancelada', liberamos plaza (-1)
        if anteriorEstadoReserva == "Confirmada" and nuevoEstadoReserva == "Cancelada":
            # Obtenemos datos de sesión para saber hora de inicio
            sesion = coleccionSesiones.find_one({"_id": id_sesion})

            # Preparamos variable horaSesion
            h, m = map(int, sesion['hora_inicio'].split(':'))
            horaSesion = sesion['fecha'].replace(hour = h, minute = m, second = 0, microsecond = 0)

            # Preparamos el espacio de tiempo de la cancelación
            horaActual = datetime.now()
            tiempoCancelacion = horaSesion - horaActual

            # Comprobamos el límite de tiempo
            if tiempoCancelacion > timedelta(minutes = 15):
                # Si se cancela hasta 15 minutos del inicio de la sesión se libera la plaza
                coleccionSesiones.update_one({"_id": id_sesion}, {"$inc": {"capacidad_actual": -1}})
                estadoAsistencia = "Cancelada"
            
            else:
                # Si se cancela cuando faltan 15 minutos o menos para el comienzo de la sesión no se libera plaza
                estadoAsistencia = "No presente"
                seCancelaReserva = False
                mensajeEstado = "No se ha cancelado la reserva por aviso tardío, la plaza sigue ocupada"

            # Actualizamos estado de asistencia
            coleccionAsistencias.update_one(
                {"id_reserva": ObjectId(id)},
                {"$set": {
                    "id_usuario": reservaActual['id_usuario'],
                    "id_sesion": id_sesion,
                    "estado": estadoAsistencia
                }},
                upsert = True # Forzamos
            )

        # Sólo se actualiza la reserva si se ha hecho a tiempo, sino se mantiene 'Confirmada'
        if seCancelaReserva:
            # Actualizamos reserva en base de datos
            coleccion.update_one(
                {"_id": ObjectId(id)},
                {"$set": datos}
            )
            mensajeEstado = "Reserva cancelada a tiempo, plaza liberada"

        return jsonify({
            "mensaje": mensajeEstado,
            "modificado": seCancelaReserva
        }), 200

    except Exception as ex:
        return jsonify({"ERROR": "ID no válido o error interno", "Detalle": str(ex)}), 400

## ASISTENCIA/ID
@app.route('/asistencias/<id>', methods=['PUT'])
def actualizar_asistencia(id):
    coleccion = db['asistencias']
    
    try:
        datos = request.json
        resultado = coleccion.update_one({"_id": ObjectId(id)}, {"$set": datos})

        if resultado.matched_count == 0:
            return jsonify({"ERROR": "Registro de asistencia no encontrado"}), 404

        return jsonify({"mensaje": "Asistencia actualizada"}), 200
    
    except Exception as ex:
        return jsonify({"ERROR": "ID no válido", "Detalle": str(ex)}), 400


#### MÉTODOS DELETE ####

## USUARIO/ID
@app.route('/usuarios/<id>', methods=['DELETE'])
def eliminar_usuario(id):
    coleccion = db['usuarios']

    try:
        # Intentamos eliminar el documento que coincida con el ObjectId
        resultado = coleccion.delete_one({"_id": ObjectId(id)})

        # Si el conteo de eliminados es 1, todo salió bien
        if resultado.deleted_count == 1:
            return jsonify({"mensaje": f"Usuario con ID {id} eliminado correctamente"}), 200
        else:
            return jsonify({"ERROR": "No se encontró el usuario para eliminar"}), 404

    except Exception as e:
        return jsonify({"ERROR": "ID no válido", "Detalle": str(e)}), 400

## ACTIVIDAD/ID
@app.route('/actividades/<id>', methods=['DELETE'])
def eliminar_actividad(id):
    coleccion = db['actividades']

    try:
        # Intentamos eliminar el documento que coincida con el ObjectId
        resultado = coleccion.delete_one({"_id": ObjectId(id)})

        # Si el conteo de eliminados es 1, todo salió bien
        if resultado.deleted_count == 1:
            return jsonify({"mensaje": f"Actividad con ID {id} eliminada correctamente"}), 200
        else:
            return jsonify({"ERROR": "No se encontró la actividad para eliminar"}), 404

    except Exception as e:
        return jsonify({"ERROR": "ID no válido", "Detalle": str(e)}), 400

## SESION/ID
@app.route('/sesiones/<id>', methods=['DELETE'])
def eliminar_sesion(id):
    coleccion = db['sesiones']
    coleccionReservas = db['reservas']

    try:
        # Borramos sesión
        resultado = coleccion.delete_one({"_id": ObjectId(id)})

        if resultado.deleted_count == 1:
            # Borramos en cascada TODAS LAS RESERVAS ASOCIADAS a dicha sesión
            coleccionReservas.delete_many({"id_sesion": ObjectId(id)})
            return jsonify({"mensaje": "Sesión y reservas asociadas eliminadas"}), 200
        
        else:
            return jsonify({"ERROR": "No se encontró la sesión"}), 404
        
    except Exception as e:
        return jsonify({"ERROR": "ID no válido", "Detalle": str(e)}), 400

## RESERVA/ID
@app.route('/reservas/<id>', methods=['DELETE'])
def eliminar_reserva(id):
    coleccion = db['reservas']
    coleccionSesiones = db['sesiones']

    try:
        # Buscamos la reserva para ver su estado actual antes de borrarla
        reserva = coleccion.find_one({"_id": ObjectId(id)})
        
        if not reserva:
            return jsonify({"ERROR": "Reserva no encontrada"}), 404

        id_sesion = reserva.get('id_sesion')
        estadoReserva = reserva.get('estado')

        # Eliminamos la reserva de la base de datos
        resultado = coleccion.delete_one({"_id": ObjectId(id)})

        if resultado.deleted_count == 1:
            # SOLO restamos si la reserva estaba 'confirmada'
            if estadoReserva == "Confirmada":
                coleccionSesiones.update_one(
                    {"_id": ObjectId(id_sesion)},
                    {"$inc": {"capacidad_actual": -1}}
                )

                return jsonify({"mensaje": "Reserva eliminada y cupo actualizado"}), 200
            
            # Si estaba 'cancelada', la plaza ya se liberó en su momento
            else:
                return jsonify({"mensaje": "Reserva eliminada (no hubo cambios en el aforo de la sesión)"}), 200
        
        return jsonify({"ERROR": "No se pudo eliminar"}), 500

    except Exception as e:
        return jsonify({"ERROR": "ID no válido", "Detalle": str(e)}), 400

## ASISTENCIA/ID
@app.route('/asistencias/<id>', methods=['DELETE'])
def eliminar_asistencia(id):
    coleccion = db['asistencias']
    
    try:
        resultado = coleccion.delete_one({"_id": ObjectId(id)})

        if resultado.deleted_count == 1:
            return jsonify({"mensaje": "Registro de asistencia eliminado"}), 200
        
        return jsonify({"ERROR": "No se encontró la asistencia"}), 404
    
    except Exception as e:
        return jsonify({"ERROR": "ID no válido", "Detalle": str(e)}), 400



if __name__ == '__main__':
    print('\nIniciando Backend...\n')
    # app.run(debug = True, use_reloader = False)
    app.run(debug = True)

# GUÍAS
# https://j2logo.com/leccion-1-la-primera-aplicacion-flask/
# https://www.youtube.com/watch?v=QBx7sLNM0_A