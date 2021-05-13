from sqlalchemy import (Boolean, Column, ForeignKey, Integer, Numeric, String,
                        create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Cookies(Base):

    __tablename__ = "cookies"

    cookie_id = Column(Integer, primary_key=True)
    cookie_name = Column(String(50), index=True)
    quantity = Column(Integer)
    unit_cost = Column(Integer)

    orders = relationship("Orders", back_populates="cookie")

    def __init__(self, name, quantity, unit_cost):
        self.cookie_name = name
        self.quantity = quantity
        self.unit_cost = unit_cost

    def __repr__(self):
        return (
            f"Cookie(cookie_name='{self.cookie_name}', "
            f"quantity={self.quantity}, "
            f"unit_cost={self.unit_cost})"
        )


class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer(), primary_key=True)
    name = Column(String(15), nullable=False, unique=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    balance = Column(Integer)

    orders = relationship("Orders", back_populates="user")

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


class Orders(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.user_id"))
    cookie_id = Column(ForeignKey("cookies.cookie_id"))
    quantity = Column(Integer, nullable=False)
    shipped = Column(Boolean(), default=False)

    user = relationship("Users", back_populates="orders")
    cookie = relationship("Cookies", back_populates="orders")

    def __init__(self, shipped, quantity):
        self.quantity = quantity
        self.shipped = shipped

    def __repr__(self):
        return f"Order(user_id={self.user_id}, " f"shipped={self.shipped})"


def create_session(name="sqlite:///:memory:", base=Base):
    engine = create_engine(name)
    base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def update_cookie_user(cookie_id):
    """
    Updates the cookie quantity and user balances for
    given cookie id
    """
    cookie = session.query(Cookies).get(cookie_id)
    print(f"Initial cookie quantity for cookie ID: {cookie_id}: {cookie.quantity}")

    for order in cookie.orders:
        print(
            f"Initial balances for user who purchase cookie_id: {cookie_id}: {order.user.name}: {order.user.balance}"
        )
        order.cookie.quantity = order.cookie.quantity - order.quantity
        order.user.balance = order.user.balance - order.cookie.unit_cost
        print(f"Updated balance for user: {order.user.name}: {order.user.balance}")

        session.add_all([order.cookie, order.user])
    print(f"Updated cookie quantity for cookie ID: {cookie_id}: {cookie.quantity}")
    session.commit()


if __name__ == "__main__":
    session = create_session()
    user = Users("Python", "python@something.co.uk", "111-111-1111", 1000)
    cookie = Cookies("chocolate chip", 20, 1)
    order = Orders(True, 2)
    order.cookie = cookie
    order.user = user
    session.add_all([user, cookie, order])
    session.commit()
    update_cookie_user(1)
