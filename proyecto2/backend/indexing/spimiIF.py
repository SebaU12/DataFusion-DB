import os
import math
import copy
import pandas as pd
import ast
import pickle 
import sys 
from collections import OrderedDict

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(os.path.realpath(THIS_DIR))

MAX_MEMORY_KB = 10  
MAX_MEMORY_BYTES = MAX_MEMORY_KB * 1024 #Convertir a bytes



class SPIMIInvert:
    def __init__(self, csvFile):
        #self.token_stream = token_stream
        self.csvFile = csvFile
        self.csvCompleto = False

        self.output_directory = "INDEX"
        self.output_directory = "/".join([ROOT_DIR, self.output_directory])

        self.block_prefix = "index"
        self.block_number = 0
        self.block_suffix = ".dat"

        self.output_index = "main_index"
        self.output_index = "/".join([ROOT_DIR, self.output_index + self.block_suffix])

        self.norm_docs  = "norm_docs"
        self.norm_docs = "/".join([ROOT_DIR, self.norm_docs + self.block_suffix])

        self.N = 0
        self.documentos = {}
        self.block_files = []
        if not os.path.exists(self.output_directory):
            self.mkdirOutputDirectory(self.output_directory)
        else:
            if not os.path.exists(self.output_index): self.mkdirOutputDirectory(self.output_directory)

    @staticmethod
    def mkdirOutputDirectory(output_directory):
        try:
            os.mkdir(output_directory)
        except FileExistsError:
            for file in os.listdir(output_directory):
                os.unlink(os.path.join(output_directory, file))

    @staticmethod
    def addToDictionary(dictionary, term):
        dictionary[term] = {"df": 0, "idf": 0, "posting_list": {}}
        return dictionary[term]

    @staticmethod
    def addToPostingsList(dictionary, term, document_info):
        doc_id = document_info[0]
        tf = document_info[1]
        wtf = document_info[2]

        dictionary[term]["posting_list"][doc_id] = {"tf": tf, "wtf": wtf, "tf_idf": 0}
        dictionary[term]["df"] = dictionary[term]["df"] + 1
    
    @staticmethod
    def sortTerms(dictionary):
        return [term for term in sorted(dictionary)]

    @staticmethod
    def writeBlockToDisk(sorted_terms, dictionary, block_file):
        with open(block_file, 'wb') as file:
            for term in sorted_terms:
                data = {}
                data[term] = dictionary[term]
                pickle.dump(data, file)  
            
        return block_file        

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

    @staticmethod
    def log_frequency_weight(tf_td):
        if tf_td > 0: return round(1 + math.log10(tf_td),2)
        return 0

    def generate_tf_wtf_tuples(self, df, column_name='stemmed_tokens', start_doc_id=0):
        result = []
        
        for doc_id, document in enumerate(df[column_name], start=start_doc_id):
            words = ast.literal_eval(document)
            term_freq = pd.Series(words).value_counts()
            
            for term, tf in term_freq.items():
                wtf = self.log_frequency_weight(tf)
                result.append((term, doc_id, tf, wtf))
        return result

    def readCSVB(self):
        if os.path.exists(self.output_index): return self.get_index()
        chunk_size = 100  # Chunk
        max_lines = 64000 # NUMERO TOTAL
        total_processed = 0  # Líneas procesadas

        #all_results = []  
        for i, chunk in enumerate(pd.read_csv(self.csvFile, chunksize=chunk_size)):

            if total_processed >= max_lines: break
            
            print(f"Procesando chunk {i + 1}")
            
            remaining_lines = max_lines - total_processed
            if len(chunk) > remaining_lines: chunk = chunk.iloc[:remaining_lines]
            
            resultado = self.generate_tf_wtf_tuples(chunk, start_doc_id=total_processed)

            
            total_processed += len(chunk)
            if(total_processed == max_lines): self.csvCompleto = True

            #Crear bloques 
            self.token_stream = resultado

            self.construct_index()
            print(f"Líneas procesadas: {total_processed}")

        return self.main_index

    def construct_index(self): #Se debe escribir por bloques (terminos) en el archivo
        #print("TOKEN POR PROCESAR: ", self.token_stream)
        dictionary = {}
        for token in self.token_stream:
            current_memory = sys.getsizeof(dictionary)
            if(current_memory >= MAX_MEMORY_BYTES):
                self.block_number += 1
                terms = self.sortTerms(dictionary)

                block_file = "/".join([self.output_directory, "".join([self.block_prefix, str(self.block_number), self.block_suffix])])
                self.block_files.append(self.writeBlockToDisk(terms, dictionary, block_file))
                dictionary = {}

                self.addToDictionary(dictionary, token[0])
                self.addToPostingsList(dictionary, token[0], (token[1], token[2], token[3]))
            else:
                if token[0] not in dictionary:
                    self.addToDictionary(dictionary, token[0]) 
                if token[1] not in self.documentos:
                    self.documentos[token[1]] = 0
                    
                self.addToPostingsList(dictionary, token[0], (token[1], token[2], token[3]))
            
            
        if(dictionary): 
            self.block_number += 1
            terms = self.sortTerms(dictionary)
            block_file = "/".join([self.output_directory, "".join([self.block_prefix, str(self.block_number), self.block_suffix])])

            self.block_files.append(self.writeBlockToDisk(terms, dictionary, block_file))

        self.N = len(self.documentos)

        if(self.csvCompleto): self.mergeBlocks()

    @staticmethod
    def mergePostingLists(posting_list1, posting_list2):
        merged_posting_list = {}

        for doc_id, doc_info in posting_list1.items():
            merged_posting_list[doc_id] = doc_info

        for doc_id, doc_info in posting_list2.items():
                merged_posting_list[doc_id] = doc_info
                
        return merged_posting_list

    def merge2Blocks(self,block1, block2):
        merged_block = {}
        terms1 = iter(sorted(block1.keys()))
        terms2 = iter(sorted(block2.keys()))

        term1 = next(terms1, None)
        term2 = next(terms2, None)

        while term1 is not None or term2 is not None:
            if term1 is None:
                merged_block[term2] = block2[term2]
                term2 = next(terms2, None)
            elif term2 is None:
                merged_block[term1] = block1[term1]
                term1 = next(terms1, None)
            elif term1 == term2:
                merged_posting_list = self.mergePostingLists(
                    block1[term1]["posting_list"], block2[term2]["posting_list"]
                )
                merged_block[term1] = {
                    "df": block1[term1]["df"] + block2[term2]["df"],
                    "idf": 0,
                    "posting_list": merged_posting_list,
                }
                term1 = next(terms1, None)
                term2 = next(terms2, None)
            elif term1 < term2:
                merged_block[term1] = block1[term1]
                term1 = next(terms1, None)
            else:
                merged_block[term2] = block2[term2]
                term2 = next(terms2, None)

        return merged_block

            
    
    def mergeBlocks(self):
        #if os.path.exists(self.output_index): return self.get_index()
        blocks = []
        for block in self.block_files:
            blocks.append(self.readBlockToDict(block))

        #Fusionar 
        while len(blocks) > 1:
            merged_blocks = []
            for i in range(0, len(blocks), 2):
                if i + 1 < len(blocks):
                    merged = self.merge2Blocks(blocks[i], blocks[i + 1])
                    merged_blocks.append(merged)
                else:
                    merged_blocks.append(blocks[i])
            blocks = merged_blocks

        merged_result = blocks[0]

        index = OrderedDict(sorted(merged_result.items(), key=lambda x: x[0]))

        #Escribir en memoria secundaria 
        output = {}
        norm = {}
        init_word = next(iter(index)).lower(); i = 0; j = i

        self.main_index = {}
        for palabra, datos in index.items():
            if(j != i): init_word = palabra.lower();j = i

            #CALCULAR SU IDF 
            idf = round(math.log10(self.N/index[palabra]["df"]),2)
            datos["idf"] = idf
            

            #CALCULAR SU TF_IDF para cada documento 
            for document,stats in datos["posting_list"].items():
                stats['tf_idf'] = round(idf*stats['tf'],2)

                #CALCULAR LA NORMA DE CADA DOCUMENTO
                if(document not in norm): norm[document] = round(pow(stats['tf_idf'],2),2)
                else: norm[document] = round(norm[document] + pow(stats['tf_idf'],2),2)

            output[palabra] = datos

            current_memory = sys.getsizeof(output)

            if(current_memory >= MAX_MEMORY_BYTES):
                #print(output) #CORREGIR
                terms = self.sortTerms(output)
                self.writeBlockToDisk(terms, output, self.block_files[i])
                output = {}
                #Agregar al main index 
                if(init_word[0] not in self.main_index): 
                    self.main_index[init_word[0]] = {}
                    self.main_index[init_word[0]][palabra] = self.block_files[i]
                else:
                    self.main_index[init_word[0]][palabra] = self.block_files[i]
                i += 1

        terms = self.sortTerms(output)
        self.writeBlockToDisk(terms, output, self.block_files[i])
        

        #Agregar al main index 
        if(init_word[0] not in self.main_index): 
            self.main_index[init_word[0]] = {}
            self.main_index[init_word[0]][palabra] = self.block_files[i]
        else:
            self.main_index[init_word[0]][palabra] = self.block_files[i]
        i += 1

        for k in range(i, len(self.block_files)):
            try:
                os.remove(self.block_files[k])
            except FileNotFoundError:
                print(f"File {self.block_files[k]} not found.")
            
        del self.block_files[i:]  

        #Crear archivo main_index
        with open(self.output_index, 'wb') as file:
            pickle.dump(self.main_index, file)          

        #Crear el archivo norm 
        self.norm_file = "/".join([self.output_directory, "".join(["norm", self.block_suffix])])
        with open(self.norm_file, 'wb') as file:
            pickle.dump(norm, file)

        

    
    def get_index(self):
        try:
            with open(self.output_index, 'rb') as file:  
                data = pickle.load(file)  
            return data
        except FileNotFoundError:
            print("Archivo main_index no encontrado. Verifica la ruta.")
            return None
        except pickle.PickleError:
            print("Error al cargar el archivo main_index. Formato binario inválido.")
            return None
        except Exception as e:
            print(f"Error inesperado: {e}")
            return None


        