def ejecutar_sql (nombre_archivo, cur):
    sql_file=open(nombre_archivo)
    sql_as_string=sql_file.read()
    sql_file.close
    cur.executescript(sql_as_string)

def year(db):
    db['year'] = db['title'].str.extract(r'\((\d{4})\)').astype(int)
    db['title'] = db['title'].str.replace(r'\(\d{4}\)', '', regex=True).str.strip()
    
    return db 
