from datetime import datetime
from reservation_microservice.classes import customer_reservations as cr
from reservation_microservice.database import Reservation

def get_reservations(user_id: int):
    res = cr.get_user_reservations(int(user_id))
    json = [r.to_dict() for r in res]
    return json


def delete_user_reservation(reservation_id: int):
    if (cr.delete_reservation(reservation_id)):
        return 204
    else:
        return {'message': 'Reservation not found'}, 404


#TODO: actual implementation
def update_user_reservation(reservation_id: int):
    return 204

#TODO: actual implementation
def reserve():
    return 200