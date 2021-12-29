from app import db
from flask import Blueprint, render_template, request, g, session

from app.auth import login_required

bp = Blueprint('show', __name__, url_prefix='/show')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if not user_id:
        g.user = None
    else:
        result = db.query(f'MATCH (u:User) WHERE u.id="{user_id}" RETURN u')[0]
        g.user = result


@bp.route('person/<string:person_id>/<int:rate>', methods=['GET', 'POST'])
@login_required
def rate(person_id: str, rate: int):
    is_already_rated = db.query(f'MATCH (u:User)-[r:Rated]->(p:Person) where u.id="{g.user[0]["id"]}" AND ID(p) = {person_id} '
                                f'SET r.rate={rate} RETURN u, r, p')
    if not is_already_rated:
        db.query(f'match (p:Person), (u:User) WHERE u.id="{g.user[0]["id"]}" and ID(p)={person_id} '
                 f'create (u)-[r:Rated {{rate:{rate}}}]->(p) Return p, u')
    person = db.query(f'match (d)-[e:Rated]->(a:Person) where ID(a)={person_id} return a,'
                      f' avg(e.rate) as avg, count(e) as count')[0]
    data = db.query(f'match (a:Person)-[b:played_in]->(movies) where ID(a)={person_id} '
                    f'return movies')
    return render_template('person.html', person=person, data=data, rate=5 - rate)


@bp.route('person/<string:person_id>', methods=['GET', 'POST'])
@login_required
def get_single_person(person_id: str):
    try:
        person = db.query(f'match (d)-[e:Rated]->(a:Person) where ID(a)={person_id} return a,'
                          f' avg(e.rate) as avg, count(e) as count')[0]
    except IndexError:
        person = db.query(f'match (a:Person) where ID(a)={person_id} return a,'
                          f' 0 as avg, 0 as count')[0]
    data = db.query(f'match (a:Person)-[b:played_in]->(movies) where ID(a)={person_id} '
                    f'return movies')
    try:
        rate = db.query(f'match (u:User)-[r:Rated]->(p:Person) where ID(p)={person_id} AND u.id="{g.user[0]["id"]}" '
                        f'return r.rate as rate')[0][0]['rate']
    except IndexError:
        rate = 0
    return render_template('person.html', person=person, data=data, rate=5 - rate)


@bp.route('people', methods=['GET', 'POST'])
@login_required
def get_all_people():
    word_filter = request.form.get('filter')
    rate_range = request.form.get('myRange')
    if not word_filter:
        word_filter = ''
    if not rate_range:
        rate_range = 0

    data = db.query(f'match (a:Person), (a)<-[b:Rated]-(c) '
                    f'where (tolower(a.name) contains tolower("{word_filter}") '
                    f'or tolower(a.lastname) contains tolower("{word_filter}")) '
                    f'Return a, avg(b.rate) as avg, count(b) as num_of_reviews, ID(a) as id')

    data_without_reviews = db.query(f'MATCH (a:Person)'
                                    f'where tolower(a.name) contains tolower("{word_filter}") AND NOT (a)<-[:Rated]-()'
                                    f'Return a, 0 as avg, 0 as num_of_reviews, ID(a) as id')
    data.extend(data_without_reviews)
    data = [e for e in data if e[1]['avg'] >= float(rate_range)]

    genres = db.query(f'MATCH (g:Genre) Return g')
    return render_template('list_people.html', data=data, genres=genres, rate_range=rate_range)
