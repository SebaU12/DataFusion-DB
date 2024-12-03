import pickle
from spimiIF import SPIMIInvert
from query import Query


index = SPIMIInvert('/Users/smdp/Documents/PERSONAL/DB2/DataFusion-DB/proyecto2/backend/dataset/preprocess_data.csv') #Cambiar por el csv file 

indice = index.readCSVB()

#print(indice)

#print("INDICE: ", indice)
#print()
query = Query(indice, "/Users/smdp/Documents/PERSONAL/DB2/DataFusion-DB/proyecto2/backend/INDEX/norm.dat", 2, "/Users/smdp/Documents/PERSONAL/DB2/DataFusion-DB/proyecto2/backend/dataset/preprocess_data.csv")
#query.execute("underscor snappi of snappi underscor underscor acidity")
#query.execute("tannins tannins acidity")
query.execute("tannis")



#LEER EL ARCHIVO NORM 
