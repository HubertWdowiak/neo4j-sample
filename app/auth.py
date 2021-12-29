from __future__ import annotations

import functools
import uuid

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from app import db

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/register', methods=['GET'])
def register_get():
    return render_template('register.html')


@auth.route('/register', methods=['POST'])
def register_post():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        email = request.form['email']

        error = find_register_error(username, password, email)
        if not error:
            try:
                string = f"CREATE (u1:User {{username: '{username}', password:'{password}', admin:{False}, " \
                         f"id:'{uuid.uuid4()}'}})"
                db.query(string)
                return redirect(url_for('auth.login_get'))
            except Exception as e:
                if 'invalid input syntax for type' in str(e):
                    error = 'Niepoprawny typ danych'

        flash(error)

    return render_template('register.html')


def find_register_error(username, password, email):
    error = None

    if not username:
        error = 'Username is required.'
    elif not password:
        error = 'Password is required.'
    elif not email:
        error = 'Email is required.'
    else:
        is_already_in_db = db.query(f'MATCH (u:USER) WHERE u.login = "{username}" RETURN u')
        if is_already_in_db:
            error = f"User '{username}' is already registered."
    return error


@auth.route('/login', methods=['GET'])
def login_get():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    error = None
    user = db.query(f'MATCH (u:User) WHERE u.username = "{username}" RETURN u')

    if not user:
        error = 'Incorrect username.'
    elif not check_password_hash(user[0][0]['password'], password):
        error = 'Incorrect password.'

    if not error:
        session.clear()
        session['user_id'] = user[0][0]['id']
        return redirect(url_for('show.get_all_people'))

    flash(error)

    return render_template('login.html')


@auth.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if not user_id:
        g.user = None
    else:
        g.user = db.query(f'MATCH (u:User) WHERE u.id="{user_id}" RETURN u')[0]


@auth.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('auth.login_get'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        a = g
        if g.user is None or g.user == []:
            return redirect(url_for('auth.login_get'))
        return view(**kwargs)

    return wrapped_view
