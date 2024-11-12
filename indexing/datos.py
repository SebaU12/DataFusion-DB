import pandas as pd
import ast
import math

# Función para calcular el peso de frecuencia logarítmica (wtf)
def log_frequency_weight(tf_td):
    if tf_td > 0:
        return 1 + math.log10(tf_td)
    return 0

# Función para generar una lista de tuplas con (term, docID, tf, wtf)
def generate_tf_wtf_tuples(df, column_name='stemmed_tokens', start_doc_id=0):
    result = []
    
    # Iterar sobre los documentos en el DataFrame
    for doc_id, document in enumerate(df[column_name], start=start_doc_id):
        words = ast.literal_eval(document)
        
        # Calcular frecuencia de términos (tf) 
        term_freq = pd.Series(words).value_counts()
        
        # Crear tuplas (term, docID, tf, wtf) 
        for term, tf in term_freq.items():
            wtf = log_frequency_weight(tf)
            result.append((term, doc_id, tf, wtf))
    
    return result


if __name__ == '__main__':
    path = "../dataset/preprocess_data.csv"
    df = pd.read_csv(path)
    resultado = generate_tf_wtf_tuples(df, start_doc_id=0)
    print(resultado[:5])  
