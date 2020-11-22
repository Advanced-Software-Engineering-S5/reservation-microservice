from reservation_microservice.database import db, Reservation
from flask import request, jsonify
from sqlalchemy.exc import DatabaseError
from datetime import datetime

def get_restaurant_reservations(restaurant_id: int):
    try:
        reservations = db.session.query(Reservation).filter_by(restaurant_id = restaurant_id).all()
    except DatabaseError as exc:
        return str(exc), 500
    if (len(reservations) > 0):
        return [res.to_dict() for res in reservations], 200
    else:
        return {'message': 'No reservations associated to the given restaurant_id'}, 404
    


def delete_restaurant_reservations(restaurant_id: int):
    try:
        future_res = db.session.query(Reservation).filter_by(restaurant_id = restaurant_id).filter(Reservation.reservation_time >= datetime.now()).delete()
        print(future_res)
        if (future_res == 0):
            return {'message': 'No future reservations associated to the given restaurant_id'}, 404
        else: 
            db.session.commit()
            return 204
    except DatabaseError as exc:
        return str(exc), 500