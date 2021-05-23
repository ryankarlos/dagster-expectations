import pandas as pd
from dagster import DagsterType, TypeCheck


def is_pandas_dataframe(_, df):
    if not isinstance(df, pd.DataFrame):
        return TypeCheck(
            success=False, description=f"pd Dataframe not found, got {type(df)}"
        )

    return TypeCheck(
        success=True,
        description=f"pd Dataframe not found, got {type(df)}",
        metadata={"n_rows": df.shape[0], "n_cols": df.shape[1]},
    )


PandasDataFrame = DagsterType(
    name="PandasDataFrame",
    type_check_fn=is_pandas_dataframe,
    description="Checking if pandas dataframe returned in output",
)
