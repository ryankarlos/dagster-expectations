from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class DataSource(Base):
    __tablename__ = "datastore"

    run_id = Column(String, primary_key=True)
    name = Column(String(80))
    version = Column(Integer)
    data = Column(String)

    def __init__(self, run_id, name, version, data):
        self.run_id = run_id
        self.name = name
        self.version = version
        self.data = data

    def __repr__(self):
        return "<Data(run_id='{}', name='{}', version='{}', data={})>".format(
            self.run_id, self.name, self.version, self.data
        )


"""
class Features(Base):
    __tablename__ = "features"
    user_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    balance = Column(Integer)

    def __init__(self, name, email, phone, money):
        self.name = name
        self.email = email
        self.phone = phone
        self.balance = money

    def __repr__(self):
        return (
            f"User(username='{self.username}', email_address='{self.email}', "
            f"phone='{self.phone}', money='{self.balance}'"
        )


class Model(Base):
    __tablename__ = "model"
    order_id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    shipped = Column(Boolean(), default=False)

    def __init__(self, shipped, quantity):
        self.quantity = quantity
        self.shipped = shipped

    def __repr__(self):
        return f"Order(user_id={self.user_id}, " f"shipped={self.shipped})"
"""
