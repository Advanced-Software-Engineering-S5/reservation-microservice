from reservation_microservice.database import db, Reservation, ReservationState
from flask import request, jsonify
from sqlalchemy.exc import DatabaseError
from datetime import datetime, date


def get_restaurant_reservations(restaurant_id: int):

    #request values
    time_range = request.args.get('range', None)
    seated = request.args.get('seated', False)
    page = request.args.get('page', 1)  #default 1
    page_size = request.args.get('page_size', 6)  #default 6

    reservations = Reservation.query.filter_by(restaurant_id=restaurant_id)
    #gets only the reservations whose status is SEATED, needed to count the number of seated customers
    if seated:
        reservations = reservations.filter_by(status=ReservationState.SEATED)
        try:
            res = [r.to_dict() for r in reservations.all()]
            return {'reservations': res}
        except DatabaseError as exc:
            return {'message': str(exc)}, 500
    #gets the reservation in the specified time range
    if time_range:
        if (time_range == 'today'):
            today = date.today()
            reservations = reservations.filter(
                datetime(today.year, today.month, today.day) <
                Reservation.reservation_time).filter(
                    Reservation.reservation_time < datetime(
                        today.year, today.month, today.day + 1))
        elif (time_range == 'upcoming'):
            reservations = reservations.filter(
                Reservation.reservation_time > datetime.now())
        else:
            return {
                'Message': 'time_range can only have value today or upcoming'
            }, 400
    #computes the offset based on the page
    reservations = reservations.offset(
        (int(page) - 1) * int(page_size)).limit(int(page_size) + 1)
    try:
        #returns reservations
        res = [r.to_dict() for r in reservations.all()]
        print(res)
        return {
            'reservations': res
        } if len(res) > 0 else {
            'message': 'No Reservations associated to the specified restaurant'
        }, 404
    except DatabaseError as exc:
        return {'message': str(exc)}, 500


def update_reservation_status(reservation_id: int):
    status = request.get_json()['status']
    #gets the needed reservation
    try:
        reservation = Reservation.query.filter_by(id=reservation_id).first()
        if (reservation is None):
            return {'message': 'Reservation not found'}, 404
    except DatabaseError as exc:
        return {'message': str(exc)}, 500
    #update the status if status is in [0, 4]
    try:
        reservation.status = ReservationState(status)
    except ValueError:
        {
            'message':
            'status can only be one of the following values: 0 = Declined, 1 = Pending, 2 = Accepted, 3 = Seated, 4 = Done'
        }, 400
    #needed to update the entrance/exit time in case status = seated or status = done
    if (status == 3 or status == 4):
        try:
            time = datetime.fromisoformat(request.get_json()['time'])
        except:
            return {'message': 'time parameter should be in ISO format'}, 400
        if (status == 3):
            reservation.entrance_time = time
        else:
            reservation.exit_time = time

    try:
        db.session.commit()
        return {'message': 'Reservation updated correctly'}
    except DatabaseError as exc:
        return {'message': str(exc)}, 500


def delete_restaurant_reservations(restaurant_id: int):
    try:
        future_res = db.session.query(Reservation).filter_by(
            restaurant_id=restaurant_id).filter(
                Reservation.reservation_time >= datetime.now()).delete()
        print(future_res)
        if (future_res == 0):
            return {
                'message':
                'No future reservations associated to the given restaurant_id'
            }, 404
        else:
            db.session.commit()
            return {'message': 'Reservations deleted correctly'}
    except DatabaseError as exc:
        return {'message': str(exc)}, 500
