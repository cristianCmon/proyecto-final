import os
import json
import datetime as fecha
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


# RUTAS
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
        "fecha_alta": fecha.datetime.now(),
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
        "capacidad_actual": 0,
        "horario": listaHorariosProcesada,
        "fecha_creacion": fecha.datetime.now()
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

## RESERVA
@app.route('/reservas', methods=['POST'])
def crear_reserva():
    coleccion = db['reservas']
    pass

## ASISTENCIA
@app.route('/asistencias', methods=['POST'])
def crear_asistencia():
    coleccion = db['asistencias']
    pass


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
        if isinstance(fecha_alta, fecha.datetime):
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

    # return jsonify(usuarios), 200 # Devuelve json con campos ordenados alfabéticamente
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
            if isinstance(fecha_alta, fecha.datetime):
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
            # return jsonify(respuesta), 200
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
        # Extraemos la fecha y la formateamos si existe
        fecha_creacion = doc.get('fecha_creacion')
        # Comprobamos si la variable es de tipo datetime y la convertimos a String
        if isinstance(fecha_creacion, fecha.datetime):
            fecha_creacion = fecha_creacion.isoformat()

        actividades.append({
            "id": str(doc['_id']),
            "nombre": doc.get('nombre'),
            "descripcion": doc.get('descripcion'),
            "capacidad_maxima": doc.get('capacidad_maxima'),
            "capacidad_actual": doc.get('capacidad_actual'),
            "horario": doc.get('horario'),
            "fecha_creacion": fecha_creacion
        })

    # return jsonify(actividades), 200 # Devuelve json con campos ordenados alfabéticamente
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
            # Extraemos la fecha y la formateamos si existe
            fecha_creacion = actividad.get('fecha_creacion')
            # Comprobamos si la variable es de tipo datetime y la convertimos a String
            if isinstance(fecha_creacion, fecha.datetime):
                fecha_creacion = fecha_creacion.isoformat()

            respuesta = {
                "id": str(actividad['_id']),
                "nombre": actividad.get('nombre'),
                "descripcion": actividad.get('descripcion'),
                "capacidad_maxima": actividad.get('capacidad_maxima'),
                "capacidad_actual": actividad.get('capacidad_actual'),
                "horario": actividad.get('horario'),
                "fecha_creacion": fecha_creacion
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

## RESERVAS
@app.route('/reservas', methods=['GET'])
def obtener_reservas():
    coleccion = db['reservas']
    pass

## RESERVA/ID
@app.route('/reservas/<id>', methods=['GET'])
def obtener_reserva(id):
    coleccion = db['reservas']
    pass

## ASISTENCIAS
@app.route('/asistencias', methods=['GET'])
def obtener_asistencias():
    coleccion = db['asistencias']
    pass

## ASISTENCIA/ID
@app.route('/asistencias/<id>', methods=['GET'])
def obtener_asistencia(id):
    coleccion = db['asistencias']
    pass


#### MÉTODOS PUT ####

## USUARIO/ID
@app.route('/usuarios/<id>', methods=['PUT'])
def actualizar_usuario(id):
    coleccion = db['usuarios']

    try:
        # 1. Obtener los nuevos datos del cuerpo de la petición
        datosActualizados = request.json

        if not datosActualizados:
            return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400

        # 2. Si el usuario envía una nueva contraseña, debemos hashearla
        if 'password' in datosActualizados:
            datosActualizados['password'] = generate_password_hash(datosActualizados['password'])

        # 3. Ejecutar la actualización en MongoDB
        # Usamos $set para modificar solo los campos enviados sin borrar el resto
        resultado = coleccion.update_one(
            {"_id": ObjectId(id)},
            {"$set": datosActualizados}
        )

        # 4. Verificar si se encontró y actualizó
        if resultado.matched_count == 0:
            return jsonify({"ERROR": "Usuario no encontrado"}), 404
        
        return jsonify({
            "mensaje": "Usuario actualizado correctamente",
            "modificado": resultado.modified_count
        }), 200

    except Exception as e:
        return jsonify({"ERROR": "ID no válido o error interno", "Detalle": str(e)}), 400

## ACTIVIDAD/ID
@app.route('/actividades/<id>', methods=['PUT'])
def actualizar_actividad(id):
    coleccion = db['actividades']
    pass

## RESERVA/ID
@app.route('/reservas/<id>', methods=['PUT'])
def actualizar_reserva(id):
    coleccion = db['reservas']
    pass

## ASISTENCIA/ID
@app.route('/asistencias/<id>', methods=['PUT'])
def actualizar_asistencia(id):
    coleccion = db['asistencias']
    pass


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

## RESERVA/ID
@app.route('/reservas/<id>', methods=['DELETE'])
def eliminar_reserva(id):
    coleccion = db['reservas']
    pass

## ASISTENCIA/ID
@app.route('/asistencias/<id>', methods=['DELETE'])
def eliminar_asistencia(id):
    coleccion = db['asistencias']
    pass


if __name__ == '__main__':
    print('\nIniciando Backend...\n')
    # app.run(debug = True, use_reloader = False)
    app.run(debug = True)

# python -m back

# GUÍAS
# https://j2logo.com/leccion-1-la-primera-aplicacion-flask/
# https://www.youtube.com/watch?v=QBx7sLNM0_A