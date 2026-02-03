import os
import json
from flask import Flask, request, jsonify, render_template, Response
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId

# Obtenemos la ruta absoluta de la carpeta donde está este archivo
base_dir = os.path.dirname(os.path.abspath(__file__))
# Subimos un nivel si tus templates están fuera de /scripts
template_dir = os.path.join(base_dir, '..', 'templates')

app = Flask(__name__, template_folder = template_dir)
# Desactiva el ordenamiento alfabético de JSON
# app.config['JSON_SORT_KEYS'] = False


# Configuración de MongoDB
cliente = MongoClient('mongodb+srv://cristianxp_db_user:wpZqcQKcnUl4kGk4@cluster0.mdf0qyj.mongodb.net/')
db = cliente['gestora']


# RUTAS
@app.route('/')
def vista_principal():
    return render_template('index.html', usuario="Programador")

## MÉTODOS POST
@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    coleccion = db['usuarios']
    datos = request.json

    # Extraemos la contraseña plana
    passPlana = datos.get('contraseña')

    # Generamos el hash
    passHasheada = generate_password_hash(passPlana)

    nuevoUsuario = {
        "nombre_usuario": datos.get('nombre_usuario'),
        "contraseña": passHasheada,  # <--- Guardamos el hash
        "nombre": datos.get('nombre'),
        "apellidos": datos.get('apellidos'),
        "edad": datos.get("edad"),
        "dni": datos.get('dni'),
        "telefono": datos.get('telefono'),
        "email": datos.get('email'),
        "rol": datos.get('rol')
    }

    # id_insertado = coleccion.insert_one(datos).inserted_id
    id_insertado = coleccion.insert_one(nuevoUsuario).inserted_id

    return jsonify({"mensaje": "Usuario creado", "id": str(id_insertado)}), 201


## MÉTODOS GET
@app.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    coleccion = db['usuarios']
    usuarios = []

    for doc in coleccion.find():
        usuarios.append({
            "id": str(doc['_id']),
            "nombre_usuario": doc.get('nombre_usuario'),
            "nombre": doc.get('nombre'),
            "apellidos": doc.get('apellidos'),
            "edad": doc.get('edad'),
            "dni": doc.get('dni'),
            "telefono": doc.get('telefono'),
            "email": doc.get('email'),
            "rol": doc.get('rol')
        })

    # return jsonify(usuarios), 200 # Devuelve json con campos ordenados alfabéticamente
    return Response(
        json.dumps(usuarios, sort_keys=False),
        mimetype='application/json'
    ), 200

@app.route('/usuarios/<id>', methods=['GET'])
def obtener_usuario(id):
    coleccion = db['usuarios']

    try:
        # Convertimos el string que viene de la URL a un ObjectId de MongoDB
        usuario = coleccion.find_one({"_id": ObjectId(id)})
        
        if usuario:
            # Construimos la respuesta (recuerda que _id no es serializable directamente)
            respuesta = {
                "id": str(usuario['_id']),
                "nombre_usuario": usuario.get('nombre_usuario'),
                "nombre": usuario.get('nombre'),
                "apellidos": usuario.get('apellidos'),
                "edad": usuario.get('edad'),
                "dni": usuario.get('dni'),
                "telefono": usuario.get('telefono'),
                "email": usuario.get('email'),
                "rol": usuario.get('rol')
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

@app.route('/actividades', methods=['GET'])
def obtener_actividades():
    coleccion = db['actividades']
    pass

@app.route('/actividades/<id>', methods=['GET'])
def obtener_actividad(id):
    coleccion = db['actividades']
    pass

@app.route('/reservas', methods=['GET'])
def obtener_reservas():
    coleccion = db['reservas']
    pass

@app.route('/reservas/<id>', methods=['GET'])
def obtener_reserva(id):
    coleccion = db['reservas']
    pass

@app.route('/asistencias', methods=['GET'])
def obtener_asistencias():
    coleccion = db['asistencias']
    pass

@app.route('/asistencias/<id>', methods=['GET'])
def obtener_asistencia(id):
    coleccion = db['asistencias']
    pass


## MÉTODOS PUT
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
        return jsonify({"ERROR": "ID no válido o error interno", "detalle": str(e)}), 400

@app.route('/actividades/<id>', methods=['PUT'])
def actualizar_actividad(id):
    coleccion = db['actividades']
    pass

@app.route('/reservas/<id>', methods=['PUT'])
def actualizar_reserva(id):
    coleccion = db['reservas']
    pass

@app.route('/asistencias/<id>', methods=['PUT'])
def actualizar_asistencia(id):
    coleccion = db['asistencias']
    pass


## MÉTODOS DELETE
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

@app.route('/actividades/<id>', methods=['DELETE'])
def eliminar_actividad(id):
    coleccion = db['actividades']
    pass

@app.route('/reservas/<id>', methods=['DELETE'])
def eliminar_reserva(id):
    coleccion = db['reservas']
    pass

@app.route('/asistencias/<id>', methods=['DELETE'])
def eliminar_asistencia(id):
    coleccion = db['asistencias']
    pass



if __name__ == '__main__':
    print('\nIniciando Backend...\n')
    app.run(debug = True, use_reloader = False)
    # app.run(debug = True)


# GUÍAS
# https://j2logo.com/leccion-1-la-primera-aplicacion-flask/
# https://www.youtube.com/watch?v=QBx7sLNM0_A