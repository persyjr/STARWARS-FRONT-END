"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User ,TokenBlockedList, Planets, People, Planets, Favorites
from api.utils import generate_sitemap, APIException 
from flask_bcrypt import Bcrypt #permite encriptar la clave
from flask_jwt_extended import JWTManager, create_access_token,create_refresh_token, jwt_required, get_jwt_identity,get_jwt #JWTManager permite usar las funciones de JWT,  create_access_token: permite crear tokens, jwt_required: me permite proteger la ruta, get_jwt_identity: me permite desencriptar la clave y libreria token de refresco
from flask_sqlalchemy import SQLAlchemy


api = Blueprint('api', __name__)
app = Flask(__name__)#permite acceder a mi api con flask y comunicarme mediante protocolo HTTP.  
bcrypt=Bcrypt(app)
db = SQLAlchemy(app)
jwt = JWTManager(app) 

@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200
    
#Registro: End point que reciba usuario y clave y lo registra en la base de datos

@api.route('/signup', methods=['POST']) #ENDPOINT DE REGISTRAR
def signup():
    email=request.json.get("email")#capturando mi usuario email del requerimiento
    password=request.json.get("password")#capturando la contraseña de mi ususario
    password_encryptada= bcrypt.generate_password_hash(password, rounds=None).decode("utf-8") #password encriptada con funcion de JWT y en UTF-8
    first_name=request.json.get("first_name")
    last_name=request.json.get("last_name")
    password=request.json.get("password")
    planets=request.json.get("planets")
    newUser=User(email=email, password=password_encryptada, first_name=first_name, last_name=last_name, planets=planets ,is_active= True)#creando mi nuevo usuario con el modelo (clase) que importe
    db.session.add(newUser)
    db.session.commit()
    response_body = {
        "message": "usuario creado exitosamente",
        "email":email,
        "first_name": first_name,
        "last_name":last_name
    }
    return jsonify(response_body), 201
    #login: end-point que recibe un nombre de usuario y clave, lo verifica en l abase de datos y genera un token
    #debe ser redirigido a un menu privado luego de que la autenticación sea éxitosa.

@api.route('/login', methods=['POST']) #ENDPOINT DE INICIO DE SESION
def login():
    email=request.json.get("email")#capturando mi usuario email del requerimiento
    password=request.json.get("password")#capturando la contraseña de mi ususario
    newUser=User.query.filter_by(email=email).first()#estoy buscando mi nuevo usuario con el modelo User, verificando que el usuario existe, lo busco por el correo
    #first me devuelve la primera coincidencia que encuentra
    #en el new user tengo el usuario (si existe)
    if not newUser:
        raise APIException("Usuario o Password no encontrado", status_code=401)#ls clave es invalida
    # Se valida si la clave que se recibio en la peticion es valida
    clave_valida=bcrypt.check_password_hash(newUser.password, password)#hace la comparacion de la contraseña encriptada de la base de datos con la que se recibe de la peticion
    if not clave_valida:
        raise APIException("Usuario o password no encontrado",status_code=401) 
    # Se genera un token y se retorna como respuesta
    token = create_access_token(email)
    refreshToken=create_refresh_token(email)    
    return jsonify({"token":token, "refreshToken":refreshToken}), 200
    #return jsonify(response_body), 201 

# Validar: endpoint que reciba un token y retorna si este es valido o no
@api.route('/verify-token',methods=['POST']) #ruta y metodo recordar que el token se guarda en el header
@jwt_required()
def verifyToken():    
    userEmail=get_jwt_identity()#en el token esta mi correo y lo esta verificando y guardando
    if not userEmail:
        return "Token invalido", 401 #cuando el token es incorrecto me muestra este mensaje
    return "Token correcto", 200
    #hay un mensaje de token expirado de igual forma

@api.route('/logout', methods=['POST'])
@jwt_required()
def destroyToken():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlockedList(token=jti, created_at=now, email=get_jwt_identity()))
    db.session.commit()
    return jsonify(msg="Access token revoked")


@api.route('/user', methods=['GET'])
def historial_usuarios():
    historialTodos = User.query.all()
    historialTodos = list(map(lambda user: user.serialize(), historialTodos ))
    return jsonify(historialTodos)

@api.route('/user/<id>', methods=['GET'])
def historial_singular_usuario(id):    
    
    historialUser = User.query.filter_by(id=id).all() 
    historialUser = list(map(lambda user: user.serialize(), historialUser ))
    print(historialUser)
    return jsonify(historialUser)

"""@api.route('/people', methods=['GET'])
def listar_people():
    
    users=User.query.all()
    all_users = list(map(lambda x: x.to_dict(), users))

    return jsonify(all_users), 200"""


@api.route('/planet', methods=['POST'])
@jwt_required()
def create_planet():
    
    name=request.json.get("name")
    users=get_jwt_identity() 
    
    newPlanet=Planets(name=name, users=users )
    db.session.add(newPlanet)
    db.session.commit()
    response_body = {
        "message": "planeta registrado exitosamente",
        "name":newPlanet.name,
        "id":newPlanet.users
    }
    return jsonify(response_body), 201


@api.route('/planet', methods=['GET'])
def historial_planetas():
    historialTodos = Planets.query.all()
    historialTodos = list(map(lambda planetas: planetas.serialize(), historialTodos ))
    return jsonify(historialTodos)

@api.route('/user/me', methods=['GET'])
@jwt_required()
def user_log():
    email=get_jwt_identity()
    historialUser = User.query.filter_by(email=email).all()
    historialUser = list(map(lambda user: user.serialize(), historialUser ))
    print(historialUser)
    response_body = {
        "message": "user in blog now",
        "user": historialUser
    }
    return jsonify(response_body), 201
# this only runs if `$ python src/main.py` is executed

@api.route('/favorite/planet/<planet_id>', methods=['POST'])
@jwt_required()
def create_favorite_planet(planet_id):
    
    #el campo plpaneta_id lo ingreso desde la url
    #el campo people_id no es requerido, lo puedo quitar
    planeta_id=planet_id
    people_id=request.json.get("people_id")
    
    #estoy buscando con el email del usuario el id del usuario 
    email=get_jwt_identity()
    historialUser = User.query.filter_by(email=email).all()
    historialUser = list(map(lambda user: user.serialize(), historialUser ))
    print(historialUser)
    user_id=historialUser[0]["id"]

    #creando el nuevo registro de planeta en favorito 
    newFavorite=Favorites(user_id=user_id, people_id=people_id, planeta_id=planeta_id, )
    db.session.add(newFavorite)
    db.session.commit()
    response_body = {
        "message": "planeta agregado a Favoritos exitosamente",
        "planeta_id":newFavorite.planeta_id,
        "id_usuario":newFavorite.user_id
    }
    return jsonify(response_body), 201
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)