import pandas as pd
from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine

def query_mysql_via_ssh(ssh_host, ssh_port, ssh_user, ssh_password, db_user, db_password, db_name, query):
    # Start the SSH tunnel
    with SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_user,
        ssh_password=ssh_password,
        remote_bind_address=('localhost', 3306)
    ) as tunnel:
        # Connect to the database via the SSH tunnel using SQLAlchemy
        local_port = tunnel.local_bind_port
        connection_string = f"mysql+pymysql://{db_user}:{db_password}@127.0.0.1:{local_port}/{db_name}"
        engine = create_engine(connection_string)

        # Execute the query and load the results into a pandas DataFrame
        df = pd.read_sql_query(query, engine)
        df.rename(columns = {"name":"Title"}, inplace = True)
    return df

# Configuration
ssh_host = '192.168.1.228'
ssh_port = 22
ssh_user = 'infi'
ssh_password = 'Passw0rd'

db_user = 'infi'
db_password = 'infi'
db_name = 'br_system'

book_query = "SELECT * FROM book"  # Modify this query as needed
user_query = """SELECT user_id as professor_id,
              GROUP_CONCAT(interested_in ORDER BY interested_in ASC SEPARATOR ' ') AS interest_area 
              FROM user_interest GROUP BY user_id"""

# Call the function and get the DataFrame
df1 = query_mysql_via_ssh(ssh_host, ssh_port, ssh_user, ssh_password, db_user, db_password, db_name, book_query)
df2 = query_mysql_via_ssh(ssh_host, ssh_port, ssh_user, ssh_password, db_user, db_password, db_name, user_query)
