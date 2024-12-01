import os
import torch
import timm
from PIL import Image
import numpy as np
import pandas as pd
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform

class KnnSequential:
    def __init__(self, data_file='knn_sequential_data.csv'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.initialize_model()
        self.data_file = data_file
        self.save_dir = 'saved_data'

        if os.path.exists(data_file):
            self.df_features = pd.read_csv(data_file, index_col=0)
        else:
            self.df_features = pd.DataFrame()  

    def initialize_model(self):
        """Inicializa el modelo preentrenado y lo coloca en el dispositivo especificado."""
        model = timm.create_model('inception_v3', pretrained=True, num_classes=0)
        model = model.to(self.device)
        model.eval()
        return model

    def load_and_transform_image(self, image_path):
        """Carga una imagen y la transforma según la configuración del modelo."""
        config = resolve_data_config({}, model=self.model)
        transform = create_transform(**config)
        img = Image.open(image_path).convert('RGB')
        tensor = transform(img).unsqueeze(0).to(self.device)
        return tensor

    def extract_features(self, image_path):
        """Extrae el vector característico de una imagen."""
        image_tensor = self.load_and_transform_image(image_path)
        with torch.no_grad():
            feature_vector = self.model(image_tensor)
        return feature_vector

    def normalize_feature_vector(self, feature_vector):
        """Normaliza el vector característico utilizando la normalización L2."""
        return feature_vector / feature_vector.norm(p=2, dim=1, keepdim=True)

    def calculate_distance(self, vector1, vector2):
        """Calcula la distancia Euclidiana entre dos vectores."""
        return np.linalg.norm(vector1 - vector2)

    def knn_search(self, query_vector, k):
        """Busca los k vecinos más cercanos."""
        distances = []
        for index, row in self.df_features.iterrows():
            stored_vector = row.values
            distance = self.calculate_distance(query_vector, stored_vector)
            distances.append((index, distance))
        distances.sort(key=lambda x: x[1])
        return [distances[i][0] for i in range(k)]

    def range_search(self, query_vector, radius):
        """Busca imágenes dentro de un radio dado."""
        return [
            index for index, row in self.df_features.iterrows()
            if self.calculate_distance(query_vector, row.values) <= radius
        ]

    def insert_image(self, image_path):
        """Procesa una imagen individual y la agrega al DataFrame."""
        feature_vector = self.extract_features(image_path)
        normalized_vector = self.normalize_feature_vector(feature_vector)
        feature_vector_np = normalized_vector.cpu().numpy().flatten()

        new_entry = pd.DataFrame([feature_vector_np], index=[image_path])
        self.df_features = pd.concat([self.df_features, new_entry])

    def save_data(self):
        """Guarda el DataFrame de características en un archivo persistente en la ruta 'save_data'."""
        # Crear la carpeta save_data si no existe
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
        # Guardar el archivo en la ruta 'save_data/data_file'
        self.df_features.to_csv(f"{self.save_dir}/{self.data_file}")

    def run_knn_search(self, query_image_path, k):
        """Ejecuta la búsqueda KNN."""
        query_vector = self.extract_features(query_image_path)
        query_vector = self.normalize_feature_vector(query_vector).cpu().numpy().flatten()
        closest_images = self.knn_search(query_vector, k)
        print(f"Las {k} imágenes más cercanas son:")
        for img_path in closest_images:
            print(img_path)

    def run_range_search(self, query_image_path, radius):
        """Ejecuta la búsqueda por rango."""
        query_vector = self.extract_features(query_image_path)
        query_vector = self.normalize_feature_vector(query_vector).cpu().numpy().flatten()
        matching_images = self.range_search(query_vector, radius)
        print(f"Las imágenes dentro del radio ({radius}) son:")
        for img_path in matching_images:
            print(img_path)

if __name__ == "__main__":
    image_dir = "test_images"

    knn_insert = KnnSequential(data_file="knn_sequential_data.csv")

    for image_name in os.listdir(image_dir):
        image_path = os.path.join(image_dir, image_name)
        if os.path.isfile(image_path):
            knn_insert.insert_image(image_path)

    knn_insert.save_data()

    query_image_path = "test.png"
    knn_search = KnnSequential(data_file="knn_sequential_data.csv")

    knn_search.run_knn_search(query_image_path, k=5)

    knn_search.run_range_search(query_image_path, radius=100)

