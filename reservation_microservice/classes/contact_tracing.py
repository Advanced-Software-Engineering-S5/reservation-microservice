from flask import request
from datetime import datetime, time, timedelta
from reservation_microservice.database import db, Reservation
import requests, os, logging

MAX_DAYS_ALLOWED = 1000
DEFAULT_NDAYS = 14

def contact_tracing(positive_user_id):
    n_days = request.args.get('contact_days', DEFAULT_NDAYS)
    # defaults to 14 days if number of days is invalid
    if n_days < 0 or n_days > MAX_DAYS_ALLOWED:
        n_days = DEFAULT_NDAYS
    # get places visited by positive guy
    try:
        reservations = check_visited_places(positive_user_id, n_days)
        return contact_tracing_users(reservations, positive_user_id)
    except Exception as e:
        logging.error(e)
        return {'message': e}, 500
    

def check_visited_places(userid: int, day_range: int):
    """ Checks the restaurants in which a given customer has been to
        in the last `day_range` days.
    Args:
        userid (int): Id of the customer
        day_range (int): Number of days in which we're checking the customer activities.
    Returns:
        [type]: A list of restaurants reservations or an empty list in case the customer didn't visit
        any restaurant.
    """
    print(f"Checking visited places by user {userid} in the last {day_range} days")
    # get reservations in which user actually showed up from Reservation service
    range = datetime.now() - timedelta(days=day_range)
    range.replace(hour=0, minute=0, second=0, microsecond=0)

    reservations = Reservation.query.filter_by(user_id=userid).\
    filter(Reservation.entrance_time != None).filter(Reservation.entrance_time >= range).all()
    # print("DB", db)
    # also all results must be json serializable
    return [row.to_dict() for row in reservations]


def contact_tracing_users(past_reservations, user_id: int):
    """Given a positive user id and a list of past reservation he/she made in the last 14 days,
        returns a list of users which were allegedly in contact with him/her.

    Args:
        past_reservations: List of dictionaries, each representing a reservation the positive 
        user made.
        user_id (int): Positive customer id.
    """
    # check which users were at the restaurant at the same time as the positive guy
    user_at_risk = []
    for reservation in past_reservations:
        et = reservation['entrance_time']
        if isinstance(et, str):
            et = datetime.strptime(reservation['entrance_time'], '%Y-%m-%dT%H:%M:%S.%f')
        # get average staying time of the restaurant and compute 'danger period'
        resp = requests.get(f"http://{os.environ.get('GOS_RESTAURANT')}/restaurants/{reservation['restaurant_id']}")
        if resp == 404:
            # restaurant does not exists/was deleted, carry on defining a standard avg time (prioritize reservations which are always kept)
            avg_stay_time = time(hour=1, minute=30)
        else:
            avg_stay_time = resp.json()['avg_stay_time']
            # convert time format back to object
            avg_stay_time = datetime.strptime(avg_stay_time, "%H:%M:%S").time()

        # avg_stay_time = Restaurant.query.filter_by(id=reservation['restaurant_id']).first().avg_stay_time
        staying_interval = timedelta(hours=avg_stay_time.hour, minutes=avg_stay_time.minute, seconds=avg_stay_time.second)
        start_time = et - staying_interval
        end_time = et + staying_interval

        user_reservation = Reservation.query.filter(Reservation.user_id != user_id).\
            filter_by(restaurant_id=reservation['restaurant_id']).\
                filter(Reservation.entrance_time.between(start_time, end_time)).all()
        # print(user_reservation)
        # preserve positive user reservation we're referring to, as to notify operator 
        user_ids_args = 'or_(' + ', '.join(['User.id == ' + str(ur.user_id) for ur in user_reservation])+')'
        # request users information from User service
        resp = requests.get(f'http://{os.environ.get("GOS_USER")}/users/filter?filter={user_ids_args}')
        if resp.status_code != 200:
            logging.error("Error in user service contact")
            raise Exception
        user_at_risk += resp.json()
    return {'users': user_at_risk}, 200
