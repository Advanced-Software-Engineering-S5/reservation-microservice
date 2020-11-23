from flask import Flask
import connexion, logging
from reservation_microservice.database import db, Reservation, ReservationState
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
    db.drop_all(app=application)
    db.create_all(app=application)

    #with application.app_context():
        #if (db.session.query(Reservation).first() is None):
           # reservation = Reservation(user_id=1, restaurant_id=1, seats=4, table_no=2, reservation_time=datetime.combine(datetime.now().date(), time(hour=21, minute=30)))
           # db.session.add(reservation)
           # db.session.commit()
        #reservation = Reservation(user_id=1, restaurant_id=999, seats=4, table_no=1, reservation_time=datetime.combine(datetime.now().date(), time(hour=21, minute=30)))
        #reservation2 = Reservation(user_id=1, restaurant_id=999, seats=4, table_no=2, reservation_time=datetime.combine(datetime.now().date(), time(hour=21, minute=30)))
        #reservation3 = Reservation(user_id=1, restaurant_id=999, seats=4, table_no=3, reservation_time=datetime.combine(datetime.now().date(), time(hour=21, minute=30)))
        #reservation4 = Reservation(user_id=1, restaurant_id=999, seats=4, table_no=4, reservation_time=datetime.combine(datetime.now().date(), time(hour=21, minute=30)))
        #reservation5 = Reservation(user_id=1, restaurant_id=999, seats=4, table_no=5, reservation_time=datetime.combine(datetime.now().date(), time(hour=21, minute=30)))
        #reservation6 = Reservation(user_id=1, restaurant_id=999, seats=4, table_no=6, reservation_time=datetime.combine(datetime.now().date(), time(hour=21, minute=30)))
        #reservation7 = Reservation(user_id=1, restaurant_id=999, seats=4, table_no=7, reservation_time=datetime.combine(datetime.now().date(), time(hour=21, minute=30)))
        #reservation8 = Reservation(user_id=1, restaurant_id=999, seats=4, table_no=8, reservation_time=datetime.combine(datetime.now().date(), time(hour=21, minute=30)))

        #db.session.add(reservation)
        #db.session.add(reservation2)
        #db.session.add(reservation3)
        #db.session.add(reservation4)
        #db.session.add(reservation5)
        #db.session.add(reservation6)
        #db.session.add(reservation7)
        #db.session.add(reservation8)
        #db.session.commit()


    return application


if __name__ == '__main__':
    app = create_app()
    app.run(port=5069)
