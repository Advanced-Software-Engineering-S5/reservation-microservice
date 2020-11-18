import unittest
from reservation_microservice.database import Reservation, db, User, RestaurantTable, Restaurant
import random
from flask import Flask
from datetime import datetime, time, date
from reservation_microservice.database import db, User, Restaurant, Reservation, RestaurantTable, ReservationState
from reservation_microservice.classes import customer_reservations as cr


class CustomerReservationsTest(unittest.TestCase):
    def setUp(self):
        self.data = {}
        self.data['restaurants'] = [
            Restaurant(id=1,
                       name="op1 restaurant",
                       likes=1,
                       lat=1,
                       lon=1,
                       phone='1337',
                       avg_stay_time=time(hour=1, minute=30)),
            Restaurant(id=2,
                       name="op2 restaurant",
                       likes=3,
                       lat=2,
                       lon=2,
                       phone='1338',
                       avg_stay_time=time(hour=2, minute=00)),
            Restaurant(id=3,
                       name="op3 restaurant",
                       likes=10,
                       lat=2,
                       lon=2,
                       phone='1339',
                       avg_stay_time=time(hour=2, minute=00))
        ]

        self.data['users'] = [
            User(id=1,
                 firstname="op1",
                 lastname="op1",
                 email="op1@op1.com",
                 password="op1"),
            User(
                id=2,
                firstname="op2",
                lastname="op2",
                email="op2@op2.com",
                password="op2",
            ),
            User(
                id=3,
                firstname="op3",
                lastname="op3",
                email="op3@op3.com",
                password="op3",
            )
        ]

        self.data['tables'] = [
            RestaurantTable(table_id=1,
                            seats=3,
                            restaurant_id=self.data['restaurants'][0].id),
            RestaurantTable(table_id=2,
                            seats=4,
                            restaurant_id=self.data['restaurants'][0].id),
            RestaurantTable(table_id=3,
                            seats=3,
                            restaurant_id=self.data['restaurants'][0].id),
            RestaurantTable(table_id=4,
                            seats=5,
                            restaurant_id=self.data['restaurants'][1].id),
            RestaurantTable(table_id=5,
                            seats=6,
                            restaurant_id=self.data['restaurants'][1].id),
            RestaurantTable(table_id=6,
                            seats=2,
                            restaurant_id=self.data['restaurants'][2].id),
            RestaurantTable(table_id=7,
                            seats=8,
                            restaurant_id=self.data['restaurants'][2].id),
            RestaurantTable(table_id=8,
                            seats=4,
                            restaurant_id=self.data['restaurants'][2].id)
        ]

        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

        db.init_app(self.app)
        db.create_all(app=self.app)

        with self.app.app_context():
            for lst in self.data.values():
                db.session.add_all(lst)

            db.session.commit()

            #This has to be declared here otherwise User.id won't be available
            self.data['reservations'] = [
                Reservation(user_id=self.data['users'][0].id,
                            restaurant_id=self.data['restaurants'][0].id,
                            table_no=self.data['tables'][0].table_id,
                            reservation_time=datetime.combine(
                                datetime.now().date(), time(hour=13,
                                                            minute=00)),
                            seats=self.data['tables'][0].seats),
                Reservation(user_id=self.data['users'][1].id,
                            restaurant_id=self.data['restaurants'][1].id,
                            table_no=self.data['tables'][3].table_id,
                            reservation_time=datetime.combine(
                                datetime.now().date(), time(hour=12,
                                                            minute=30)),
                            seats=self.data['tables'][3].seats),
                Reservation(user_id=self.data['users'][1].id,
                            restaurant_id=self.data['restaurants'][1].id,
                            table_no=self.data['tables'][4].table_id,
                            reservation_time=datetime.combine(
                                datetime.now().date(), time(hour=12,
                                                            minute=30)),
                            status=ReservationState.DECLINED,
                            seats=self.data['tables'][4].seats),
                Reservation(user_id=self.data['users'][1].id,
                            restaurant_id=self.data['restaurants'][1].id,
                            table_no=self.data['tables'][4].table_id,
                            reservation_time=datetime.combine(
                                datetime.now().date(), time(hour=11,
                                                            minute=00)),
                            status=ReservationState.DONE,
                            seats=self.data['tables'][1].seats),
                Reservation(user_id=self.data['users'][2].id,
                            restaurant_id=self.data['restaurants'][2].id,
                            table_no=self.data['tables'][5].table_id,
                            reservation_time=datetime.combine(
                                datetime.now().date(),
                                time(hour=(datetime.now().time().hour + 1) % 24,
                                     minute=15)),
                            status=ReservationState.ACCEPTED,
                            seats=self.data['tables'][5].seats),
                Reservation(user_id=self.data['users'][2].id,
                            restaurant_id=self.data['restaurants'][2].id,
                            table_no=self.data['tables'][6].table_id,
                            reservation_time=datetime.combine(
                                datetime.now().date(),
                                time(hour=(datetime.now().time().hour + 1) % 24,
                                     minute=30)),
                            status=ReservationState.PENDING,
                            seats=self.data['tables'][6].seats),
                Reservation(user_id=self.data['users'][2].id,
                            restaurant_id=self.data['restaurants'][2].id,
                            table_no=self.data['tables'][7].table_id,
                            reservation_time=datetime.combine(
                                datetime.now().date(),
                                time(hour=(datetime.now().time().hour + 1) % 24,
                                     minute=00)),
                            status=ReservationState.DECLINED,
                            seats=self.data['tables'][7].seats),
                Reservation(user_id=self.data['users'][1].id,
                            restaurant_id=self.data['restaurants'][0].id,
                            table_no=self.data['tables'][2].table_id,
                            reservation_time=datetime.combine(
                                datetime.now().date(), time(hour=12,
                                                            minute=30)),
                            status=ReservationState.SEATED,
                            seats=self.data['tables'][2].seats)
            ]

            db.session.add_all(self.data['reservations'])
            db.session.commit()

    def test_get_overlapping_tables_restaurant1(self):
        res_time = time(hour=12, minute=00)
        res_date = datetime.now().date()
        res_datetime = datetime.combine(res_date, res_time)
        with self.app.app_context():
            restaurant = db.session.query(Restaurant).filter_by(id=1).first()
            overlapping_tables = cr.get_overlapping_tables(
                restaurant_id=restaurant.id,
                reservation_time=res_datetime,
                reservation_seats=3,
                avg_stay_time=restaurant.avg_stay_time)
        self.assertEqual(2, len(overlapping_tables))
        self.assertEqual(1, overlapping_tables[0])
        self.assertEqual(3, overlapping_tables[1])

    def test_get_ovelapping_tables_restaurant2(self):
        res_time = time(hour=13, minute=00)
        res_date = datetime.now().date()
        res_datetime = datetime.combine(res_date, res_time)
        with self.app.app_context():
            restaurant = db.session.query(Restaurant).filter_by(id=2).first()
            overlapping_tables = cr.get_overlapping_tables(
                restaurant_id=restaurant.id,
                reservation_time=res_datetime,
                reservation_seats=5,
                avg_stay_time=restaurant.avg_stay_time)
        self.assertEqual(1, len(overlapping_tables))
        self.assertEqual(4, overlapping_tables[0])

    def test_no_overlapping_tables(self):
        res_time = time(hour=21, minute=00)
        res_date = datetime.now().date()
        res_datetime = datetime.combine(res_date, res_time)
        with self.app.app_context():
            restaurant = db.session.query(Restaurant).filter_by(id=1).first()
            overlapping_tables = cr.get_overlapping_tables(
                restaurant_id=restaurant.id,
                reservation_time=res_datetime,
                reservation_seats=3,
                avg_stay_time=restaurant.avg_stay_time)
        self.assertEqual(0, len(overlapping_tables))

    def test_get_overlapping_tables_declined_and_done_reservations(self):
        res_time = time(hour=12, minute=30)
        res_date = datetime.now().date()
        res_datetime = datetime.combine(res_date, res_time)
        with self.app.app_context():
            restaurant = db.session.query(Restaurant).filter_by(id=2).first()
            overlapping_tables = cr.get_overlapping_tables(
                restaurant_id=restaurant.id,
                reservation_time=res_datetime,
                reservation_seats=6,
                avg_stay_time=restaurant.avg_stay_time)
            self.assertEqual(0, len(overlapping_tables))

    def test_is_overbooked(self):
        res_time_1 = time(hour=13, minute=00)
        res_date_1 = datetime.now().date()
        res_datetime_1 = datetime.combine(res_date_1, res_time_1)
        res_seats_1 = 5

        res_time_2 = time(hour=21, minute=00)
        res_date_2 = datetime.now().date()
        res_datetime_2 = datetime.combine(res_date_2, res_time_2)
        res_seats_2 = 3
        with self.app.app_context():
            restaurant_1 = db.session.query(Restaurant).filter_by(id=2).first()
            overlapping_tables_1 = cr.get_overlapping_tables(
                restaurant_id=restaurant_1.id,
                reservation_time=res_datetime_1,
                reservation_seats=res_seats_1,
                avg_stay_time=restaurant_1.avg_stay_time)
            overbooked_1 = cr.is_overbooked(
                restaurant_id=restaurant_1.id,
                reservation_seats=res_seats_1,
                overlapping_tables=overlapping_tables_1)

            restaurant_2 = db.session.query(Restaurant).filter_by(id=1).first()
            overlapping_tables_2 = cr.get_overlapping_tables(
                restaurant_id=restaurant_2.id,
                reservation_time=res_datetime_2,
                reservation_seats=res_seats_2,
                avg_stay_time=restaurant_2.avg_stay_time)
            overbooked_2 = cr.is_overbooked(
                restaurant_id=restaurant_2.id,
                reservation_seats=res_seats_2,
                overlapping_tables=overlapping_tables_2)
        self.assertEqual(True, overbooked_1)
        self.assertEqual(False, overbooked_2)

    def test_assign_table_to_reservation(self):
        res_time_free = time(hour=21, minute=00)
        res_date_free = datetime.now().date()
        res_datetime_free = datetime.combine(res_date_free, res_time_free)
        res_seats_free = 3

        res_time_none = time(hour=13, minute=00)
        res_date_none = datetime.now().date()
        res_datetime_none = datetime.combine(res_date_none, res_time_none)
        res_seats_none = 5

        with self.app.app_context():
            restaurant_free = db.session.query(Restaurant).filter_by(
                id=1).first()
            overlapping_tables_free = cr.get_overlapping_tables(
                restaurant_id=restaurant_free.id,
                reservation_time=res_datetime_free,
                reservation_seats=res_seats_free,
                avg_stay_time=restaurant_free.avg_stay_time)
            free_table = db.session.query(RestaurantTable).filter_by(
                restaurant_id=restaurant_free.id).filter_by(
                    seats=res_seats_free).filter(
                        RestaurantTable.table_id.notin_(
                            overlapping_tables_free)).first()
            assigned_table_1 = cr.assign_table_to_reservation(
                overlapping_tables=overlapping_tables_free,
                restaurant_id=restaurant_free.id,
                reservation_seats=res_seats_free)

            restaurant_none = db.session.query(Restaurant).filter_by(
                id=2).first()
            overlapping_tables_none = cr.get_overlapping_tables(
                restaurant_id=restaurant_none.id,
                reservation_time=res_datetime_none,
                reservation_seats=res_seats_none,
                avg_stay_time=restaurant_none.avg_stay_time)
            assigned_table_2 = cr.assign_table_to_reservation(
                overlapping_tables=overlapping_tables_none,
                restaurant_id=restaurant_none.id,
                reservation_seats=res_seats_none)
        self.assertEqual(free_table, assigned_table_1)
        self.assertIsNone(assigned_table_2)

    def test_add_reservation(self):
        res_time = time(hour=21, minute=00)
        res_date = datetime.now().date()
        with self.app.app_context():
            user = db.session.query(User).filter_by(id=1).first()
            restaurant = db.session.query(Restaurant).filter_by(id=1).first()
            table = db.session.query(RestaurantTable).filter_by(
                table_id=1).first()
            reservation = Reservation()
            reservation.id = 100
            reservation.user_id = user.id
            reservation.restaurant_id = restaurant.id
            reservation.reservation_time = datetime.combine(res_date, res_time)
            reservation.seats = table.seats
            cr.add_reservation(reservation)

            reservation_in_db = db.session.query(Reservation).filter_by(
                id=100).first()
        self.assertEqual(reservation, reservation_in_db)

    def test_reserve(self):
        res_time1 = time(hour=15, minute=00)
        res_date1 = datetime.now().date()
        res_datetime1 = datetime.combine(res_date1, res_time1)
        res_time2 = time(hour=12, minute=30)
        res_date2 = datetime.now().date()
        res_datetime2 = datetime.combine(res_date2, res_time2)

        with self.app.app_context():
            user = db.session.query(User).filter_by(id=1).first()
            restaurant = db.session.query(Restaurant).filter_by(id=1).first()
            is_reserved1 = cr.reserve(restaurant, res_datetime1, 3, user.id)
            is_reserved2 = cr.reserve(restaurant, res_datetime2, 3, user.id)
            self.assertTrue(is_reserved1)
            self.assertFalse(is_reserved2)

    def test_get_user_reservations(self):
        with self.app.app_context():
            reservations = cr.get_user_reservations(3)
        for reservation in reservations:
            print(reservation.reservation_time)
            self.assertEqual(reservation.user_id, 3)
            self.assertGreater(reservation.reservation_time, datetime.now())

    def test_update_safely_updatable_reservation(self):
        with self.app.app_context():
            reservation = db.session.query(Reservation).filter_by(id=1).first()
            new_time = time(hour=12, minute=45)
            new_res_time = datetime.combine(datetime.now().date(), new_time)
            new_seats = reservation.seats
            self.assertTrue(
                cr.update_reservation(reservation,
                                      new_reservation_time=new_res_time,
                                      new_seats=new_seats))
            updated_res = db.session.query(Reservation).filter_by(id=1).first()
            self.assertEqual(updated_res.reservation_time, new_res_time)
            self.assertEqual(updated_res.seats, new_seats)
            self.assertEqual(updated_res.status.__str__(), 'Pending')

    def test_update_reservation_same_seats(self):
        with self.app.app_context():
            reservation = db.session.query(Reservation).filter_by(id=1).first()
            new_time = time(hour=21, minute=45)
            new_res_time = datetime.combine(datetime.now().date(), new_time)
            new_seats = reservation.seats
            self.assertTrue(
                cr.update_reservation(reservation,
                                      new_reservation_time=new_res_time,
                                      new_seats=new_seats))
            updated_res = db.session.query(Reservation).filter_by(id=1).first()
            self.assertEqual(updated_res.reservation_time, new_res_time)
            self.assertEqual(updated_res.seats, new_seats)
            self.assertEqual(updated_res.status.__str__(), 'Pending')

    def test_update_reservation_diff_seats(self):
        with self.app.app_context():
            reservation = db.session.query(Reservation).filter_by(id=1).first()
            new_time = time(hour=21, minute=45)
            new_res_time = datetime.combine(datetime.now().date(), new_time)
            new_seats = 4
            self.assertTrue(
                cr.update_reservation(reservation,
                                      new_reservation_time=new_res_time,
                                      new_seats=new_seats))
            updated_res = db.session.query(Reservation).filter_by(id=1).first()
            self.assertEqual(updated_res.reservation_time, new_res_time)
            self.assertEqual(updated_res.seats, new_seats)
            # The new reservation is assigned a new table because of the new number of seats.
            # This new table should the only 4 seats table of Restaurant 1 (== Table 2)
            self.assertEqual(updated_res.table_no, 2)
            self.assertEqual(updated_res.status.__str__(), 'Pending')

    def test_update_reservation_diff_date(self):
        with self.app.app_context():
            reservation = db.session.query(Reservation).filter_by(id=1).first()
            new_time = time(hour=21, minute=45)
            new_res_time = datetime.combine(date(2020, 11, 15), new_time)
            new_seats = reservation.seats
            self.assertTrue(
                cr.update_reservation(reservation,
                                      new_reservation_time=new_res_time,
                                      new_seats=new_seats))
            updated_res = db.session.query(Reservation).filter_by(id=1).first()
            self.assertEqual(updated_res.reservation_time, new_res_time)
            self.assertEqual(updated_res.seats, new_seats)

            self.assertEqual(updated_res.status.__str__(), 'Pending')

    def test_is_safely_updatable(self):
        with self.app.app_context():
            reservation = db.session.query(Reservation).filter_by(id=1).first()
            new_res_time_safe = cr.diff_time(
                reservation.reservation_time.time(), time(hour=1))
            new_res_time_not_safe = time(hour=3)

            res_date_safe = datetime.combine(
                reservation.reservation_time.date(), new_res_time_safe)
            res_date_not_safe = datetime.combine(
                reservation.reservation_time.date(), new_res_time_not_safe)

            self.assertTrue(cr.is_safely_updatable(reservation, res_date_safe))
            self.assertFalse(
                cr.is_safely_updatable(reservation, res_date_not_safe))

    def test_is_existing_reservation(self):
        existing_time = datetime.combine(datetime.now().date(), time(12, 30))
        non_existing_time = datetime.combine(datetime.now().date(),
                                             time(23, 00))
        with self.app.app_context():
            self.assertTrue(
                cr.is_existing_reservation(restaurant_id=1,
                                           user_id=2,
                                           reservation_time=existing_time,
                                           seats=3))
            self.assertFalse(
                cr.is_existing_reservation(restaurant_id=1,
                                           user_id=2,
                                           reservation_time=non_existing_time,
                                           seats=3))

    def test_update_reservation_fail(self):
        with self.app.app_context():
            reservation = db.session.query(Reservation).filter_by(id=1).first()
            new_time = time(hour=21, minute=45)
            new_res_time = datetime.combine(datetime.now().date(), new_time)
            # Restaurant 1 has no tables with 10 seats, thus the reservation should not be updated
            new_seats = 10
            self.assertFalse(
                cr.update_reservation(reservation,
                                      new_reservation_time=new_res_time,
                                      new_seats=new_seats))
            updated_res = db.session.query(Reservation).filter_by(id=1).first()
            self.assertEqual(reservation, updated_res)

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
