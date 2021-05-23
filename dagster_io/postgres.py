from dagster import Field, String, resource
from models import Base, DataSource
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker


class SqlAlchemyPostgresWarehouse:
    def __init__(self, conn_str):
        self._conn_str = conn_str
        self._engine = create_engine(self._conn_str)

    def update_records(self, records):
        Base.metadata.bind = self._engine
        # Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        # with self._engine.connect() as connection:
        # raw_data = Base.metadata.tables['raw_data']
        # result = connection.execute(raw_data.insert().values(run_id=10, name= "hello", version=2, data='1'))
        # update data
        Session = sessionmaker()
        Session.configure(bind=self._engine)
        session = Session()
        try:
            for item in records:
                row = DataSource(**item)
                session.add(row)
            session.commit()
        except SQLAlchemyError as e:
            print(e)
        finally:
            session.close()


@resource(config_schema={"conn_str": Field(String)})
def postgres_warehouse_resource(_init_context):
    return SqlAlchemyPostgresWarehouse(_init_context.resource_config["conn_str"])


if __name__ == "__main__":
    pg = SqlAlchemyPostgresWarehouse(
        "postgresql+psycopg2://postgres:rwbo1103@localhost:5432/dagster"
    )

    pg.update_records()
