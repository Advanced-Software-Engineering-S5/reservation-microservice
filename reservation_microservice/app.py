from flask import Flask
import connexion, logging
from reservation_microservice.database import db, Reservation
from datetime import datetime, time

def create_app(dbfile='sqlite:///reservations_service.db'):
    logging.basicConfig(level=logging.INFO)

    app = connexion.App(__name__)
    app.add_api('swagger.yml')
    #app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    #app.config['SECRET_KEY'] = 'ANOTHER ONE'
    application = app.app
    application.config['SQLALCHEMY_DATABASE_URI'] = dbfile
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(application)
    #db.drop_all(app=app)
    db.create_all(app=application)

    with application.app_context():
        reservation = Reservation(user_id=1, restaurant_id=1, seats=4, table_no=2, reservation_time=datetime.combine(datetime.now().date(), time(hour=21, minute=30)))
        db.session.add(reservation)
        db.session.commit()


    return application


if __name__ == '__main__':
    app = create_app()
    app.run(port=8080)
