#  FOR CMD #
# set FLASK_DEBUG="True"
# set FLASK_APP=src
# flask --app src/__init__.py --debug run

#  FOR POWERSHELL #
# $env:FLASK_DEBUG = "True"
# $env:FLASK_APP = "src"
# flask --app src/__init__.py --debug run

from flask import (Flask, jsonify, redirect)
from os import environ
from src.auth import auth
from src.bookmarks import bookmarks
from src.database import db, Bookmark
from src.constants.http_status_code import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_404_NOT_FOUND
from flask_jwt_extended import JWTManager

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=environ.get("SQLALCHEMY_DATABASE_URI"),
            SQLALCHEMY_TRACK_MODIFICATION=False,
            JWT_SECRET_KEY=environ.get("JWT_SECRET_KEY")
        )
    else:
        app.config.from_mapping(test_config)
    
    db.app=app
    db.init_app(app)
    
    JWTManager(app)
    
    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)
    
    @app.get("/<short_url>")
    def redirect_to_url(short_url):
        bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()
        if bookmark:
            bookmark.visits=bookmark.visits+1
            db.session.commit()
            
            return redirect(bookmark.url)
        
    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(error):
        return jsonify({"error":"Not found"}), HTTP_404_NOT_FOUND
    
    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(error):
        return jsonify({"error":"Something went wrong, we are working on it"}), HTTP_500_INTERNAL_SERVER_ERROR
    
    return app