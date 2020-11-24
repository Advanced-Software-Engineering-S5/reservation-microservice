import enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime, time

db = SQLAlchemy()

class ReservationState(enum.IntEnum):
    DECLINED = 0
    PENDING = 1
    ACCEPTED = 2
    SEATED = 3
    DONE = 4

    def __str__(self):
        return {
            self.DECLINED: "Declined",
            self.PENDING: "Pending",
            self.ACCEPTED: "Accepted",
            self.SEATED: "Seated",
            self.DONE: "Done"
        }.get(self)


class Reservation(db.Model):
    __tablename__ = 'reservation'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    #Many to one relationship
    user_id = db.Column(db.Integer)
    #Reservations - many to one relationship
    restaurant_id = db.Column(db.Integer)

    reservation_time = db.Column(db.DateTime, default=datetime.now())
    status = db.Column(db.Enum(ReservationState), default=ReservationState.PENDING)

    #One to one relationship
    table_no = db.Column(db.Integer)

    seats = db.Column(db.Integer, default=False)
    entrance_time = db.Column(db.DateTime, nullable=True)
    exit_time = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        res_dict = {
        'id': getattr(self, 'id'),
        'user_id': getattr(self, 'user_id'),
        'restaurant_id': getattr(self, 'restaurant_id'),
        'reservation_time': getattr(self, 'reservation_time').isoformat(),
        'status': getattr(self, 'status').__str__(),
        'table_no': getattr(self, 'table_no'),
        'seats': getattr(self, 'seats'),
        'entrance_time': getattr(self, 'entrance_time'),
        'exit_time': getattr(self, 'exit_time')}
        
        if res_dict['entrance_time'] is not None:
            res_dict['entrance_time'] = res_dict['entrance_time'].isoformat()
        if res_dict['exit_time'] is not None:
            res_dict['exit_time'] = res_dict['exit_time'].isoformat()
        
        return res_dict
