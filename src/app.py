"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Vehicles, Planets, Favorites

#Este fragmento de codigo crea una instancio de Flask y modifica la configuracion 
#del mapeo de URL para permitir rutas con o sin barra diagonal al final de la URL.

#El argumento __name__ se utiliza para determinar el nombre del modulo actual. Se utiliza para ubicar recursos como plantillas y archivos.
app = Flask(__name__) 

#Esta línea establece la propiedad strict_slashes del objeto url_map de la aplicación en False.   
#El objeto url_map se encarga de gestionar las reglas de mapeo de URL en la aplicación.
#Cuando strict_slashes está en True (valor predeterminado), Flask trata las rutas con y sin barra diagonal al final como rutas distintas.
#Por ejemplo, /ruta y /ruta/ se considerarían diferentes. Al establecerlo en False, ambas rutas se tratan como equivalentes, lo que significa que /ruta y /ruta/ se manejarían de la misma manera.
app.url_map.strict_slashes = False 

#Este fragmento de código se encarga de configurar la conexión a la base de datos en tu aplicación Flask. 
#Esta línea utiliza la función os.getenv() para obtener el valor de la variable de entorno "DATABASE_URL"
#Esta variable se utiliza para almacenar la URL de conexión a la base de datos.
db_url = os.getenv("DATABASE_URL")
#Esta línea verifica si la variable db_url contiene un valor (es decir, si la variable de entorno "DATABASE_URL" está definida)
if db_url is not None:
    #Si la variable de entorno "DATABASE_URL" está definida, esta línea configura la URL de conexión a la base de datos
    # en la configuración de la aplicación Flask. Antes de hacerlo, reemplaza el prefijo "postgres://" en la URL por "postgresql://".
    #Esto es necesario para manejar la conexión a bases de datos PostgreSQL, ya que algunos sistemas y servicios utilizan este prefijo.
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
#Si la variable de entorno "DATABASE_URL" no está definida, este bloque se ejecutará.
else:
    #esta línea configura la URL de conexión a una base de datos SQLite.
    #En este caso, se utiliza la ruta al archivo "/tmp/test.db" como base de datos SQLite.
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
#Esta línea deshabilita el seguimiento de modificaciones en la base de datos. 
#El seguimiento de modificaciones es útil para algunas características, pero puede consumir recursos innecesarios si no se utilizan.
#Al establecerlo en False, se mejora el rendimiento de la aplicación.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Esta línea crea una instancia de la clase Migrate y la asocia con tu aplicación Flask (app) y la base de datos (db).
#La extensión Flask-Migrate se utiliza para gestionar las migraciones de la base de datos, lo que permite modificar
#el esquema de la base de datos de manera controlada a medida que evoluciona tu aplicación. 
#Las migraciones son especialmente útiles cuando se cambian los modelos de la base de datos.
MIGRATE = Migrate(app, db)
#Aquí, se inicializa la base de datos (db) con tu aplicación Flask (app). 
# Esto establece la conexión entre la base de datos y tu aplicación, permitiendo que los modelos y las vistas de base de datos funcionen correctamente.
db.init_app(app)
#Esta línea habilita el manejo de solicitudes CORS (Cross-Origin Resource Sharing) en tu aplicación.
#CORS es un mecanismo de seguridad en navegadores web que permite que los recursos en un dominio sean solicitados desde otro dominio.
#Al habilitar CORS en tu aplicación, estás permitiendo que tu API sea accesible desde dominios diferentes al dominio en el que se encuentra alojada la API.
CORS(app)
#Esta línea llama a la función setup_admin que se configura en el "admin.py".
#Esta función configura el panel de administración de Flask-Admin en tu aplicación, lo que te permite gestionar
#y administrar los datos de la base de datos de manera visual a través de una interfaz web.
setup_admin(app)
##En resumen, estas líneas de código configuran la gestión de migraciones de base de datos con Flask-Migrate, establecen la conexión entre la base de datos
##tu aplicación Flask, habilitan CORS para permitir el acceso desde otros dominios y configuran el panel de administración de Flask-Admin.

#Este fragmento de código define un manejador de errores personalizado para las excepciones del tipo APIException en tu aplicación Flask.
#Esta línea utiliza el decorador 
@app.errorhandler(APIException)
#Esta es la definición de la función que manejará las excepciones del tipo APIException.
#oma un argumento llamado error, que representa la instancia de la excepción que se ha producido.
def handle_invalid_usage(error):
    #Dentro de esta función, se utiliza la función jsonify() para serializar el diccionario devuelto por el método to_dict() de la instancia de la excepción APIException. 
    #El método to_dict() generalmente devolverá un diccionario que contiene información sobre el error,como un mensaje y un código de estado.
    #jsonify(error.to_dict()): Se serializa el diccionario del error en un objeto JSON.
    #Se obtiene el código de estado de la excepción. Esto suele indicar el tipo de error que ocurrió (por ejemplo, 404 para "No encontrado"
    return jsonify(error.to_dict()), error.status_code

