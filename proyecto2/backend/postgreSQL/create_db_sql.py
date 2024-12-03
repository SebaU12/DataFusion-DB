import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
#from postgreSQL.db_config import DB_CONFIG
from db_config import DB_CONFIG
import pandas as pd

def connect_db():
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        print("Conexión exitosa.")
        return connection
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None
def create_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS wines (
        id SERIAL PRIMARY KEY,
        country VARCHAR,
        description TEXT,
        designation VARCHAR,
        points INTEGER,
        price NUMERIC,
        province VARCHAR,
        region_1 VARCHAR,
        region_2 VARCHAR,
        taster_name VARCHAR,
        taster_twitter_handle VARCHAR,
        title VARCHAR,
        variety VARCHAR,
        winery VARCHAR,
        text TEXT,
        tokens TEXT,
        filtered_tokens TEXT,
        stemmed_tokens TEXT
    );
    """
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_query)
        connection.commit()
        print("Tabla creada exitosamente.")
    except Exception as e:
        print(f"Error al crear la tabla: {e}")
    finally:
        cursor.close()



def load_csv(connection, file_path, max_rows, new_delimiter = '@'):
    try:
        df = pd.read_csv(file_path, sep=',')
        df = df.head(max_rows)
        
        temp_file_path = '/Users/smdp/Documents/PERSONAL/DB2/DataFusion-DB/proyecto2/backend/postgreSQL/temp_file.csv'
        df.to_csv(temp_file_path, index=False, sep=new_delimiter)
        
        copy_query = sql.SQL("""
            COPY wines (id, country, description, designation, points, price, province, 
                      region_1, region_2, taster_name, taster_twitter_handle, title, variety, 
                      winery, text, tokens, filtered_tokens, stemmed_tokens)
            FROM {}
            DELIMITER {}
            CSV HEADER
        """).format(sql.Literal(temp_file_path), sql.Literal(new_delimiter))
        
        cursor = connection.cursor()
        cursor.execute(copy_query)
        connection.commit()
        
        print(f"Datos cargados exitosamente desde {temp_file_path}.") 
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        connection.rollback()
    
    finally:
        cursor.close()



def create_extensions(connection):
    try:
        cursor = connection.cursor()
        
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")
        
        connection.commit()
        print("Extensiones creadas exitosamente.")
    
    except Exception as e:
        print(f"Error al crear extensiones: {e}")
        connection.rollback()
    
    finally:
        cursor.close()

def create_tsvector_column(connection):
    try:
        cursor = connection.cursor()
        
        cursor.execute("""
            ALTER TABLE wines ADD COLUMN IF NOT EXISTS tsvector_col tsvector;
        """)
        
        cursor.execute("""
            UPDATE wines SET tsvector_col = to_tsvector('english', unaccent(text));
        """)
        
        connection.commit()
        print("Columna tsvector actualizada exitosamente.")
    
    except Exception as e:
        print(f"Error al crear y actualizar la columna tsvector: {e}")
        connection.rollback()
    
    finally:
        cursor.close()

def create_gin_index(connection):
    try:
        cursor = connection.cursor()
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tsvector ON wines USING GIN(tsvector_col);
        """)
        
        connection.commit()
        print("Índice GIN creado exitosamente.")
    
    except Exception as e:
        print(f"Error al crear el índice GIN: {e}")
        connection.rollback()
    
    finally:
        cursor.close()

def search_with_similarity(connection, search_terms, k):
    """Realizar consulta con similitud de coseno en la columna tsvector para varios términos."""
    try:
        cursor = connection.cursor()
        
        # Unir los términos de búsqueda con un operador lógico (AND o OR)
        # Suponiendo que quieres hacer una búsqueda de términos con "AND"
        search_query = ' | '.join([f"'{term}'" for term in search_terms])
        
        # Crear la consulta SQL con los términos de búsqueda concatenados
        query = sql.SQL("""
            SELECT id, title, ts_rank_cd(tsvector_col, query) AS rank
            FROM wines, to_tsquery('english', {search_query}) AS query
            WHERE tsvector_col @@ query
            ORDER BY rank DESC
            LIMIT {k};
        """).format(
            search_query=sql.Literal(search_query),
            k=sql.Literal(k)
        )
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            return results
        else:
            print("No se encontraron resultados.")
            return []
    
    except Exception as e:
        print(f"Error al realizar la búsqueda: {e}")
    
    finally:
        cursor.close()

# TODOs ESTO ES MAIN 



connection = connect_db()
#create_table(connection)
#load_csv(connection, "/Users/smdp/Documents/PERSONAL/DB2/DataFusion-DB/proyecto2/backend/dataset/preprocess_data.csv", 20)


#create_extensions(connection)

#create_tsvector_column(connection)

#create_gin_index(connection)
search_terms = ['underscor', 'snappi', 'of', 'snappi', 'underscor', 'underscor', 'acidity']
print(search_with_similarity(connection, search_terms, 2))

# Cerrar la conexión
#connection.close()