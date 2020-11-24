import unittest, requests
import os
from reservation_microservice.app import create_app
from reservation_microservice.database import db, Reservation, ReservationState
from datetime import datetime, time, date

class TestRestaurantReservationsEndpoints(unittest.TestCase):

    def setUp(self):
        today = date.today()
        self.reservations_list = [{
            'id': 50,
            'user_id': 1,
            'restaurant_id': 1,
            'reservation_time': datetime.combine(datetime.today(), time(hour=20, minute=30)),
            'seats': 4,
            'table_no': 1,
            'status': ReservationState.DONE,
            'entrance_time': datetime.combine(datetime.today(), time(hour=20, minute=30)),
            'exit_time': datetime.combine(datetime.today(), time(hour=21, minute=30))
        }, {
            'id': 51,
            'user_id': 1,
            'restaurant_id': 1,
            'reservation_time': datetime.combine(datetime.today(), time(hour=19, minute=00)),
            'seats': 4,
            'table_no': 2,
            'status': ReservationState.PENDING,
            'entrance_time': None,
            'exit_time': None
        }, {
            'id': 52,
            'user_id': 1,
            'restaurant_id': 1,
            'reservation_time': datetime.combine(datetime.today(), time(hour=21, minute=00)),
            'seats': 4,
            'table_no': 3,
            'status': ReservationState.PENDING,
            'entrance_time': None,
            'exit_time': None
        }, {
            'id': 53,
            'user_id': 2,
            'restaurant_id': 1,
            'reservation_time': datetime.combine(datetime.today(), time(hour=21, minute=00)),
            'seats': 4,
            'table_no': 4,
            'status': ReservationState.DONE,
            'entrance_time': datetime.combine(datetime.today(), time(hour=21, minute=00)),
            'exit_time': datetime.combine(datetime.today(), time(hour=22, minute=00))
        }, {
            'id': 54,
            'user_id': 3,
            'restaurant_id': 1,
            'reservation_time': datetime.combine(datetime.today(), time(hour=20, minute=00)),
            'seats': 4,
            'table_no': 5,
            'status': ReservationState.SEATED,
            'entrance_time': datetime.combine(datetime.today(), time(hour=20, minute=00)),
            'exit_time': None
        }, {
            'id': 55,
            'user_id': 3,
            'restaurant_id': 1,
            'reservation_time': datetime.combine(date(year=today.year, month=today.month, day=today.day - 1), time(hour=12, minute=00)),
            'seats': 4,
            'table_no': 6,
            'status': ReservationState.PENDING,
            'entrance_time': None,
            'exit_time': None
        }, {
            'id': 56,
            'user_id': 3,
            'restaurant_id': 1,
            'reservation_time': datetime.combine(date(year=today.year, month=today.month, day=today.day - 1), time(hour=12, minute=00)),
            'seats': 4,
            'table_no': 7,
            'status': ReservationState.PENDING,
            'entrance_time': None,
            'exit_time': None
        }, {
            'id': 57,
            'user_id': 3,
            'restaurant_id': 1,
            'reservation_time': datetime.combine(date(year=today.year, month=today.month, day=today.day - 1), time(hour=12, minute=00)),
            'seats': 4,
            'table_no': 8,
            'status': ReservationState.PENDING,
            'entrance_time': None,
            'exit_time': None
        }]
        
        self.app = create_app(dbfile='sqlite:///:memory:')


        with self.app.app_context():
            for res in self.reservations_list:
                db.session.add(Reservation(**res))
            db.session.commit()
    
    def test_get_restaurant_reservations(self):
        with self.app.test_client() as client:
            #this should return 7 reservations, since the page & page_size parameters default to 1 and 6 respectively
            response_no_params = client.get('/reservations/1')
            #this should return 1 reservation, since there is only one reservation whose status is SEATED
            response_seated = client.get('/reservations/1?seated=True')
            # this should return 2 reservations, sinceh the we compute an offset given by the page and the page_size parameter
            # in particular, in this case offset would be offset = (page - 1) * page_size = 1 * 6 = 6
            # since in our test database there are 8 reservations, we will return the last 2
            response_page_page_size = client.get('/reservations/1?page=2&page_size=6')
            #This should return an 400 Bad Request status code, since page_size is an enum with only a possible value: 6
            response_page_page_size_400 = client.get('/reservations/1?page=2&page_size=8')
            #This should return 4 reservations since there are only 4 reservations with reservation_time > datetime.now() [DO NOT RUN TESTS AFTER 8PM]
            response_range_upcoming = client.get('/reservations/1?range=upcoming')
            #This should return 4 reservations since there are 4 reservations for today
            response_range_today = client.get('/reservations/1?range=today')
            #This should return 400, since the only value accepted for range are today and upcoming
            response_fake_range = client.get('/reservations/1?range=yesterday')
            #this should return 404, since there is no restaurant with id 2
            response_fake_res = client.get('/reservaions/2')

        self.assertEqual(len(response_no_params.get_json()['reservations']), 7)
        self.assertEqual(len(response_seated.get_json()['reservations']), 1)
        self.assertEqual(len(response_page_page_size.get_json()['reservations']), 2)
        self.assertEqual(response_page_page_size_400.status_code, 400)
        self.assertEqual(len(response_range_upcoming.get_json()['reservations']), 5)
        self.assertEqual(len(response_range_today.get_json()['reservations']), 5)
        self.assertEqual(response_fake_range.status_code, 400)
        self.assertEqual(response_fake_res.status_code, 404)

    def test_update_reservation_status(self):
        update_1 = {
            "status": 0,
            "time": "2020-11-23T20:00:00"
        }
        update_2 = {
            "status": 3,
            "time": "2020-11-23T20:00:00"
        }
        update_3 = {
            "status": 4,
            "time": "2020-11-23T21:00:00"
        }
        update_4 = {
            "status": 5,
            "time": "2020-11-23T20:00:00"
        }

        with self.app.test_client() as client:
            #Reservation is correctly updated (only status updated)
            response_up_1 = client.put('/reservation/51/status', json=update_1)
            res_updated_1 = Reservation.query.filter_by(id=51).first()
            #Reservation is correctly updated (status and entrance_time updated)
            response_up_2 = client.put('/reservation/52/status', json=update_2)
            res_updated_2 = Reservation.query.filter_by(id=52).first()
            #Reservation is correctly updated (status and exit_time updated)
            response_up_3 = client.put('/reservation/54/status', json=update_3)
            res_updated_3 = Reservation.query.filter_by(id=54).first()
            #Update failure, status can only have values in [0, 4]
            response_up_4 = client.put('/reservation/55/status', json=update_4)
            #Update failure, reservation not found
            response_up_5 = client.put('/reservation/124/status', json=update_1)

        self.assertEqual(response_up_1.status_code, 200)
        self.assertEqual(res_updated_1.status, ReservationState.DECLINED)
        self.assertEqual(response_up_2.status_code, 200)
        self.assertEqual(res_updated_2.status, ReservationState.SEATED)
        self.assertEqual(res_updated_2.entrance_time, datetime.fromisoformat(update_2['time']))
        self.assertEqual(res_updated_3.status, ReservationState.DONE)
        self.assertEqual(res_updated_3.exit_time, datetime.fromisoformat(update_3['time']))
        self.assertEqual(response_up_4.status_code, 400)
        self.assertEqual(response_up_5.status_code, 404)

    def test_delete_restaurant_reservations(self):
        with self.app.test_client() as client:
            #This should delete all the reservations with reservation_time >= datetime.now()
            response_delete = client.delete('reservations/1')
            #There should be three reservations left
            res_after_deletion = Reservation.query.filter_by(restaurant_id = 1).all()
            #This should return a 404 since there are no future reservations associated to restaurand_id = 2
            response_delete_fail = client.delete('reservations/2')

        self.assertEqual(response_delete.status_code, 200)
        self.assertEqual(len(res_after_deletion), 3)
        for res in res_after_deletion:
            self.assertLess(res.reservation_time, datetime.now())
        self.assertEqual(response_delete_fail.status_code, 404)
        pass
            