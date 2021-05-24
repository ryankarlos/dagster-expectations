from dagster import resource
from sqlalchemy import create_engine

from .models import Base, write_df_json_to_row, write_model_plot_to_row


class SqlAlchemyPostgresWarehouse:
    def __init__(self, conn_str):
        self._conn_str = conn_str
        self._engine = create_engine(self._conn_str)

    def handle_data_output(self, context, obj):
        write_df_json_to_row(context, obj, Base, self._engine)

    def update_model_plot(self, context, obj):
        write_model_plot_to_row(context, obj, Base, self._engine)


@resource
def postgres_warehouse_resource(_init_context):
    conn = _init_context.resource_config["conn_str"]
    return SqlAlchemyPostgresWarehouse(conn)
