import psycopg2

try:
    #conn=psycopg2.connect("dbname='myDB' user='postgres' host='localhost' password='yusufalppAAAASSSS1'")
    conn = psycopg2.connect("postgres://zdnxlrcciefcyt:cf311822d376530a9305b321a38b2cf7bd73ed254158dc3bcb10b55c1baf4e46@ec2-54-170-123-247.eu-west-1.compute.amazonaws.com:5432/dl2mqgtrp3lgj",sslmode="require")
except:
    print ("I am unable to connect to the database.")
    
cur = conn.cursor()
try:
    cur.execute("""
    CREATE TABLE if not exists users (
        id serial, 
        username VARCHAR NOT NULL UNIQUE, 
        password VARCHAR NOT NULL,
        name VARCHAR NOT NULL, 
        surname VARCHAR NOT NULL,
        registration_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id));
    
    CREATE TABLE if not exists privilege (
        id serial,
        privelege_type BOOL NOT NULL, 
        PRIMARY KEY (id),
        FOREIGN KEY (id) REFERENCES users(id));

    CREATE TABLE if not exists admin (
        id INT NOT NULL,
        expertise VARCHAR NOT NULL, 
        company VARCHAR NOT NULL, 
        PRIMARY KEY (id),
        FOREIGN KEY (id) REFERENCES users(id));

    CREATE TABLE if not exists regular (
        id INT NOT NULL,
        subject_of_interest VARCHAR NOT NULL, 
        job VARCHAR NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY (id) REFERENCES users(id));

    CREATE TABLE if not exists entry (
        entry_id serial, 
        id INT NOT NULL,
        title VARCHAR NOT NULL, 
        text TEXT NOT NULL,
        time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        email VARCHAR NOT NULL,
        phone VARCHAR NOT NULL,
        PRIMARY KEY (entry_id),
        FOREIGN KEY (id) REFERENCES users(id));
    
    CREATE TABLE if not exists complaint (
        entry_id INT NOT NULL, 
        status VARCHAR NOT NULL, 
        category VARCHAR NOT NULL,
        PRIMARY KEY (entry_id),
        FOREIGN KEY (entry_id) REFERENCES entry(entry_id));

    CREATE TABLE if not exists reply (
        entry_id INT NOT NULL, 
        extra_points INT NOT NULL, 
        given_points INT NOT NULL, 
        complaint_id INT NOT NULL,
        PRIMARY KEY (entry_id),
        FOREIGN KEY (entry_id) REFERENCES entry(entry_id));

    CREATE TABLE if not exists regularranking (
        id INT NOT NULL,
        total_marked_answers INT NOT NULL DEFAULT 0, 
        entry_count INT NOT NULL DEFAULT 0, 
        total_given_points INT NOT NULL DEFAULT 0, 
        PRIMARY KEY (id),
        FOREIGN KEY (id) REFERENCES users(id));

    CREATE TABLE if not exists adminranking (
        id INT NOT NULL,
        total_points INT NOT NULL DEFAULT 0, 
        total_replies INT NOT NULL DEFAULT 0, 
        total_extra_points INT NOT NULL DEFAULT 0, 
        total_points_from_users INT NOT NULL DEFAULT 0,
        PRIMARY KEY (id),
        FOREIGN KEY (id) REFERENCES users(id));

    CREATE TABLE if not exists images (
        user_id INT, 
        img bytea,
        PRIMARY KEY (user_id));
    """)

    conn.commit()
except Exception as e:
    print(e)
    print ("I can't drop our test database!")



