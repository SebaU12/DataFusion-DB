import os
import math
import json

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(os.path.realpath(THIS_DIR))

BLOCK_SIZE = 10 #Máximo un bloque puede tener 30 documentos

class SPIMIInvert:
    def __init__(self, token_stream):
        self.token_stream = token_stream

        self.output_directory = "INDEX"
        self.output_directory = "/".join([ROOT_DIR, self.output_directory])

        self.block_prefix = "BLOCK"
        self.block_number = 0
        self.block_suffix = ".json"

        self.output_index = "index"
        self.output_index = "/".join([ROOT_DIR, self.output_index + self.block_suffix])

        self.N = 0
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
        dictionary[term] = {"df":0, "posting_list":{}}
        return dictionary[term]

    @staticmethod
    def getPostingsList(dictionary, term):
        return dictionary[term]["posting_list"]    

    @staticmethod
    def addToPostingsList(dictionary, term, document_info):
        doc_id = document_info[0]
        tf = document_info[1]
        wtf = document_info[2]

        if doc_id not in dictionary[term]["posting_list"]:
            dictionary[term]["posting_list"][doc_id] = {"tf": tf, "wtf": wtf, "tf_idf": 0}
        else:
            # Si el documento ya existe, actualizar el tf y wtf
            dictionary[term]["posting_list"][doc_id]["tf"] += tf
            dictionary[term]["posting_list"][doc_id]["wtf"] += wtf
        
        dictionary[term]["df"] = dictionary[term]["df"] + 1

    @staticmethod
    def sortTerms(dictionary):
        return [term for term in sorted(dictionary)]
    
    @staticmethod
    def writeBlockToDisk(sorted_terms, dictionary, block_file):
        json_data = {}
        for term in sorted_terms:
            json_data[term] = dictionary[term]

        with open(block_file, 'w') as file:
            json.dump(json_data, file, indent=4)

        return block_file    

    def construct_pre_index(self):
        block_files = []
        documentos = set()
        for list_of_tokens in self.token_stream:

            dictionary = {}
            for token in list_of_tokens:
                if token[0] not in dictionary:
                    postings_list = self.addToDictionary(dictionary, token[0]) #term(token)
                else:
                    postings_list = self.getPostingsList(dictionary, token[0])

                self.addToPostingsList(dictionary, token[0], (token[1], token[2], token[3]))
                documentos.add(token[1])

            self.block_number += 1
            terms = self.sortTerms(dictionary)

            block_file = "/".join([self.output_directory, "".join([self.block_prefix, str(self.block_number), self.block_suffix])])
            block_files.append(self.writeBlockToDisk(terms, dictionary, block_file))

        self.N = len(documentos)
        #self.mergeBlocks(block_files, 0)
        return self.mergeBlocks(block_files, 0)

    @staticmethod
    def readBlockToDict(block_file):
        try:
            with open(block_file, 'r') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            print(f"Error: El archivo {block_file} no se encontró.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: El archivo {block_file} tiene un formato JSON inválido.")
            return {}

    @staticmethod
    def mergePostingLists(posting_list1, posting_list2):
        merged_posting_list = {}

        for doc_id, doc_info in posting_list1.items():
            merged_posting_list[doc_id] = doc_info

        for doc_id, doc_info in posting_list2.items():
                merged_posting_list[doc_id] = doc_info
                
        return merged_posting_list

    @staticmethod
    def getTotalPostingSize(output):
        return sum(len(posting["posting_list"]) for posting in output.values())

    def mergeTwoBlocks(self, block_fileP, block_fileQ):
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

            if self.getTotalPostingSize(output) > BLOCK_SIZE:
                terms = self.sortTerms(output)
                self.writeBlockToDisk(terms, output, current_block_file)
                output = {} 
                current_block_file = block_fileQ
                block1_complete = True
            
        
        if output:
            terms = self.sortTerms(output)
            self.writeBlockToDisk(terms, output, current_block_file)

        #if block1_complete == False:
            #os.remove(block_fileQ)

        return block1_complete

 

    def mergeBlocks(self, block_files, merge_size):  #10, 2
        n = pow(2,merge_size)
        print("Vuelta",n)
        if(len(block_files)/n < 1):
            return self.construct_index(block_files)

        p =0; q = n; x = 0; y = 0
        cont = 2

        P = p + x
        Q = q + y 

        pos_block_delete = []

        while(Q < len(block_files) and P < len(block_files)):
            print("Fusiona: ", P, " con ", Q)
            eliminar = self.mergeTwoBlocks(block_files[P], block_files[Q])
            if(eliminar==False): pos_block_delete.append(Q)

            if(x+1 < n): x += 1 #x = 1,2,3
            else: x = 0; p = cont*n; cont +=1 # x = 0, p = 8

            if(y+1 < n): y += 1 #y = 1,2
            else: y = 0; q = cont*n; cont +=1 # y = 0, q = 12 pero 12 no existe

            P = p + x #0 1 2 3 8
            Q = q+y
            
            #Q = q + y #4 5 6 7 12
            

        #Limpiar block_files
        pos_block_delete.sort(reverse=True)
        for i in pos_block_delete:
            os.remove(block_files[i])
            block_files.pop(i)
        print(block_files)    
        return self.mergeBlocks(block_files, merge_size + 1)    

    @staticmethod
    def create_bucket(bucket_file, posting_list):
        with open(bucket_file, 'w') as file:
            json.dump(posting_list, file, indent=4)
        return 

    def construct_index(self, blocks_file): 
        index = {}
        self.block_prefix = "BUCKET"
        self.block_number = 0
        self.block_suffix = ".json"

        n = 0
        while len(blocks_file)>0:
            data = self.readBlockToDict(blocks_file[0])
            #Compara con impar
            terms1 = iter(data)
            term1 = next(terms1, None)
            while term1 is not None:
                if(term1 not in index):
                    #Crear el bucket con todos los posting_list por defecto
                    bucket_name = "".join([self.block_prefix, str(self.block_number), self.block_suffix])
                    bucket_file = "/".join([self.output_directory, bucket_name])
                    self.create_bucket(bucket_file, data[term1]["posting_list"])

                    #Agregarlo al índice
                    index[term1] = {
                        "df": data[term1]["df"],
                        "idf": round(math.log10(self.N/data[term1]["df"]),2),
                        "list_buckets": [bucket_name]
                    }
                    self.block_number += 1
                    term1 = next(terms1, None)
                else:
                    term1 = next(terms1, None)
                    '''#Evaluar la creación de un bucket overflow o escribirlo en el bucket actual 
                    cant_buckets = len(index[term1]["list_buckets"]) 
                    df_a = index[term1]["df"]
                    last_bucket_size = BLOCK_SIZE -(cant_buckets*BLOCK_SIZE - df_a)

                    if( last_bucket_size < BLOCK_SIZE):

                        #Traer el último bucket
                        bucket_file = "/".join([self.output_directory, index[term1]["list_buckets"][cant_buckets-1]])
                        bucket =self.readBlockToDict(bucket_file)

                        i = 0
                        cont = 0
                        while()
                        for doc in data[term1]["posting_list"]:
                            terms1[doc] = data[term1]["posting_list"][doc]
                            i += 1

                            #Si se llega al límite, entonces crear un bucketOverflow


                        
                    else:
                        pass
                    pass  ''' 
                    
            #limpiar el bloque
            os.remove(blocks_file[0])
            blocks_file.pop(0)
            print(blocks_file)

        #construir indißce 
        self.create_bucket(self.output_index, index)
        print(self.N)
        return 1

    def get_index(self):
        #si no existe el archivo lo construye, en caso si exista lo regresa

        pass