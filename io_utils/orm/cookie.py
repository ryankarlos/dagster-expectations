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
    unit_cost = Column(Numeric(12, 2))

    orders = relationship("Orders", back_populates="cookie")

    def __init__(self, name, quantity, unit_cost):
        self.cookie_name = name
        self.quantity = quantity
        self.unit_cost = unit_cost

    def __repr__(self):
        return (
            f"Cookie(cookie_name='{self.cookie_name}', "
            f"cookie_recipe_url='{self.cookie_recipe_url}', "
            f"cookie_sku='{self.cookie_sku}', "
            f"quantity={self.quantity}, "
            f"unit_cost={self.unit_cost})"
        )


class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    name = Column(String(15), nullable=False, unique=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)

    orders = relationship("Orders", back_populates="user")

    def __init__(self, name, email, phone):
        self.name = name
        self.email = email
        self.phone = phone

    def __repr__(self):
        return (
            f"User(username='{self.username}', email_address='{self.email_address}', "
            f"phone='{self.phone}',password='{self.password}')"
        )


class Orders(Base):
    __tablename__ = "orders"
    order_id = Column(Integer(), primary_key=True)
    user_id = Column(ForeignKey("users.user_id"))
    cookie_id = Column(ForeignKey("cookies.cookie_id"))
    shipped = Column(Boolean(), default=False)

    user = relationship("Users", back_populates="orders")
    cookie = relationship("Cookies", back_populates="orders")

    def __init__(self, shipped):
        self.shipped = shipped

    def __repr__(self):
        return f"Order(user_id={self.user_id}, " f"shipped={self.shipped})"


def create_session(name="sqlite:///:memory:", base=Base):
    engine = create_engine(name)
    base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


if __name__ == "__main__":
    session = create_session()
    user = Users("ryan", "rn@something.co.uk", "111-111-1111")
    cookie = Cookies("chocolate chip", 6, 0.50)
    order = Orders(shipped=True)
    session.add(user)
    session.add(cookie)

    print(str(order))
