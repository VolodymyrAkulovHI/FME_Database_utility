import pandas as pd
import sqlalchemy as sa
from datetime import datetime
import re
from shapely import wkt
import win32com.client as win32

def read_sql_table_with_geom_cast(server, database, table, columns, geom_column=None):
    """
    Reads a SQL table and optionally casts a geometry column to WKT format.

    Args:
        server (str): The server address.
        database (str): The database name.
        table (str): The table name.
        columns (list of str): The list of columns to retrieve.
        geom_column (str, optional): The geometry column to cast as WKT. Defaults to None.

    Returns:
        pandas.DataFrame: The dataframe containing the retrieved data with the geometry column casted as WKT if specified.
    """
    # Construct the connection string for the SQL Server
    conn_str = f"mssql+pyodbc://{server}/{database}?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server"
    engine = sa.create_engine(conn_str)
    
    # Add the geometry column cast to VARCHAR(MAX) if specified
    if geom_column:
        columns = columns + [f"CAST({geom_column} AS VARCHAR(MAX)) AS {geom_column}"]
    select_columns = ", ".join(columns)
    query = f"SELECT {select_columns} FROM {table}"
    
    # Execute the SQL query and read the data into a DataFrame
    df = pd.read_sql(query, engine)
    
    # Convert the geometry column from WKT string to Shapely geometry if specified
    if geom_column:
        df[geom_column] = df[geom_column].apply(lambda val: wkt.loads(val) if pd.notnull(val) and re.search(r'\bNULL\b', val) is None else None)
    
    return df


def backup_dataframe(df, table_name):
    # Generate a timestamp for the backup file with a more readable format
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"{table_name}_backup_{timestamp}.csv"
    
    # Save the dataframe to a CSV file
    df.to_csv(filename, index=False)
    
    # Print a confirmation message with the backup file location
    print(f"Backup saved to {filename}")


def send_email(subject, body, to_email):
    # Create a new email item using Outlook
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    
    # Set the email subject, body, and recipient
    mail.Subject = subject
    mail.Body = body
    mail.To = to_email
    
    # Send the email
    mail.Send()
