import configparser
import pandas as pd
import mysql.connector
from mysql.connector import Error
import sqlite3

# Create a DB connection. If host, user and user_password are None, sqlite will be used.
def create_connection(db_name, host=None, user=None, user_password=None):
    connection = None
    if not host and not user and not user_password:
        connection = sqlite3.connect(db_name)
        print('Using sqlite for development.')
    else:
        try:
            connection = mysql.connector.connect(
                host=host,
                user=user,
                passwd=user_password,
                database=db_name
            )
            print("Connection to MySQL DB successful")
        except Error as e:
            print(f"The following error occurred:", e)
    return connection

# Set Description based on Amount and MainDesc
def set_description(row):
    if row['Amount'] > 0:
        return 'Revenue'
    elif row['Amount'] < 0:
        return 'Expenses'
    elif 'FRIDGETNP' in row['MainDesc']:
        return 'Suppliers'
    else:
        return 'Unknown'


if __name__ == '__main__':
    parser = configparser.ConfigParser()
    # Read the configuration file
    parser.read('config.ini')
    excel_file = parser['development']['excel_file_path']
    host = parser['development']['host']
    database_name = parser['development']['database_name']
    user = parser['development']['user']
    password = parser['development']['password']
    table_name = parser['development']['table_name']

    # Load data from Excel.
    try:
        df = pd.read_excel(excel_file)
    except FileNotFoundError:
        print("Excel file not found:", excel_file)
        exit()

    # Fill Description column based on Amount and MainDesc
    df['Description'] = df.apply(set_description, axis=1)

    # Establish connection to MySQL database
    connection = create_connection(database_name, host, user, password)

    if connection is not None:
        with connection:
            df.to_sql(name=table_name, con=connection, if_exists='append', index=False)
    else:
        print("Unable to establish connection to MySQL")