#Esta línea utiliza el decorador @app.route() para asociar una función a la ruta '/', que representa la raíz de la URL. En otras palabras, esta función se ejecutará cuando se acceda a la página principal de tu sitio web.
@app.route('/')
#Esta es la definición de la función que manejará las solicitudes a la ruta '/'. No toma ningún argumento.
def sitemap():
    #Dentro de esta función, se llama a la función generate_sitemap(app) y se devuelve el resultado. La función 
    #generate_sitemap() probablemente está definida en otro lugar de tu código (en el archivo utils.py, según parece por el import en la parte superior).
    #Esta función generará un sitemap que contiene enlaces a los diferentes endpoints de la API.
    return generate_sitemap(app)
#En resumen, este bloque de código establece una ruta en tu aplicación Flask que responde a las solicitudes a la raíz de la URL ('/') devolviendo un sitemap generado por la función generate_sitemap(app).
#El sitemap es una forma de proporcionar una lista de enlaces a diferentes partes de tu aplicación, lo que puede ser útil para la navegación y el SEO.

#En resumen, este bloque de código establece una ruta en tu aplicación Flask que responde a las solicitudes GET a la URL /users devolviendo una lista de usuarios en formato JSON con un código de estado 200.
#Esta línea utiliza el decorador @app.route() para asociar una función a la ruta '/users'.
#Además, se especifica que esta función solo responderá a solicitudes HTTP GET (mediante el argumento methods=['GET']).
@app.route('/users', methods=['GET'])
#Esta es la definición de la función que manejará las solicitudes GET a la ruta '/users'. No toma ningún argumento
def get_users():
    #Dentro de esta función, se utiliza la clase User (que probablemente está definida en el archivo "models.py") y el método query.all() para obtener una lista de todos los usuarios en la base de datos.
    users = User.query.all()
    #Después de obtener la lista de usuarios, se itera a través de ella y se llama al método to_json() en cada usuario.
    #[user.to_json() for user in users]: Esta comprensión de lista crea una lista de objetos JSON a partir de los usuarios.
    #Junto con la lista de usuarios en formato JSON, se devuelve un código de estado HTTP 200 para indicar que la solicitud se ha procesado correctamente.
    return [user.to_json() for user in users], 200


@app.route('/users/<int:user_id>')
def get_single_user(user_id):
    user = User.query.get(user_id)
    return jsonify(user.serialize()), 200


@app.route('/users/<int:user_id>/favorites')
def get_favorites():
    favorites = Favorites.query.all()
    return [favorite.to_json() for favorite in favorites], 200


@app.route('/users/<int:user_id>/favorites/people/<int:person_id>', methods=['POST', 'DELETE'])
def post_or_delete_favorite_person(person_id):
    if request.method == 'POST':
        favorite = Favorites(people_id=person_id)
        db.session.add(favorite)
        db.session.commit()
        return jsonify(favorite.serialize()), 200
    else:
        favorite = Favorites.query.get(person_id)
        if favorite is None:
            raise APIException('User not found', status_code=404)
        db.session.delete(favorite)
        db.session.commit()
        return jsonify(favorite.serialize()), 200


@app.route('/users/<int:user_id>/favorites/vehicles/<int:vehicle_id>', methods=['POST', 'DELETE'])
def post_or_delete_favorite_vehicle(vehicle_id):
    if request.method == 'POST':
        favorite = Favorites(vehicles_id=vehicle_id)
        db.session.add(favorite)
        db.session.commit()
        return jsonify(favorite.serialize()), 200
    else:
        favorite = Favorites.query.get(vehicle_id)
        if favorite is None:
            raise APIException('User not found', status_code=404)
        db.session.delete(favorite)
        db.session.commit()
        return jsonify(favorite.serialize()), 200


@app.route('/users/<int:user_id>/favorites/planets/<int:planet_id>', methods=['POST', 'DELETE'])
def post_or_delete_favorite_planet(planet_id):
    if request.method == 'POST':
        favorite = Favorites(planets_id=planet_id)
        db.session.add(favorite)
        db.session.commit()
        return jsonify(favorite.serialize()), 200
    else:
        favorite = Favorites.query.get(planet_id)
        if favorite is None:
            raise APIException('User not found', status_code=404)
        db.session.delete(favorite)
        db.session.commit()
        return jsonify(favorite.serialize()), 200


@app.route('/people')
def get_people():
    people = People.query.all()
    return [person.to_jason() for person in people], 200


@app.route('/people/<int:person_id>')
def get_single_person(person_id):
    person = People.query.get(person_id)
    return jsonify(person.serialize()), 200


@app.route('/vehicles')
def get_vehicles():
    vehicles = Vehicles.query.all()
    return [vehicle.to_jason() for vehicle in vehicles], 200


@app.route('/vehicles/<int:vehicle_id>')
def get_single_vehicle(vehicle_id):
    vehicle = Vehicles.query.get(vehicle_id)
    return jsonify(vehicle.serialize()), 200


@app.route('/planets')
def get_planets():
    planets = Planets.query.all()
    return [planet.to_jason() for planet in planets], 200


@app.route('/planets/<int:planet_id>')
def get_single_planet(planet_id):
    planet = Planets.query.get(planet_id)
    return jsonify(planet.serialize()), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
