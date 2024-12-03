import pickle
from spimiIF import SPIMIInvert
from query import Query
import time


index = SPIMIInvert('/Users/smdp/Documents/PERSONAL/DB2/DataFusion-DB/proyecto2/backend/dataset/preprocess_data.csv') #Cambiar por el csv file 

indice = index.readCSVB()

#print(indice)

#print("INDICE: ", indice)
#print()
query = Query(indice, "/Users/smdp/Documents/PERSONAL/DB2/DataFusion-DB/proyecto2/backend/INDEX/norm.dat", 8, "/Users/smdp/Documents/PERSONAL/DB2/DataFusion-DB/proyecto2/backend/dataset/preprocess_data.csv")
print(query.execute("tropical fruit broom brimstone and dried herb"))
#print(query.execute("tannins tannins acidity"))
#print(query.execute("tannis"))

