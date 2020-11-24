import unittest
import random
from flask import Flask
from datetime import datetime, time, date
from reservation_microservice.database import db, ReservationState, Reservation
from reservation_microservice.classes import customer_reservations as cr


class CustomerReservationsTest(unittest.TestCase):
    def setUp(self):
        self.data = {}

        self.restaurants = [
            {'id': 1,
            'avg_stay_time': time(hour=1, minute=30),
            'tables': [
                {
                    'table_id': 1,
                    'seats': 3
                }, {
                    'table_id': 2,
                    'seats': 4
                }, {
                    'table_id': 3,
                    'seats': 3
                }          
            ]},
            {'id': 2,
            'avg_stay_time': time(hour=2, minute=00),
            'tables': [
                {
                    'table_id': 4,
                    'seats': 5
                }, {
                    'table_id': 5,
                    'seats': 6
                }  
            ]},
            {'id': 3,
            'avg_stay_time': time(hour=2, minute=00),
            'tables': [
                {
                    'table_id': 6,
                    'seats': 2
                }, {
                    'table_id': 7,
                    'seats': 8
                }, {
                    'table_id': 8,
                    'seats': 4
                }          
            ]}
        ]
        self.users_ids = [1, 2, 3]

        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

        db.init_app(self.app)
        db.create_all(app=self.app)

        with self.app.app_context():
            self.data['reservations'] = [
                Reservation(user_id=self.users_ids[0],
                            restaurant_id=self.restaurants[0]['id'],
                            table_no=self.restaurants[0]['tables'][0]['table_id'],
                            reservation_time=datetime.combine(
                                datetime.now().date(), time(hour=13,
                                                            minute=00)),
                            seats=self.restaurants[0]['tables'][0]['seats']),
                Reservation(user_id=self.users_ids[1],
                            restaurant_id=self.restaurants[1]['id'],
                            table_no=self.restaurants[1]['tables'][0]['table_id'],
                            reservation_time=datetime.combine(
                                datetime.now().date(), time(hour=12,
                                                            minute=30)),
                            seats=self.restaurants[1]['tables'][0]['seats']),
                Reservation(user_id=self.users_ids[1],
                            restaurant_id=self.restaurants[1]['id'],
                            table_no=self.restaurants[1]['tables'][1]['table_id'],
                            reservation_time=datetime.combine(
                                datetime.now().date(), time(hour=12,
                                                            minute=30)),
                            status=ReservationState.DECLINED,
                            seats=self.restaurants[1]['tables'][1]['seats']),
                Reservation(user_id=self.users_ids[1],
                            restaurant_id=self.restaurants[1]['id'],
                            table_no=self.restaurants[1]['tables'][1]['table_id'],
                            reservation_time=datetime.combine(
                                datetime.now().date(), time(hour=11,
                                                            minute=00)),
                            status=ReservationState.DONE,
                            seats=self.restaurants[1]['tables'][1]['seats']),
                Reservation(user_id=self.users_ids[2],
                            restaurant_id=self.restaurants[2]['id'],
                            table_no=self.restaurants[2]['tables'][0]['table_id'],
                            reservation_time=datetime.combine(
                                datetime.now().date(),
                                time(hour=(datetime.now().time().hour + 1) % 24,
                                     minute=15)),
                            status=ReservationState.ACCEPTED,
                            seats=self.restaurants[2]['tables'][0]['seats']),
                Reservation(user_id=self.users_ids[2],
                            restaurant_id=self.restaurants[2]['id'],
                            table_no=self.restaurants[2]['tables'][1]['table_id'],
                            reservation_time=datetime.combine(
                                datetime.now().date(),
                                time(hour=(datetime.now().time().hour + 1) % 24,
                                     minute=30)),
                            status=ReservationState.PENDING,
                            seats=self.restaurants[2]['tables'][1]['seats']),
                Reservation(user_id=self.users_ids[2],
                            restaurant_id=self.restaurants[2]['id'],
                            table_no=self.restaurants[2]['tables'][2]['table_id'],
                            reservation_time=datetime.combine(
                                datetime.now().date(),
                                time(hour=(datetime.now().time().hour + 1) % 24,
                                     minute=00)),
                            status=ReservationState.DECLINED,
                            seats=self.restaurants[2]['tables'][2]['seats']),
                Reservation(user_id=self.users_ids[1],
                            restaurant_id=self.restaurants[0]['id'],
                            table_no=self.restaurants[0]['tables'][2]['table_id'],
                            reservation_time=datetime.combine(
                                datetime.now().date(), time(hour=12,
                                                            minute=30)),
                            status=ReservationState.SEATED,
                            seats=self.restaurants[0]['tables'][2]['seats'])
            ]

            db.session.add_all(self.data['reservations'])
            db.session.commit()

    def test_get_overlapping_tables_restaurant1(self):
        res_time = time(hour=12, minute=00)
        res_date = datetime.now().date()
        res_datetime = datetime.combine(res_date, res_time)
        with self.app.app_context():
            #restaurant = db.session.query(Restaurant).filter_by(id=1).first()
            overlapping_tables = cr.get_overlapping_tables(
                restaurant_id= self.restaurants[0]['id'],
                reservation_time=res_datetime,
                reservation_seats=3,
                avg_stay_time=self.restaurants[0]['avg_stay_time'])
        self.assertEqual(2, len(overlapping_tables))
        self.assertEqual(1, overlapping_tables[0])
        self.assertEqual(3, overlapping_tables[1])

    def test_get_ovelapping_tables_restaurant2(self):
        res_time = time(hour=13, minute=00)
        res_date = datetime.now().date()
        res_datetime = datetime.combine(res_date, res_time)
        with self.app.app_context():
            #restaurant = db.session.query(Restaurant).filter_by(id=2).first()
            overlapping_tables = cr.get_overlapping_tables(
                restaurant_id= self.restaurants[1]['id'],
                reservation_time=res_datetime,
                reservation_seats=5,
                avg_stay_time=self.restaurants[1]['avg_stay_time'])
        self.assertEqual(1, len(overlapping_tables))
        self.assertEqual(4, overlapping_tables[0])

    def test_no_overlapping_tables(self):
        res_time = time(hour=21, minute=00)
        res_date = datetime.now().date()
        res_datetime = datetime.combine(res_date, res_time)
        with self.app.app_context():
            #restaurant = db.session.query(Restaurant).filter_by(id=1).first()
            overlapping_tables = cr.get_overlapping_tables(
                restaurant_id=self.restaurants[0]['id'],
                reservation_time=res_datetime,
                reservation_seats=3,
                avg_stay_time=self.restaurants[0]['avg_stay_time'])
        self.assertEqual(0, len(overlapping_tables))

    def test_get_overlapping_tables_declined_and_done_reservations(self):
        res_time = time(hour=12, minute=30)
        res_date = datetime.now().date()
        res_datetime = datetime.combine(res_date, res_time)
        with self.app.app_context():
            #restaurant = db.session.query(Restaurant).filter_by(id=2).first()
            overlapping_tables = cr.get_overlapping_tables(
                restaurant_id=self.restaurants[2]['id'],
                reservation_time=res_datetime,
                reservation_seats=6,
                avg_stay_time=self.restaurants[2]['avg_stay_time'])
            self.assertEqual(0, len(overlapping_tables))

    def test_is_overbooked(self):
        res_time_1 = time(hour=13, minute=00)
        res_date_1 = datetime.now().date()
        res_datetime_1 = datetime.combine(res_date_1, res_time_1)
        res_seats_1 = 5
        #mock the response from restaurant service
        res_tables_1 = [t['table_id'] for t in self.restaurants[1]['tables'] if t['seats'] == res_seats_1]

        res_time_2 = time(hour=21, minute=00)
        res_date_2 = datetime.now().date()
        res_datetime_2 = datetime.combine(res_date_2, res_time_2)
        res_seats_2 = 3
        #mock the response from restaurant service
        res_tables_2 = [t['table_id'] for t in self.restaurants[0]['tables'] if t['seats'] == res_seats_2]

        with self.app.app_context():
            #restaurant_1 = db.session.query(Restaurant).filter_by(id=2).first()
            overlapping_tables_1 = cr.get_overlapping_tables(
                restaurant_id=self.restaurants[1]['id'],
                reservation_time=res_datetime_1,
                reservation_seats=res_seats_1,
                avg_stay_time=self.restaurants[1]['avg_stay_time'])
            overbooked_1 = cr.is_overbooked(
                overlapping_tables=overlapping_tables_1,
                restaurant_tables=res_tables_1)

            #restaurant_2 = db.session.query(Restaurant).filter_by(id=1).first()
            overlapping_tables_2 = cr.get_overlapping_tables(
                restaurant_id=self.restaurants[0]['id'],
                reservation_time=res_datetime_2,
                reservation_seats=res_seats_2,
                avg_stay_time=self.restaurants[0]['avg_stay_time'])
            overbooked_2 = cr.is_overbooked(
                overlapping_tables=overlapping_tables_2,
                restaurant_tables=res_tables_2)
        self.assertEqual(True, overbooked_1)
        self.assertEqual(False, overbooked_2)

    def test_assign_table_to_reservation(self):
        res_time_free = time(hour=21, minute=00)
        res_date_free = datetime.now().date()
        res_datetime_free = datetime.combine(res_date_free, res_time_free)
        res_seats_free = 3

        res_tables_free = [t['table_id'] for t in self.restaurants[0]['tables'] if t['seats'] == res_seats_free]

        res_time_none = time(hour=13, minute=00)
        res_date_none = datetime.now().date()
        res_datetime_none = datetime.combine(res_date_none, res_time_none)
        res_seats_none = 5

        res_tables_none = [t['table_id'] for t in self.restaurants[1]['tables'] if t['seats'] == res_seats_none]

        with self.app.app_context():
            #restaurant_free = db.session.query(Restaurant).filter_by(
             #   id=1).first()
            overlapping_tables_free = cr.get_overlapping_tables(
                restaurant_id=self.restaurants[0]['id'],
                reservation_time=res_datetime_free,
                reservation_seats=res_seats_free,
                avg_stay_time=self.restaurants[0]['avg_stay_time'])
            
            assigned_table_1 = cr.assign_table_to_reservation(
                overlapping_tables=overlapping_tables_free,
                restaurant_tables=res_tables_free)

            #restaurant_none = db.session.query(Restaurant).filter_by(
            #    id=2).first()
            overlapping_tables_none = cr.get_overlapping_tables(
                restaurant_id=self.restaurants[1]['id'],
                reservation_time=res_datetime_none,
                reservation_seats=res_seats_none,
                avg_stay_time=self.restaurants[1]['avg_stay_time'])
            assigned_table_2 = cr.assign_table_to_reservation(
                overlapping_tables=overlapping_tables_none,
                restaurant_tables=res_tables_none)
        self.assertEqual(1, assigned_table_1)
        self.assertIsNone(assigned_table_2)

    def test_add_reservation(self):
        res_time = time(hour=21, minute=00)
        res_date = datetime.now().date()
        with self.app.app_context():
            user = self.users_ids[0]
            restaurant = self.restaurants[0]['id']
            table = self.restaurants[0]['tables'][0]['table_id']
            reservation = Reservation()
            reservation.id = 100
            reservation.user_id = user
            reservation.restaurant_id = restaurant
            reservation.reservation_time = datetime.combine(res_date, res_time)
            reservation.seats = table
            cr.add_reservation(reservation)

            reservation_in_db = db.session.query(Reservation).filter_by(
                id=100).first()
        self.assertEqual(reservation, reservation_in_db)

    def test_get_user_reservations(self):
        with self.app.app_context():
            reservations = cr.get_user_reservations(3)
        for reservation in reservations:
            print(reservation.reservation_time)
            self.assertEqual(reservation.user_id, 3)
            self.assertGreater(reservation.reservation_time, datetime.now())

    def test_is_safely_updatable(self):
        with self.app.app_context():
            reservation = db.session.query(Reservation).filter_by(id=1).first()
            new_res_time_safe = cr.diff_time(
                reservation.reservation_time.time(), time(hour=1))
            new_res_time_not_safe = time(hour=3)

            avg_stay_time = self.restaurants[0]['avg_stay_time']

            res_date_safe = datetime.combine(
                reservation.reservation_time.date(), new_res_time_safe)
            res_date_not_safe = datetime.combine(
                reservation.reservation_time.date(), new_res_time_not_safe)

            self.assertTrue(cr.is_safely_updatable(reservation, avg_stay_time, res_date_safe))
            self.assertFalse(
                cr.is_safely_updatable(reservation, avg_stay_time, res_date_not_safe))


    def test_delete_reservation(self):
        with self.app.app_context():
            #There should be a reservation with id 1
            self.assertTrue(cr.delete_reservation(reservation_id=1))
            #reservation_1 should not exist after the execution of the method
            reservation_1 = db.session.query(Reservation).filter_by(
                id=1).first()
            self.assertIsNone(reservation_1)
            #There should not be a reservation with id 42
            self.assertFalse(cr.delete_reservation(reservation_id=42))

    def test_sum_time(self):
        t1 = time(hour=3, minute=00)
        t2 = time(hour=1, minute=00)
        self.assertEqual(time(hour=4, minute=00), cr.sum_time(t1, t2))
        self.assertIsInstance(cr.sum_time(t1, t2), time)

    def test_diff_time(self):
        t1 = time(hour=3, minute=00)
        t2 = time(hour=1, minute=00)
        self.assertEqual(time(hour=2, minute=00), cr.diff_time(t1, t2))
        self.assertIsInstance(cr.diff_time(t1, t2), time)


if __name__ == '__main__':
    unittest.main()
