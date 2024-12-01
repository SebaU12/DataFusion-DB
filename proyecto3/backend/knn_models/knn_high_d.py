import timm
from PIL import Image
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform
import torch
import faiss
import os
import pickle
import numpy as np


class KnnHighD:
    def __init__(self, image_data_file='image_data.bin'):
        """Inicializa el modelo de Faiss, el modelo de red neuronal y los datos de imágenes."""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.initialize_model()
        self.image_data_file = image_data_file
        self.image_data = self.load_image_data()  
        self.next_id = self.get_next_id()  
        
        self.index = self.initialize_faiss_index()

        self.index_to_id = {}

    def initialize_model(self):
        """Inicializa el modelo preentrenado y lo coloca en el dispositivo especificado."""
        model = timm.create_model('inception_v3', pretrained=True, num_classes=0)
        model = model.to(self.device)
        model.eval()
        return model

    def initialize_faiss_index(self):
        """Inicializa un índice de Faiss para búsqueda de KNN."""
        dimension = 2048
        index = faiss.IndexFlatL2(dimension)  
        return index

    def load_and_transform_image(self, image_path):
        """Carga una imagen y la transforma según la configuración del modelo."""
        config = resolve_data_config({}, model=self.model)
        transform = create_transform(**config)
        
        img = Image.open(image_path).convert('RGB')
        tensor = transform(img).unsqueeze(0).to(self.device)
        return tensor

    def extract_feature_vector(self, image_path):
        """Extrae el vector característico de una imagen."""
        tensor = self.load_and_transform_image(image_path)
        with torch.no_grad():
            features = self.model(tensor)
        return features.squeeze().cpu().numpy()

    def insert_image(self, image_path):
        """Inserta una imagen y su vector en el índice Faiss."""
        image_id = self.next_id
        self.next_id += 1  
        
        feature_vector = self.extract_feature_vector(image_path)
        
        # Guardar la ruta de la imagen
        self.image_data[image_id] = image_path
        
        # Insertar el vector en el índice Faiss
        faiss_index = self.index.ntotal  
        self.index.add(np.expand_dims(feature_vector, axis=0).astype(np.float32))
        
        # Mapear el índice de Faiss con el ID de la imagen
        self.index_to_id[faiss_index] = image_id
        
        self.save_image_data()

    def search_similar_images(self, query_image_path, k=5):
        """Devuelve las k imágenes más similares a la imagen de consulta utilizando Faiss."""
        query_feature_vector = self.extract_feature_vector(query_image_path)
        
        distances, indices = self.index.search(np.expand_dims(query_feature_vector, axis=0).astype(np.float32), k)
        
        similar_images = [self.image_data[self.index_to_id[idx]] for idx in indices[0]]
        return similar_images

    def load_image_data(self):
        """Carga el diccionario de imágenes desde un archivo binario."""
        if os.path.exists(self.image_data_file):
            with open(self.image_data_file, 'rb') as file:
                return pickle.load(file)
        else:
            return {}

    def save_image_data(self):
        """Guarda el diccionario de imágenes en un archivo binario."""
        with open(self.image_data_file, 'wb') as file:
            pickle.dump(self.image_data, file)

    def get_next_id(self):
        """Obtiene el siguiente ID disponible para las imágenes."""
        return max(self.image_data.keys(), default=0) + 1



def main():
    image_dir = "test_images"
    knn_index = KnnHighD()

    for image_name in os.listdir(image_dir):
        image_path = os.path.join(image_dir, image_name)
        if os.path.isfile(image_path):
            knn_index.insert_image(image_path)
    
    query_image_path = "test.png" 
    similar_images = knn_index.search_similar_images(query_image_path, k=3)  

    print(f"Las imágenes más similares a {query_image_path}:")
    for img in similar_images:
        print(img)

if __name__ == "__main__":
    main()

