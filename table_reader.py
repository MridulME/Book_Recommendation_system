from sqlalchemy import create_engine
import pandas as pd
import config as c
import numpy as np

def connect_to_mysql():
    # Database connection parameters
    db_uri = 'mysql+pymysql://infi:infi@127.0.0.1:3306/br_system'

    # Establish the connection
    engine = create_engine(db_uri)
    connection = engine.connect()

    # Write your SQL queries
#    book_query = "SELECT * FROM {}".format(c.book_data_for_reader)
#    user_query = "SELECT * FROM {}".format(c.user_data_for_reader)

    book_query = "SELECT * FROM book"
    user_query = """SELECT user_id as professor_id,
                  GROUP_CONCAT(interested_in ORDER BY interested_in ASC SEPARATOR ' ') AS interest_area
                  FROM user_interest GROUP BY user_id"""

    # Load data into DataFrames
    book_df = pd.read_sql_query(book_query, connection)
#    filter_df = book_df[book_df['published_date'].isna()]
#    print(filter_df)
    book_df['published_date'] = pd.to_datetime(book_df['published_date'],errors = 'coerce')
    book_df['created_date'] = pd.to_datetime(book_df['created_date'],errors = 'coerce')
#     book_df['published_date'] = book_df['published_date'].dt.strftime('%m-%d-%Y')
    book_df['published_date'] = book_df['published_date'].fillna('null')
    book_df['created_date'] = book_df['created_date'].fillna('null')
    #print(book_df.dtypes)
    book_df.rename(columns = {"name":"Title"}, inplace = True)
    user_df = pd.read_sql_query(user_query, connection)
    
    

    # Close the connection
    connection.close()

    return book_df, user_df

#a,b = connect_to_mysql()

#print(a)
