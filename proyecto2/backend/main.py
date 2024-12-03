from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import pickle
import nltk
from postgreSQL.create_db_sql import connect_db, search_with_similarity
from indexing.spimiIF import SPIMIInvert
from indexing.query import Query
import time

app = FastAPI()

class QueryRequest(BaseModel):
    database: str
    query: str
    K: int

csv_file = "/Users/smdp/Documents/PERSONAL/DB2/DataFusion-DB/proyecto2/backend/dataset/preprocess_data.csv"
norm_file ="/Users/smdp/Documents/PERSONAL/DB2/DataFusion-DB/proyecto2/backend/INDEX/norm.dat"

@app.post("/database/query")
async def insert_image_sequential(request: QueryRequest):
    if(request.database == "postgreSQL"):
        start_time = time.time()
        #Parsear 

        connection = connect_db()
        input_data = request.query.split()
        query_result = search_with_similarity(connection,set(input_data), request.K)
    
        connection.close()
        end_time = time.time()
        elapsed_time = end_time - start_time

        result = {"result": query_result, "time": elapsed_time}
        return result
    else:
        index = SPIMIInvert(csv_file)
        start_time = time.time()
        indice = index.readCSVB()
        query = Query(indice, norm_file, request.K, csv_file)
        query_result = query.execute(request.query)
        end_time = time.time()
        elapsed_time = end_time - start_time
        result = {"result": query_result, "time": elapsed_time}
        return result


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)