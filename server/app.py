#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        json = request.get_json()
        user = User(
            username=json.get('username'),
            image_url=json.get('image_url'),
            bio=json.get('bio')
        )
        user.password_hash = json.get('password')
        if user and user.username:

            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id

            return user.to_dict(), 201
        
        return {"Message": "One or more fields are invalid"}, 422
        

        

class CheckSession(Resource):
    def get(self):
        if session['user_id']:
            user = User.query.filter(User.id == session["user_id"]).first()
            return user.to_dict(), 200
        
        return {"Message": "User not found"}, 401

class Login(Resource):
    def post(self):
        json = request.get_json()
        username = json.get('username')
        password = json.get('password')

        user = User.query.filter(User.username == username).first()
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict()
        
        return {"Message": "User not found"}, 401

class Logout(Resource):
    def delete(self):
        if session['user_id']:

            session['user_id'] = None
            return {}, 204
        
        return {"Message": "User not logged in"}, 401

class RecipeIndex(Resource):
    def get(self):
        if session['user_id']:
            return [recipe.to_dict() for recipe in Recipe.query.all()], 200
        
        return {"Message": "User not logged in"}, 401
    
    def post(self):
        json = request.get_json()
        if session['user_id']:
            recipe = Recipe(
                title = json.get("title"),
                instructions = json.get("instructions"),
                minutes_to_complete = json.get("minutes_to_complete"),
                user_id = session['user_id']
            )
            
            if recipe and len(recipe.instructions) >= 50:
                db.session.add(recipe)
                db.session.commit()
                return recipe.to_dict(), 201
            
            return {"Message": "One or more fields are invalid"}, 422
        
        return {"Message": "User not logged in"}, 401


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)