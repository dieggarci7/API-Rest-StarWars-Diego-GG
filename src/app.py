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
from models import db, User, Character, Planet, FavCharacter, FavPlanet
from sqlalchemy import select
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def get_user():
    stmt=select(User)
    users = db.session.execute(stmt).scalars().all()
    users = list(map(lambda item: item.serialize(), users))

    return jsonify(users), 200


@app.route('/planet', methods=['GET'])
def get_planet():
    stmt=select(Planet)
    planets = db.session.execute(stmt).scalars().all()
    planets = list(map(lambda item: item.serialize(), planets))

    return jsonify(planets), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_id(planet_id):
    planet = db.session.execute(select(Planet).where(Planet.id == planet_id)).scalar_one_or_none()
    if planet is None:
        return { 'message': f"El planeta con el id {planet_id} no existe"},404

    return jsonify(planet.serialize()), 200


@app.route('/character', methods=['GET'])
def get_character():
    stmt=select(Character)
    characters = db.session.execute(stmt).scalars().all()
    characters = list(map(lambda item: item.serialize(), characters))

    return jsonify(characters), 200


@app.route('/characters/<int:character_id>', methods=['GET'])
def get_character_id(character_id):
    character = db.session.execute(select(Character).where(Character.id == character_id)).scalar_one_or_none()
    if character is None:
        return { 'message': f"El personaje con el id {character_id} no existe"},404

    return jsonify(character.serialize()), 200


@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_users_favorites(user_id):
    user = db.session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        return {'message': f"El usuario con el id {user_id} no existe"}, 404

    planets = [fav.planet.serialize() for fav in user.fav_planets]
    characters = [fav.character.serialize() for fav in user.fav_characters]

    return {
        'user_id': user.id,
        'favorites': {
            'planets': planets,
            'characters': characters
        }
    }, 200


@app.route('/favorites/planets/<int:planet_id>', methods=['POST'])
def post_planet_to_favorite(planet_id):
    planet = db.session.execute(select(Planet).where(Planet.id == planet_id)).scalar_one_or_none()
    if planet is None:
        return { 'message': f"El planeta con el id {planet_id} no existe"},404

    data = request.get_json()
    user_id = data.get('user_id')
    user = db.session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        return { 'message': f"El usuario con el id {user_id} no existe"},404

    new_fav = FavPlanet(user=user, planet=planet)
    db.session.add(new_fav)

    db.session.commit()

    return jsonify(user.serialize()), 200


@app.route('/favorites/characters/<int:character_id>', methods=['POST'])
def post_character_to_favorite(character_id):
    character = db.session.execute(select(Character).where(Character.id == character_id)).scalar_one_or_none()
    if character is None:
        return { 'message': f"El personaje con el id {character_id} no existe"},404

    data = request.get_json()
    user_id = data.get('user_id')
    user = db.session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        return { 'message': f"El usuario con el id {user_id} no existe"},404

    new_fav = FavCharacter(user=user, character=character)
    db.session.add(new_fav)

    db.session.commit()

    return jsonify(user.serialize()), 200


@app.route('/favorites/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet_id_favorites(planet_id):
    planet = db.session.execute(select(Planet).where(Planet.id == planet_id)).scalar_one_or_none()
    if planet is None:
        return {'message': f"El planeta con el id {planet_id} no existe"}, 404

    list(map(db.session.delete(planet)))
    db.session.commit()

    return {'message': f"El planeta con el id {planet_id} fue eliminado correctamente de sus favoritos" }, 200


@app.route('/favorites/characters/<int:character_id>', methods=['DELETE'])
def delete_character_id_favorites(character_id):
    character = db.session.execute(select(Character).where(Character.id == character_id)).scalar_one_or_none()
    if character is None:
        return {'message': f"El personaje con el id {character_id} no existe"}, 404

    list(map(db.session.delete(character)))
    db.session.commit()

    return {'message': f"El personaje con el id {character_id} fue eliminado correctamente de sus favoritos" }, 200


@app.route('planets/<int:planet_id>', methods=['DELETE'])
def delete_planet_id(planet_id):
    planet = db.session.execute(select(Planet).where(Planet.id == planet_id)).scalar_one_or_none()
    if planet is None:
        return {'message': f"El planeta con el id {planet_id} no existe"}, 404
    
    db.session.delete(planet)
    db.session.commit()

    return {'message': f"El planeta con el id {planet_id} fue eliminado correctamente"}, 200


@app.route('characters/<int:character_id>', methods=['DELETE'])
def delete_character_id(character_id):
    character = db.session.execute(select(Character).where(Character.id == character_id)).scalar_one_or_none()
    if character is None:
        return {'message': f"El personaje con el id {character_id} no existe"}, 404
    
    db.session.delete(character)
    db.session.commit()

    return {'message': f"El personaje con el id {character_id} fue eliminado correctamente"}, 200



@app.route('/users/<int:user_id>/favorites', methods=['PUT'])
def update_users_favorites(user_id):
    data = request.get_json()

    user = db.session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        return {'message': f"El usuario con el id {user_id} no existe"}, 404

    list(map(db.session.delete, user.fav_planets))
    list(map(db.session.delete, user.fav_characters))

    for planet_id in data.get("planets", []):
        planet = db.session.get(Planet, planet_id)
        if planet:
            new_fav = FavPlanet(user=user, planet=planet)
            db.session.add(new_fav)

    for character_id in data.get("characters", []):
        character = db.session.get(Character, character_id)
        if character:
            new_fav = FavCharacter(user=user, character=character)
            db.session.add(new_fav)

    db.session.commit()

    return {'message': f"Favoritos del usuario {user_id} actualizados correctamente."}, 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
