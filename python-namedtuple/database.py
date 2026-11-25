PASSENGER_COLUMNS = ("id", "first_name", "last_name", "class")


def get_column_names(table):
    """Return the column names for a given table name."""
    if table == "passenger":
        return PASSENGER_COLUMNS
    raise ValueError(f"unknown table {table}")


def get_passenger_by_id(passenger_id):
    if passenger_id == 1234:
        return (1234, "John", "Doe", "Business")
    raise ValueError(f"no record with id={passenger_id}")
