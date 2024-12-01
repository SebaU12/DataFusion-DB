import timm
from PIL import Image
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform
import torch
from sklearn.decomposition import PCA
from rtree import index
import joblib
import os
import pickle


class KnnRtreeIndex:
    def __init__(self, pca_model_path='pca_model.pkl', image_data_file='image_data.bin', n_components=2):
        """Inicializa el índice R-tree, el modelo PCA y el modelo de red neuronal."""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.initialize_model()
        self.pca_model = self.load_pca_model(pca_model_path)
        self.rtree_index = self.initialize_rtree()
        
        self.image_data_file = image_data_file
        self.image_data = self.load_image_data()  
        self.next_id = self.get_next_id()  

    def initialize_model(self):
        """Inicializa el modelo preentrenado y lo coloca en el dispositivo especificado."""
        model = timm.create_model('inception_v3', pretrained=True, num_classes=0)
        model = model.to(self.device)
        model.eval()
        return model

    def load_pca_model(self, filename):
        """Carga el modelo PCA preentrenado desde un archivo."""
        pca_model = joblib.load(filename)
        print(f"PCA cargado desde {filename}")
        return pca_model

    def initialize_rtree(self):
        """Inicializa un índice R-tree vacío."""
        return index.Index()

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

    def reduce_dimensions_with_pca(self, feature_vector):
        """Reduce la dimensionalidad de un vector de características usando PCA."""
        reduced_vector = self.pca_model.transform([feature_vector])[0]
        return reduced_vector

    def insert_image(self, image_path):
        """Inserta una imagen y su vector reducido en el índice R-tree."""
        image_id = self.next_id
        self.next_id += 1  # Incrementar el ID para la siguiente imagen
        
        feature_vector = self.extract_feature_vector(image_path)
        reduced_vector = self.reduce_dimensions_with_pca(feature_vector)
        
        # Guardar la ruta de la imagen
        self.image_data[image_id] = image_path
        
        # Insertar el vector reducido en el índice R-tree
        self.insert_to_rtree(reduced_vector, image_id)
        
        self.save_image_data()

    def insert_to_rtree(self, reduced_vector, image_id):
        """Inserta un vector reducido en el índice R-tree con un ID único."""
        if len(reduced_vector) == 2:
            x, y = reduced_vector
            bounding_box = (x, y, x, y)  
        else:
            raise ValueError("La dimensionalidad del vector no es compatible con R-tree.")
        
        self.rtree_index.insert(image_id, bounding_box)

    def search_similar_images(self, query_image_path, k=5):
        """Devuelve las k imágenes más similares a la imagen de consulta."""
        query_feature_vector = self.extract_feature_vector(query_image_path)
        query_reduced_vector = self.reduce_dimensions_with_pca(query_feature_vector)
        
        # Buscar las imágenes más cercanas en el índice R-tree
        nearest_images = list(self.rtree_index.nearest(query_reduced_vector, k))

        # Devolver las rutas de las imágenes más similares
        similar_images = [self.image_data[image_id] for image_id in nearest_images]
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
    knn_index = KnnRtreeIndex(pca_model_path='pca_models/pca_model_2c.pkl')

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


 

