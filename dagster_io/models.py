import base64
import io
import pickle
from contextlib import contextmanager

import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

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


class Model(Base):
    __tablename__ = "model"

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


@contextmanager
def session_scope(base, engine):
    base.metadata.bind = engine
    # Base.metadata.drop_all(engine)
    base.metadata.create_all(engine)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(e)
        raise
    finally:
        session.close()


def write_df_json_to_row(context, df, base, engine, version=1):
    run_id = context.run_id
    name = context.solid_handle.name
    json_str = df.to_json()
    with session_scope(base, engine) as session:
        row = DataSource(run_id, name, version, json_str)
        context.log.info(f"Writing run with serialised json data input {row}")
        session.add(row)


def write_model_plot_to_row(context, obj, base, engine, version=1):
    run_id = context.run_id
    name = context.solid_handle.name
    with session_scope(base, engine) as session:
        if isinstance(obj, KMeans):
            result = pickle.dumps(obj)
        elif isinstance(obj, plt):
            s = io.BytesIO()
            plt.savefig(s, format="png")
            result = base64.b64encode(s.getvalue()).decode("utf-8").replace("\n", "")
        row = Model(run_id, name, version, result)
        context.log.info(f"Writing model and plot output {row}")
        session.add(row)
