import os
import json
from flask import Flask, request, jsonify, render_template, Response
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
coleccion = db['usuarios']


# RUTAS
@app.route('/')
def hello_world():
    return render_template('index.html', usuario="Programador")

## Registros POST
@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    datos = request.json
    id_insertado = coleccion.insert_one(datos).inserted_id

    return jsonify({"mensaje": "Usuario creado", "id": str(id_insertado)}), 201




## Registros GET
@app.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    usuarios = []

    for doc in coleccion.find():
        usuarios.append({
            "id": str(doc['_id']),
            "nombre_usuario": doc.get('nombre_usuario'),
            "nombre": doc.get('nombre'),
            "apellidos": doc.get('apellidos'),
            "dni": doc.get('dni'),
            "email": doc.get('email')
        })

    # return jsonify(usuarios), 200 # Devuelve json con campos ordenados alfabéticamente
    return Response(
        json.dumps(usuarios, sort_keys=False),
        mimetype='application/json'
    ), 200



if __name__ == '__main__':
    print('\nIniciando Backend...\n')
    app.run(debug = True, use_reloader = False)
    # app.run(debug = True)


# GUÍAS
# https://j2logo.com/leccion-1-la-primera-aplicacion-flask/
# https://www.youtube.com/watch?v=QBx7sLNM0_A