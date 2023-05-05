import psycopg2

def create_tables(conn): # Функция, создающая структуру БД (таблицы)
    with conn.cursor() as cur:            
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            client_id SERIAL PRIMARY KEY,
            name_client VARCHAR (20) NOT NULL,
            surname_client VARCHAR (20) NOT NULL,
            email_client VARCHAR (20) UNIQUE NOT NULL);
            """)
            
        cur.execute("""
        CREATE TABLE IF NOT EXISTS phones(
            phone_id SERIAL PRIMARY KEY,
            phone_number INTEGER,
            client_id INTEGER REFERENCES clients(client_id));
            """)
        
    conn.commit()
    return
        
    
def add_client(conn, name, surname, email, phone=None): # Функция, позволяющая добавить нового клиента
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO clients (name_client, surname_client, email_client)
        VALUES (%s, %s, %s) 
        RETURNING client_id
        """, (name, surname, email))
        client_id = cur.fetchone()[0]

        cur.execute("""
        INSERT INTO phones (phone_number, client_id)
        VALUES (%s, %s)
        """, (phone, client_id))
    
    conn.commit()
    return
    
def add_phone(conn, client_id, phone): # Функция, позволяющая добавить телефон для существующего клиента
    with conn.cursor() as cur:            
        cur.execute("""
        INSERT INTO phones (phone_number, client_id)
        VALUES (%s, %s)
        """, (phone, client_id))

    conn.commit()
    return

def change_client(conn, client_id, name=None, surname=None, email=None, phone=None): # Функция, позволяющая изменить данные о клиенте
    with conn.cursor() as cur:            
        cur.execute("""
        UPDATE clients 
        SET name_client = %s, surname_client = %s, email_client = %s 
        WHERE client_id = %s""", (name, surname, email, client_id))

        cur.execute("""
        UPDATE phones 
        SET phone_number = %s 
        WHERE client_id = %s""", (phone, client_id))

    conn.commit()
    return
    
def delete_phone(conn, client_id, phone_number): # Функция, позволяющая удалить телефон для существующего клиента
    with conn.cursor() as cur:            
        cur.execute("""
        DELETE FROM phones
        WHERE client_id = %s AND phone_id IN (SELECT phone_id FROM phones p
        WHERE client_id = %s AND phone_number = %s)""", (client_id, client_id, phone_number))

    conn.commit()
    return

def delete_client(conn, client_id): # Функция, позволяющая удалить существующего клиента
    with conn.cursor() as cur:            
        cur.execute("""
        DELETE FROM phones
        WHERE client_id = %s""", (client_id, ))

        cur.execute("""
        DELETE FROM clients
        WHERE client_id = %s""", (client_id, ))

    conn.commit()
    return
    
def find_client(conn, name=None, surname=None, email=None, phone=None):
    # Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону
    with conn.cursor() as cur:
        query = ""
        params = []
        if name is not None:
            query += f"SELECT * FROM clients WHERE name_client = %s"
            params.append(name)
        if surname is not None:
            if query:
                query += " UNION "
            query += f"SELECT * FROM clients WHERE surname_client = %s"
            params.append(surname)
        if email is not None:
            if query:
                query += " UNION "
            query += f"SELECT * FROM clients WHERE email_client = %s"
            params.append(email)
        if phone is not None:
            if query:
                query += " UNION "
            query += f"SELECT * FROM phones INNER JOIN clients ON phones.client_id = clients.client_id WHERE phone_number = %s"
            params.append(phone)

        cur.execute(query, tuple(params))

        result = cur.fetchall()

    return result

with psycopg2.connect(database="clients", user="postgres", password="Fedor2001") as conn:
    create_tables(conn)
    add1 = add_client(conn, 'Rogi', 'Kuch', 'K@mai.ru', 55555555)
    add2 = add_client(conn, 'Ivan', 'Ivanov', 'I@mai.ru', 11111111)
    add3 = add_client(conn, 'John', 'Travolta', 'J@mai.ru', 77777777)
    add4 = add_client(conn, 'Jack', 'Daniels', 'JD@mai.ru', 33333333)
    add_ph = add_phone(conn, 1, 99999999)
    change1 = change_client(conn, 1, 'Igor', 'Chuk', 'ch@mai.ru', 88888888)
    delete_ph = delete_phone(conn, 1, 88888888)
    delete_cl = delete_client(conn, 2)
    find1 = find_client(conn, 'Igor')
    find2 = find_client(conn, 'Travolta')
    find3 = find_client(conn, '33333333')