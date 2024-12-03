import pickle
from spimiIF import SPIMIInvert
from query import Query
import time


index = SPIMIInvert('/Users/smdp/Documents/PERSONAL/DB2/DataFusion-DB/proyecto2/backend/dataset/preprocess_data.csv') #Cambiar por el csv file 

indice = index.readCSVB()

#print(indice)

#print("INDICE: ", indice)
#print()
query = Query(indice, "/Users/smdp/Documents/PERSONAL/DB2/DataFusion-DB/proyecto2/backend/INDEX/norm.dat", 2, "/Users/smdp/Documents/PERSONAL/DB2/DataFusion-DB/proyecto2/backend/dataset/preprocess_data.csv")
#query.execute("underscor snappi of snappi underscor underscor acidity")
#query.execute("tannins tannins acidity")
start_time = time.time()
print(query.execute("tannis"))
end_time = time.time()

elapsed_time = end_time - start_time
print(f"Tiempo de ejecución: {elapsed_time:.4f} segundos")
