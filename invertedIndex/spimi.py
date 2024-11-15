import os
import math
import copy
import pickle 
import sys 

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(os.path.realpath(THIS_DIR))

MAX_MEMORY_MB = 1  
MAX_MEMORY_BYTES = MAX_MEMORY_MB * 1024   # * 1024 Convertir a bytes


class SPIMIInvert:
    def __init__(self, token_stream):
        self.token_stream = token_stream

        self.output_directory = "INDEX"
        self.output_directory = "/".join([ROOT_DIR, self.output_directory])

        self.block_prefix = "index"
        self.block_number = 0
        self.block_suffix = ".dat"

        self.output_index = "index_master"
        self.output_index = "/".join([ROOT_DIR, self.output_index + self.block_suffix])

        self.norm_docs  = "norm_docs"
        self.norm_docs = "/".join([ROOT_DIR, self.norm_docs + self.block_suffix])

        self.N = 0
        self.documentos = {}
        self.mkdirOutputDirectory(self.output_directory)

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

    def construct_index(self): #Se debe escribir por bloques (terminos) en el archivo
        block_files = []
        dictionary = {}
        for token in self.token_stream:
            current_memory = sys.getsizeof(dictionary)
            if(current_memory >= MAX_MEMORY_BYTES/5):
                self.block_number += 1
                terms = self.sortTerms(dictionary)

                block_file = "/".join([self.output_directory, "".join([self.block_prefix, str(self.block_number), self.block_suffix])])
                block_files.append([self.writeBlockToDisk(terms, dictionary, block_file), True])

                dictionary = {}

                self.addToDictionary(dictionary, token[0])
                self.addToPostingsList(dictionary, token[0], (token[1], token[2], token[3]))
            else:
                if token[0] not in dictionary:
                    self.addToDictionary(dictionary, token[0]) 
                if token[1] not in self.documentos:
                    self.documentos[token[1]] = 0
                    
                self.addToPostingsList(dictionary, token[0], (token[1], token[2], token[3]))

        self.block_number += 1
        terms = self.sortTerms(dictionary)
        block_file = "/".join([self.output_directory, "".join([self.block_prefix, str(self.block_number), self.block_suffix])])

        block_files.append([self.writeBlockToDisk(terms, dictionary, block_file), True])

        self.N = len(self.documentos)

        for file in block_files:
            print(self.readBlockToDict(file[0]))
            print()

        return self.mergeBlocks(block_files, 0)

    @staticmethod
    def mergePostingLists(posting_list1, posting_list2):
        merged_posting_list = {}

        for doc_id, doc_info in posting_list1.items():
            merged_posting_list[doc_id] = doc_info

        for doc_id, doc_info in posting_list2.items():
                merged_posting_list[doc_id] = doc_info
                
        return merged_posting_list

    @staticmethod
    def getPosicion(n, lista, tipo):  # Lista = [ p, x, q, y]
        if tipo == "P":
            index_val = 1;index_let = 0
        else:
            index_val = 3;index_let = 2

        if lista[index_val] + 1 < n:
            lista[index_val] += 1
        else:
            lista[index_val] = 0
            lista[index_let] = lista[index_let] + n + 1

        posicion = lista[index_let] + lista[index_val]
        return posicion  # P o Q


    def mergeBlocks(self, block_files, merge_size):
        if os.path.exists(self.output_index):
            print("El archivo o directorio existe")
            return self.get_index() 

        n = pow(2,merge_size)
        print("Vuelta",n)

        if(len(block_files)/n < 1):
            print("FIN")
            return #self.construct_indexF(block_files)

        init_values = [0,0,n,0]

        P = 0;Q = n; Qprev = n; Qf = Q

        cant_blocks = len(block_files)

        input1 = self.readBlockToDict(block_files[P][0])
        input2 = self.readBlockToDict(block_files[Q][0])
        output = {}

        terms1 = iter(input1)
        terms2 = iter(input2)

        term1 = next(terms1, None)
        term2 = next(terms2, None)
        
        write_file = block_files[P][0]
        new_block_list = []
        current_Q = block_files[P][0]
        current_P = block_files[Q][0]
        while P <cant_blocks:
            #print("El bloque P (term1)", block_files[P], "El bloque Q (term2)", block_files[Q])
            print("Se procesa termino 1:", term1, " con termino 2: ", term2)

            if(term1 is not None and term2 is not None):
                if(term1 == term2 ):
                    merged_posting_list = self.mergePostingLists(input1[term1]["posting_list"], input2[term2]["posting_list"])
                    output[term1] = {
                        "df": input1[term1]["df"] + input2[term2]["df"],
                        "posting_list": merged_posting_list
                    }
                    term1 = next(terms1, None)
                    term2 = next(terms2, None)
                elif(term1 < term2):
                    output[term1] = input1[term1]
                    term1 = next(terms1, None)
                elif(term1 > term2):
                    output[term2] = input2[term2]
                    term2 = next(terms2, None)
            if(term1 is not None and term2 is None):
                output[term1] = input1[term1]
                term1 = next(terms1, None)
            if(term2 is not None and term1 is None):
                output[term2] = input2[term2]
                term2 = next(terms2, None)

            #Verificar que si al menos un term1 o term2 es none, entonces, se pase al siguiente P, Q
            if(term1 is None ):
                #Actualizar P
                P = self.getPosicion(n, init_values, "P") 
                if(P>=cant_blocks): break
                input1 = self.readBlockToDict(block_files[P][0])
                terms1 = iter(input1)
                term1 = next(terms1, None)
                write_file = block_files[P][0]

            if(term2 is None):
                #Actualizar Q
                Qnext = self.getPosicion(n, init_values, "Q") 
                #print("Q: ", Q)
                if(Qnext < cant_blocks): 
                    Q = Qnext; 
                    input2 = self.readBlockToDict(block_files[Q][0])
                    terms2 = iter(input2)
                term2 = next(terms2, None)    
                write_file = block_files[Q][0] 
            
            #Escribir el output 
            current_memory = sys.getsizeof(output)

            if(current_memory >= MAX_MEMORY_BYTES/5):
                print("ESCRIBIR EN ARHCIVO: ", write_file)
                print(output)
                terms = self.sortTerms(output)
                self.writeBlockToDisk(terms, output, write_file)

                new_block_list.append(write_file)

                if(write_file == block_files[P][0]): write_file = block_files[Q][0]
                else: write_file = block_files[P][0]

                output = {}

    
        print(output)            
        if output:
            terms = self.sortTerms(output)
            self.writeBlockToDisk(terms, output, write_file)
            new_block_list.append(write_file)

        print(new_block_list)
        '''print(block_files)

        for file in block_files:
            print(self.readBlockToDict(file[0]))
            print()'''
        return 1#self.mergeBlocks(block_files,merge_size+1)










    '''def mergeBlocks(self, block_files, merge_size):  #10, 2
        if os.path.exists(self.output_index):
            print("El archivo o directorio existe")
            return self.get_index()

        n = pow(2,merge_size)

        print("Vuelta",n)

        if(len(block_files)/n < 1):
            return self.construct_indexF(block_files)

        p =0; q = n; x = 0; y = 0
        cont = 2

        P = p + x
        Q = q + y 
        new_block_files = []
        while(Q < len(block_files) or P < len(block_files)):
            if(Q >= len(block_files)):
                new_block_files.append(block_files[P])
                print("Se agregó: ", block_files[P])
                if(x+1 < n): x += 1 #x = 1,2,3
                else: x = 0; p = cont*n; cont +=1 # x = 0, p = 8
                P = p + x #0 1 2 3 8

            else:
                #Validar que el archivo esté activo 
                print("Fusiona: ", P, " con ", Q)
                if(block_files[P][1] == True and block_files[Q][1] == True):
                    eliminar = self.mergeTwoIndex(block_files[P][0], block_files[Q][0])
                    if(eliminar==False):  block_files[Q][1] = False #pos_block_delete.append(Q)
                new_block_files.append(block_files[P])
                print("Se agregó: ", block_files[P])
                new_block_files.append(block_files[Q])
                print("Se agregó: ", block_files[Q])
                if(x+1 < n): x += 1 #x = 1,2,3
                else: x = 0; p = cont*n; cont +=1 # x = 0, p = 8

                if(y+1 < n): y += 1 #y = 1,2
                else: y = 0; q = cont*n; cont +=1 # y = 0, q = 12 pero 12 no existe

                P = p + x #0 1 2 3 8
                Q = q+y
        
        for element in block_files:
            if element not in new_block_files:
                new_block_files.append(element)
        
        print(new_block_files)  
    

        return self.mergeBlocks(new_block_files, merge_size + 1)  '''  

    '''def mergeTwoIndex(self, block_fileP, block_fileQ):
        input1 = self.readBlockToDict(block_fileP)
        input2 = self.readBlockToDict(block_fileQ)
        output = {}
        current_block_file = block_fileP

        terms1 = iter(input1)
        terms2 = iter(input2)

        term1 = next(terms1, None)
        term2 = next(terms2, None)

        block1_complete = False
        while term1 is not None or term2 is not None:
            if(term1 is not None and term2 is not None):
                if(term1 == term2 ):
                    merged_posting_list = self.mergePostingLists(input1[term1]["posting_list"], input2[term2]["posting_list"])
                    output[term1] = {
                        "df": input1[term1]["df"] + input2[term2]["df"],
                        "posting_list": merged_posting_list
                    }
                    term1 = next(terms1, None)
                    term2 = next(terms2, None)
                elif(term1 < term2):
                    output[term1] = input1[term1]
                    term1 = next(terms1, None)

                elif(term1 > term2):
                    output[term2] = input2[term2]
                    term2 = next(terms2, None)

            elif(term1 is not None and term2 is None):
                output[term1] = input1[term1]
                term1 = next(terms1, None)
            elif(term2 is not None and term1 is None):
                output[term2] = input2[term2]
                term2 = next(terms2, None)   

            current_memory = sys.getsizeof(output)
            if current_memory > MAX_MEMORY_BYTES/5:
                terms = self.sortTerms(output)
                self.writeBlockToDisk(terms, output, current_block_file)
                output = {} 
                current_block_file = block_fileQ
                block1_complete = True
            
        if output:
            terms = self.sortTerms(output)
            self.writeBlockToDisk(terms, output, current_block_file)

        return block1_complete  '''  

    def construct_indexF(self, block_files):
        #Limpiar block_files
        '''for file in block_files:
            if file[1] == False:
                os.remove(file[0])
        block_files = [file for file in block_files if file[1] != False]'''

        

        print(block_files)  
        print("DICCIONARIO FINAL")
        for file in block_files:
            print(self.readBlockToDict(file[0]))
            print()

        #Actualizar los tf_idf para cada documento por término
        #Construir el archivo norm
        #construir el archivo offset
        return 1
