import unittest
import requests
from reservation_microservice.classes.tests.utils import add_random_visit_to_place, create_app_for_test
from reservation_microservice.classes.contact_tracing import contact_tracing
from reservation_microservice.database import db
from datetime import datetime
import os

app = create_app_for_test()
class ContactTracingTest(unittest.TestCase):

    def setUp(self):
        db.create_all(app=app)
        with app.app_context():

            user1 = dict(firstname="user1",
                 lastname="user1",
                 email="user1@example.com",
                 phone='324455123',
                 password="user1",
                 dateofbirth=datetime(2020, 10, 31).isoformat())

            user2 = dict(firstname="user2",
                 lastname="user2",
                 email="user2@example.com",
                 phone='324455321',
                 password="user2",
                 dateofbirth=datetime(2020, 10, 31).isoformat())
            user3 = dict(firstname="user3",
                 lastname="user3",
                 email="user3@example.com",
                 phone='324459121',
                 password="user3",
                 dateofbirth=datetime(2020, 10, 31).isoformat())
            self.users = [user1, user2, user3]
            self.uids = []

    def tearDown(self):
        db.drop_all(app=app)
        # delete users created in User service
        for id in self.uids:
            resp = requests.delete(f"http://{os.environ.get('GOS_USER')}/users/{id}")


    def test_contact_tracing(self):
        with app.app_context():
            n_users = 3
            # create some users
            self.uids = [requests.post(f'http://{os.environ.get("GOS_USER")}/user', json=self.users[i]).json() for i in range(n_users)]
            print('user ids:', self.uids)
            # have users visit same place at same time
            add_random_visit_to_place(1, datetime.now(), self.uids)
            # check contact tracing (assume one user is positive, check others are returned)
            test_app = app.test_client()
            users = test_app.get(f'/contact_tracing/{self.uids[0]}').get_json()['users']
            self.assertEqual(len(users), len(self.uids)-1)
            for user in users:
                self.assertIn(user['id'], self.uids)
                self.assertNotEqual(user['id'], self.uids[0])
            