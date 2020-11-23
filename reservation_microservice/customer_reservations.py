from datetime import datetime
from flask import request, jsonify
from sqlalchemy import between
from sqlalchemy.exc import DatabaseError
from reservation_microservice.classes import customer_reservations as cr
from reservation_microservice.database import db, Reservation, ReservationState
import requests
import os


def reserve():
    req_body = request.get_json()
    try:
        response = requests.get(f'http://{os.environ.get("GOS_RESTAURANT")}/restaurants/{req_body["restaurant_id"]}')
        restaurant = None if response.status_code != 200 else response.json()
    except requests.exceptions.RequestException as exc:
        restaurant = None
    if restaurant is not None:
        avg_stay_time = datetime.strptime(restaurant['avg_stay_time'], '%H:%M:%S').time()
        try:
            overlapping_tables = cr.get_overlapping_tables(
                restaurant_id=req_body['restaurant_id'],
                reservation_time=datetime.fromisoformat(
                    req_body['reservation_time']),
                reservation_seats=req_body['seats'],
                avg_stay_time=avg_stay_time)
        except DatabaseError as exc:
            return {'message': str(exc)}, 500
        try:
            table_response = requests.get(f'http://{os.environ.get("GOS_RESTAURANT")}/restaurants/tables/{req_body["restaurant_id"]}?seats={req_body["seats"]}')
            if table_response.status_code == 404:
                return {'message': 'No tables with the wanted number of seats available'}, 404
            tables = None if response.status_code != 200 else table_response.json()['tables']
            print(tables)
        except:
            tables = None
        if tables is not None:
            ids = [table['table_id'] for table in tables]
            print(cr.is_overbooked(overlapping_tables, ids))
            if (cr.is_overbooked(overlapping_tables, ids)):
                return {
                    'message':
                    'Overbooking: no tables available at the requested date and time'
                }, 409
            else:
                assigned = cr.assign_table_to_reservation(
                    overlapping_tables, ids)
                reservation = Reservation(
                    user_id=req_body['user_id'],
                    restaurant_id=req_body['restaurant_id'],
                    reservation_time=datetime.fromisoformat(
                        req_body['reservation_time']),
                    seats=req_body['seats'],
                    table_no=assigned)
                try:
                    id = cr.add_reservation(reservation)
                    return {'id': id}, 200
                except DatabaseError as exc:
                    return {'message': str(exc)}, 500
        else:
            return {'message': 'Restaurant service unavailable'}, 500
    else:
        return {'message': 'Restaurant service unavailable'}, 500


def get_reservations(user_id: int):
    try:
        res = cr.get_user_reservations(int(user_id))
        if (len(res) == 0):
            return {'message': 'The given user has made no reservations yet'}, 404
        json = [r.to_dict() for r in res]
        return {'reservations': json}
    except DatabaseError as exc:
        return {'message': str(exc)}, 500


def get_reservations_by_restaurant(user_id: int):
    uid_diff = request.args.get('exclude_user_id', False)
    print(uid_diff)
    start = request.args.get('start_time', None)
    end = request.args.get('end_time', None)
    restaurant_id = request.args.get('restaurant_id', None)
    if start is None and end is not None:
        return {'message': 'exclude_user_id and end_time can only be used with start_time'}, 400

    reservations = Reservation.query.filter(Reservation.user_id != user_id) if uid_diff else Reservation.query.filter_by(user_id=user_id)
    
    if restaurant_id:
        reservations = reservations.filter_by(restaurant_id=restaurant_id)
    
    if start and end:
        try:
            start_time = datetime.fromisoformat(start)
            end_time = datetime.fromisoformat(end)
        except ValueError:
            return {
                'message': 'start_time and end_time should be in ISO format'
            }, 400
        reservations = reservations.filter(Reservation.entrance_time != None, Reservation.entrance_time.between(start_time, end_time))
    elif start and end is None:
        try:
            start_time = datetime.fromisoformat(start)
        except ValueError:
            return {'message': 'start_time should be in ISO format'}, 400
        reservations = reservations.filter(Reservation.entrance_time != None).\
            filter(Reservation.entrance_time >= start_time)
    try:
        # execute filtered query
        return {'reservations': [r.to_dict() for r in reservations.all()]}
    except DatabaseError as exc:
        return str(exc), 500


def delete_user_reservation(reservation_id: int):
    try:
        if (cr.delete_reservation(reservation_id)):
            return {'message': 'Reservation deleted correctly'}
        else:
            return {'message': 'Reservation not found'}, 404
    except DatabaseError as exc:
       return {'message': str(exc)}, 500


def update_user_reservation(reservation_id: int):
    req_body = request.get_json()
    new_seats = req_body['new_seats']
    new_time = datetime.fromisoformat(req_body['new_reservation_time'])

    try:
        reservation = db.session.query(Reservation).filter_by(
            id=reservation_id).first()
        if reservation is None:
            return {'message': 'Reservation not found'}, 404
    except DatabaseError as exc:
        return {'message': str(exc)}, 500

    try:
        response = requests.get(f'http://{os.environ.get("GOS_RESTAURANT")}/restaurants/{reservation.restaurant_id}')
        restaurant = None if response.status_code != 200 else response.json()
    except:
        restaurant = None
    if (restaurant != None):
        avg_stay_time = datetime.strptime(restaurant['avg_stay_time'], '%H:%M:%S').time()
        if (req_body['new_seats'] == reservation.seats and
                cr.is_safely_updatable(reservation, avg_stay_time, new_time)):
            reservation.reservation_time = new_time
            reservation.status = ReservationState.PENDING
            try:
                db.session.commit()
                return {'message': 'Reservation updated correctly'}, 200
            except DatabaseError as exc:
                return str(exc), 500
        else:
            try:
                overlapping_tables = cr.get_overlapping_tables(
                    restaurant_id=reservation.restaurant_id,
                    reservation_time=new_time,
                    reservation_seats=new_seats,
                    avg_stay_time=avg_stay_time)
            except DatabaseError as exc:
                return str(exc), 500
            try:
               table_response = requests.get(f'http://{os.environ.get("GOS_RESTAURANT")}/restaurants/tables/{reservation.restaurant_id}?seats={new_seats}')
               if table_response.status_code == 404:
                    return {'message': 'No tables with the wanted number of seats available'}, 404
               tables = None if table_response.status_code != 200 else table_response.json()['tables']
            except:
                if table_response.status_code == 404:
                    return {'message': 'No tables with the wanted number of seats available'}, 404
                tables = None
            if (tables != None):
                ids = [table['table_id'] for table in tables]
                print(ids)
                if (cr.is_overbooked(overlapping_tables, ids)):
                    return {
                        'message':
                        'Overbooking: no tables available at the requested date and time'
                    }, 409
                else:
                    assigned = cr.assign_table_to_reservation(
                        overlapping_tables, ids)
                    reservation.reservation_time = new_time
                    reservation.table_no = assigned
                    reservation.seats = new_seats
                    reservation.status = ReservationState.PENDING
                    try:
                        db.session.commit()
                        return {
                            'message': 'Reservation updated correctly'
                        }, 200
                    except DatabaseError as exc:
                        return str(exc), 500
            else:
                return {'message': 'Restaurant service unavailable'}, 500
    else:
        return {'message': 'Restaurant service unavailable'}, 500
