from sqlalchemy import create_engine
import pandas as pd
import config as c

def connect_to_mysql():
    # Database connection parameters
    db_uri = c.db_uri_conf

    # Establish the connection
    engine = create_engine(db_uri)
    connection = engine.connect()

    # Write your SQL queries
#    book_query = "SELECT * FROM {}".format(c.book_data_for_reader)
#    user_query = "SELECT * FROM {}".format(c.user_data_for_reader)

    book_query = "SELECT * FROM {}".format(c.book_data_for_reader)
    user_query = """SELECT user_id as professor_id,
                  GROUP_CONCAT(interested_in ORDER BY interested_in ASC SEPARATOR ' ') AS interest_area
                  FROM {} GROUP BY user_id""".format(c.user_data_for_reader)

    # Load data into DataFrames
    book_df = pd.read_sql_query(book_query, connection)
    user_df = pd.read_sql_query(user_query, connection)

    # Close the connection
    connection.close()

    return book_df, user_df



