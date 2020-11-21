import connexion
from reservation_microservice.database import db, Reservation
from datetime import datetime, timedelta
import random

def create_app_for_test():
    # creates app using in-memory sqlite db for testing purposes
    app = connexion.App(__name__)
    app.add_api('../../swagger.yml')
    app = app.app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    app.config['SECRET_KEY'] = 'ANOTHER ONE'

    # celery config
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'

    db.init_app(app)
    db.create_all(app=app)

    # set the WSGI application callable to allow using uWSGI:
    # uwsgi --http :8080 -w app
    return app

def add_random_visit_to_place(restaurant_id:int, visit_date: datetime, users_ids):
    visits = []
    risky_visits = 0

    # make a bunch of reservations
    for uid in users_ids:
        # compute 'danger period' in which user might have been in contact with positive dude
        visit = Reservation(user_id=uid, 
        restaurant_id=restaurant_id, reservation_time=visit_date, 
        table_no=0, seats=1, entrance_time=visit_date)
        visits.append(visit)
    db.session.add_all(visits)
    db.session.commit()
    return risky_visits
