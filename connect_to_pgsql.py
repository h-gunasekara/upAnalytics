import psycopg2

#connect to db
con = psycopg2.connect(
            host = "localhost"
        ,   database = "upBank"
        ,   user = "postgres"
        ,   password = "hamish123"
        )

#cursor
cur = con.cursor()

# cur.execute("insert into transaction (transaction_id, created_at) values (%s, %s)", ('123', "2020-09-16"))


cur.execute("select * from transaction")

rows = cur.fetchall()

for r in rows:
    print("id {} name {}".format(r[1], r[2]))

#commit everything
con.commit()

#close the cursor
cur.close()

#close the connection
con.close()