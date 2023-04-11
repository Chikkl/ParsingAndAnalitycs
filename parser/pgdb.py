import psycopg2
import os
import json


try:
    connection = True

    connection.autocommit = True
    
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT version();"
        )
        print(f"Server version: {cursor.fetchone()}")

    if os.path.exists("/home/chikoni/Документы/parser/all_vacaniec.json"):
        with open("/home/chikoni/Документы/parser/all_vacaniec.json", encoding='utf-8') as jsonFile:
            templates = json.load(jsonFile)
            dumpsJson = json.dumps(templates, indent=4)
            loadsJson = json.loads(dumpsJson)
        
    with connection.cursor() as cursor:
         cursor.execute(
             f"""CREATE TABLE IF NOT EXISTS `vacaniec`(
                 id VARCHAR(9) PRIMARY KEY,
                 name VARCHAR(60) NOT NULL,
                 premium boolean,
                 area VARCHAR(50),
                 salary INT,
                 address VARCHAR(50),
                 experience VARCHAR(50),
                 schedule VARCHAR(50),
                 published_at VARCHAR(50), 
                 url VARCHAR(150),
                 employer VARCHAR,

                 ;"""
         )
        
    #     # connection.commit()
    #     print("[INFO] Table created successfully")
        
    # insert data into a table
    # with connection.cursor() as cursor:
    #     cursor.execute(
    #         """INSERT INTO users (first_name, nick_name) VALUES
    #         ('Oleg', 'barracuda');"""
    #     )
        
    #     print("[INFO] Data was succefully inserted")
        
    # get data from a table
    # with connection.cursor() as cursor:
    #     cursor.execute(
    #         """SELECT nick_name FROM users WHERE first_name = 'Oleg';"""
    #     )
        
    #     print(cursor.fetchone())
        
    # delete a table
    # with connection.cursor() as cursor:
    #     cursor.execute(
    #         """DROP TABLE users;"""
    #     )
        
    #     print("[INFO] Table was deleted")
    
except Exception as _ex:
    print("[INFO] Error while working with PostgreSQL", _ex)
finally:
    if connection:
        # cursor.close()
        connection.close()
        print("[INFO] PostgreSQL connection closed")
