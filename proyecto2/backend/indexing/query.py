import abc
import nltk
#nltk.download()
import pickle 
import numpy as np
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer


class Query:
    def __init__(self, index, length_file, K_vecinos, csv_file):
        self.K = K_vecinos
        self.csv_file = csv_file
        self.length_file = length_file
        self.index = index
        self.original_terms = ""
        self.terms = []
        self.most_recent_results = []
        self.terms_tf = []

    def ask_user(self, query):
        self.original_terms = query

    @staticmethod
    def readBlockToDict(block_file):
        try:
            all_data = {}
            with open(block_file, 'rb') as file:
                while True:
                    try:
                        entry = pickle.load(file)
                        for key in entry:
                            all_data[key] = entry[key]
                            
                    except EOFError:
                        break
            return all_data
        except FileNotFoundError:
            print(f"Error: El archivo {block_file} no se encontró.")
            return {}
        except  pickle.PickleError:
            print(f"Error: El archivo {block_file} tiene un formato binario inválido.")
            return {}

    def get_word_information(self, terms):

        self.original_terms = terms
        tokens = word_tokenize(terms, language="english")

        stop_words = set(stopwords.words("english")) 
        filtered_terms = [term for term in tokens if term.lower() not in stop_words]

        stemmer = SnowballStemmer("english")  

        for term in filtered_terms:
            stemmed_term = stemmer.stem(term)
            if stemmed_term in self.terms:
                index = self.terms.index(stemmed_term)
                self.terms_tf[index] += 1
            else:
                self.terms.append(stemmed_term)
                self.terms_tf.append(1)

        results = {} #Palabra con su posting list 

        for term in self.terms:

            next = False
            if(term[0] not in self.index): results[term] = []; continue
            else: datos = self.index[term[0]]

            for palabra,url in datos.items():
                if (term <= palabra):
                    #Leer el bloque
                    block = self.readBlockToDict(url)
                    #En el bloque obtener sus posting list 
                    try:
                        data = block[term]
                    except KeyError:
                        next = True

                    if(not next): results[term] = data
                    break


            if (next):

                claves = sorted(self.index.keys())  # Ordenar claves
                indice_actual = claves.index(term[0])

                letra_anterior = claves[indice_actual - 1] if indice_actual > 0 else None

        
                if letra_anterior:
                    try:
                        datos = self.index[letra_anterior]
                        encontrado = False
                        for palabra,url in datos.items():
                            if (term <= palabra):
                                block = self.readBlockToDict(url)
                                data = block[term]
                                results[term] = data
                                encontrado = True

                        if(not encontrado): results[term] = []
                    except Exception as e:  
                        print(f"Error: {e}")  
                        results[term] = []
                else:
                    results[term] = []

        return results

    def get_title_at_row(self, row_index, chunk_size=10):
        chunk_iter = pd.read_csv(self.csv_file, chunksize=chunk_size)
        
        chunk_number = row_index // chunk_size
        row_within_chunk = row_index % chunk_size
        
        for i, chunk in enumerate(chunk_iter):
            if i == chunk_number:
                return chunk.iloc[row_within_chunk]['title']
        return None


    def execute(self, terms):
        #LEER EL ARCHIVO NORM 
        with open(self.length_file, 'rb') as file:  
            data = pickle.load(file)

        scores = np.zeros(len(data))
        length = np.array([value for docId, value in data.items()])


        #Información total para cada término 
        word_information = self.get_word_information(terms)

        i = 0
        #Peso basado en la consulta FALTA COMPROBAR CUANDO ME DA VACIO
        for word,information  in word_information.items():
            if(information == []): continue
            #Peso para cada término de la query
            self.terms_tf[i] = self.terms_tf[i] * information["idf"]
            posting_list = information["posting_list"]

            for docId, info in posting_list.items():
                scores[docId]+= info["tf_idf"] * self.terms_tf[i]

            i += 1

        #NORMALIZAR SCORES
        scores = scores / length

        top_k_indices = np.argsort(scores)[-self.K:][::-1]
        top_k_scores = scores[top_k_indices] 

        top_k_dict = [(int(index), round(float(score), 4)) for index, score in zip(top_k_indices, top_k_scores)]
        

        result = []
        for docId, score in top_k_dict:
            if(score == 0): continue
            title = self.get_title_at_row(docId)
            result.append((docId, title, score))

        return result
        






      


