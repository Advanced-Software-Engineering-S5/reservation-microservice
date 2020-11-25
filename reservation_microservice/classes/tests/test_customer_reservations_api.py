import unittest, requests
import os
from reservation_microservice.app import create_app
from reservation_microservice.database import db, Reservation, ReservationState
from datetime import datetime, time


class TestCustomerReservationsEndpoints(unittest.TestCase):
    def setUp(self):
        self.reservations_list = [{
            'id': 50,
            'user_id': 1,
            'restaurant_id': 1000,
            'reservation_time': datetime.combine(datetime.today(), time(hour=20, minute=30)),
            'seats': 4,
            'table_no': 1,
            'status': ReservationState.DONE,
            'entrance_time': datetime.combine(datetime.today(), time(hour=20, minute=30)),
            'exit_time': datetime.combine(datetime.today(), time(hour=21, minute=30))
        }, {
            'id': 51,
            'user_id': 1,
            'restaurant_id': 1001,
            'reservation_time': datetime.now(),
            'seats': 4,
            'table_no': 1,
            'status': ReservationState.PENDING,
            'entrance_time': None,
            'exit_time': None
        }, {
            'id': 52,
            'user_id': 1,
            'restaurant_id': 1001,
            'reservation_time': datetime.combine(datetime.today(), time(hour=21, minute=00)),
            'seats': 4,
            'table_no': 2,
            'status': ReservationState.PENDING,
            'entrance_time': None,
            'exit_time': None
        }, {
            'id': 53,
            'user_id': 2,
            'restaurant_id': 1000,
            'reservation_time': datetime.combine(datetime.today(), time(hour=21, minute=00)),
            'seats': 4,
            'table_no': 2,
            'status': ReservationState.DONE,
            'entrance_time': datetime.combine(datetime.today(), time(hour=21, minute=00)),
            'exit_time': datetime.combine(datetime.today(), time(hour=22, minute=00))
        }, {
            'id': 54,
            'user_id': 3,
            'restaurant_id': 1,
            'reservation_time': datetime.combine(datetime.today(), time(hour=20, minute=00)),
            'seats': 4,
            'table_no': 1,
            'status': ReservationState.PENDING,
            'entrance_time': None,
            'exit_time': None
        }, {
            'id': 55,
            'user_id': 3,
            'restaurant_id': 1,
            'reservation_time': datetime.combine(datetime.today(), time(hour=12, minute=00)),
            'seats': 4,
            'table_no': 1,
            'status': ReservationState.PENDING,
            'entrance_time': None,
            'exit_time': None
        }]

        self.restaurants_list = [{
            'name': 'Prova 1', 
            'lat': 4,
            'lon': 5,
            'phone': '5656565656',
            'extra_info': 'Rigatoni dorati h24, cucina povera'
            }, {
                'name': 'Prova 2',
                'lat': 3,
                'lon': 3,
                'phone': '1111001234',
                'extra_info': 'cucina di prova'
            }   
        ]

        self.app = create_app(dbfile='sqlite:///:memory:')


        with self.app.app_context():
            for res in self.reservations_list:
                db.session.add(Reservation(**res))
            db.session.commit()

    def test_get_user_reservations(self):
        with self.app.test_client() as client:
            #user with id 1 has 2 future reservations
            response_user1 = client.get('/customer_reservations/1')
            #user with id 2 has 1  reservations
            response_user2 = client.get('/customer_reservations/2')
            #user with id 10 does not exist, the json of the response should be empty
            response_user3 = client.get('/customer_reservations/10')

        self.assertEqual(len(response_user1.get_json()['reservations']), 2)
        self.assertEqual(len(response_user2.get_json()['reservations']), 1)
        self.assertEqual(response_user3.status_code, 404)
    
    def test_get_reservations(self):
        with self.app.test_client() as client:
            response_reservation = client.get('customer_reservation/51')
            response_no_reservation = client.get('customer_reservation/126')

        self.assertEqual(response_reservation.status_code, 200)
        self.assertEqual(response_no_reservation.status_code, 404)
              
    
    def test_get_user_reservations_by_restaurant(self):
        start_time = datetime.combine(datetime.today(), time(hour=20, minute=30)).isoformat()
        end_time = datetime.combine(datetime.today(), time(hour=21, minute=30)).isoformat()
        with self.app.test_client() as client:
            #test the combination of the three parameters
            response_all_params = client.get(f'/filtered_reservations/1?restaurant_id=1000&exclude_user_id=True&start_time={start_time}&end_time={end_time}')
            response_end_time = client.get(f'/filtered_reservations/1?end_time={end_time}')
            response_no_params = client.get(f'/filtered_reservations/1')
            response_start_time = client.get(f'/filtered_reservations/1?start_time={start_time}')
            response_dates_no_ISO = client.get(f'/filtered_reservations/1?start_time=112412412&end_time=235982958')
            response_start_end = client.get(f'/filtered_reservations/1?start_time={start_time}&end_time={end_time}')
            response_exclude_user = client.get(f'/filtered_reservations/1?exclude_user_id=True')
            response_restaurant = client.get(f'/filtered_reservations/1?restaurant_id=1001')
        
        self.assertEqual(len(response_all_params.get_json()['reservations']), 1)
        self.assertEqual(response_end_time.status_code, 400)
        self.assertEqual(len(response_no_params.get_json()['reservations']), 3)
        self.assertEqual(len(response_start_time.get_json()['reservations']), 1)
        self.assertEqual(response_dates_no_ISO.status_code, 400)
        self.assertEqual(len(response_start_end.get_json()['reservations']), 1)
        self.assertEqual(len(response_exclude_user.get_json()['reservations']), 3)
        self.assertEqual(len(response_restaurant.get_json()['reservations']), 2)

    def test_delete_user_reservation(self):
        with self.app.test_client() as client:
            #there is a reservation with id=52, should return a 204 status code
            response_true = client.delete(f'/customer_reservation/52')
            # there is no reservation with id=10000, should return a 404 status code
            response_false = client.delete(f'/customer_reservation/10000')
        self.assertEqual(response_true.status_code, 200)
        self.assertEqual(response_false.status_code, 404)
    
    
    def test_reserve(self):        
        reservation_1 = {
            'user_id': 1,
            'restaurant_id': 1, #restaurant with id 1 is the Trial Restaurant in the restaurant_microservice
            'reservation_time': datetime.combine(datetime.today(), time(hour=15, minute=00)).isoformat(),
            'seats': 4
        }
        reservation_2 = {
            'user_id': 2,
            'restaurant_id': 1,
            'reservation_time': datetime.combine(datetime.today(), time(hour=18, minute=00)).isoformat(),
            'seats': 4            
        }
        reservation_3 = {
            'user_id': 1,
            'restaurant_id': 1,
            'reservation_time': datetime.combine(datetime.today(), time(hour=10, minute=00)).isoformat(),
            'seats': 6
        }
        reservation_4 = {
            'user_id': 1,
            'restaurant_id': 125,
            'reservation_time': datetime.combine(datetime.today(), time(hour=10, minute=00)).isoformat(),
            'seats': 6
        }
        
        with self.app.test_client() as client:
            #Needed to store the newly added reservations
            with self.app.app_context():
            # restaurant with id 1 has a single table with 4 seats, both reservation should be added returning 200 as status_code
            # note that the two reservation_time are not conflicting considering the avg_stay_time of the restaurant.
                response_res_1 = client.post('/reserve', json=reservation_1)
                print(response_res_1.get_json())
                response_res_2 = client.post('/reserve', json=reservation_2)
                print(response_res_2.get_json())
                #No tables with 6 seats
                response_res_3 = client.post('reserve', json=reservation_3)
                print(response_res_3.get_json())

                #restaurant with id 1 has a single table with 4 seats, thus the new reservation should fail returning 409 as status code
                #this code is associated with overbooking
                response_res_4 = client.post('/reserve', json=reservation_1)

                response_res_5 = client.post('/reserve', json=reservation_4)
        self.assertEqual(response_res_1.status_code, 200)
        self.assertEqual(response_res_2.status_code, 200)
        self.assertEqual(response_res_3.status_code, 404)
        self.assertEqual(response_res_4.status_code, 409)
        self.assertEqual(response_res_5.status_code, 404)


    def test_update_user_reservation(self):
        res_update_1 = {
            "new_reservation_time": datetime.combine(datetime.today(), time(hour=19, minute=30)).isoformat(),
            "new_seats": 4
        }
        res_update_2 = {
            "new_reservation_time": datetime.combine(datetime.today(), time(hour=12, minute=30)).isoformat(),
            "new_seats": 4
        }
        res_update_3 = {
            "new_reservation_time": datetime.combine(datetime.today(), time(hour=12, minute=30)).isoformat(),
            "new_seats": 6
        }
        with self.app.test_client() as client:
            with self.app.app_context():
                #This can be performed since there are no other conflicting reservations, the status_code of the response should be 200
                response_res_1 = client.put('customer_reservation/54', json=res_update_1)
                #This cannot, since there is a conflict with reservation with id=55 , the status_code of the response should be 409
                response_res_2 = client.put('customer_reservation/54', json=res_update_2)
                #this must return 404 since the restaurant with id=1 has no tables with seats=6
                response_res_3 = client.put('customer_reservation/54', json=res_update_3)
                #the reservation with id 123 does not exist
                response_res_4 = client.put('customer_reservation/123', json=res_update_1)
        self.assertEqual(response_res_1.status_code, 200)
        self.assertEqual(response_res_2.status_code, 409)
        self.assertEqual(response_res_3.status_code, 404)
        self.assertEqual(response_res_4.status_code, 404)
