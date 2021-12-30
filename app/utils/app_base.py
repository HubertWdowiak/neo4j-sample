from flask import Flask, request, render_template, redirect, url_for
from app.utils import db
from app.controllers import auth_controller, info_controller


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.app_context().push()
    app.secret_key = "super secret key"

    app.register_blueprint(info_controller.bp)
    app.register_blueprint(auth_controller.auth)

    @app.route('/', methods=['POST', 'GET'])
    def index():
        return redirect(url_for('show.get_all_people'))

    return app
