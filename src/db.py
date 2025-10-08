import psycopg2
def connect_db():
    return psycopg2.connect(
        dbname="orders",
        user="admin",
        password="diakosmisi1!",
        host="db",
        port="5432"
    )