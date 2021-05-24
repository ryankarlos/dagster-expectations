from contextlib import contextmanager

from dagster import resource
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from .models import Base, DataSource


@contextmanager
def session_scope(Base, engine):
    Base.metadata.bind = engine
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
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


def write_df_json_to_row(context, df, engine):
    run_id = context.run_id
    version = 1
    name = context.solid_handle.name
    json_str = df.to_json()
    with session_scope(Base, engine) as session:
        row = DataSource(run_id, name, version, json_str)
        context.log.info(f"Writing run with serialised json data input {row}")
        session.add(row)


class SqlAlchemyPostgresWarehouse:
    def __init__(self, conn_str):
        self._conn_str = conn_str
        self._engine = create_engine(self._conn_str)

    def handle_data_output(self, context, obj):
        write_df_json_to_row(context, obj, self._engine)


@resource
def postgres_warehouse_resource(_init_context):
    conn = _init_context.resource_config["conn_str"]
    return SqlAlchemyPostgresWarehouse(conn)
