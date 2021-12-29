from flask import Flask, request, render_template
from app import show, auth, db


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.app_context().push()
    app.secret_key = "super secret key"

    app.register_blueprint(show.bp)
    app.register_blueprint(auth.auth)
    uri = 'neo4j+s://2fc6a12c.databases.neo4j.io'
    user = 'neo4j'
    password = 'jcpq1DW5IemYr1UIFn64RPNuvUP4TQLNcs2U5fNiruE'
    database = db.get_db()

    @app.route('/index', methods=['POST', 'GET'])
    def index():
        return render_template('base.html')

    @app.route('/filter', methods=['POST', 'GET'])
    def filter_actor():
        if request.method == 'GET':
            return render_template('list_people.html')

        name = request.form.get("name")
        data = db.query(f'Match (p:Person) WHERE TOLOWER(p.name) CONTAINS TOLOWER("{name}") Return p')
        return render_template('list_people.html', data=data)

    return app
