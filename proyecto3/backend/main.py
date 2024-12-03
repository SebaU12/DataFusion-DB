from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from knn_models.knn_sequential import KnnSequential
from knn_models.knn_rtree_index import KnnRtreeIndex  
from knn_models.knn_high_d import KnnHighD
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Inicialización de las clases
knn_sequential = KnnSequential(data_file="knn_sequential_data.csv")
knn_rtree = KnnRtreeIndex(pca_model_path='pca_models/pca_model_2c.pkl', image_data_file='saved_data/image_data_rtree.bin')
knn_high_d = KnnHighD(image_data_file='saved_data/image_data_faiss.bin')

# Modelo para búsqueda KNN
class KNNRequest(BaseModel):
    query_image_path: str
    k: int

# Modelo para búsqueda por rango
class RangeSearchRequest(BaseModel):
    query_image_path: str
    radius: float

@app.post("/insert_image_sequential/")
async def insert_image_sequential(image_path: str):
    """Inserta una imagen en el índice KNN (secuencial)."""
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    try:
        knn_sequential.insert_image(image_path)
        knn_sequential.save_data()
        return {"status": "success", "message": f"Image {image_path} inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert image: {e}")

@app.post("/insert_image_rtree/")
async def insert_image_rtree(image_path: str):
    """Inserta una imagen en el índice KNN (R-tree)."""
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    try:
        knn_rtree.insert_image(image_path)
        return {"status": "success", "message": f"Image {image_path} inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert image: {e}")

@app.post("/insert_image_high_d/")
async def insert_image_high_d(image_path: str):
    """Inserta una imagen en el índice KNN de alta dimensión (Faiss)."""
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    try:
        knn_high_d.insert_image(image_path)
        return {"status": "success", "message": f"Image {image_path} inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert image: {e}")

@app.post("/knn_search_sequential/")
async def knn_search_sequential(request: KNNRequest):
    """Realiza una búsqueda KNN secuencial y devuelve las K imágenes más cercanas."""
    if not os.path.exists(request.query_image_path):
        raise HTTPException(status_code=404, detail="Query image not found")
    try:
        query_vector = knn_sequential.extract_features(request.query_image_path)
        query_vector = knn_sequential.normalize_feature_vector(query_vector).cpu().numpy().flatten()
        closest_images = knn_sequential.knn_search(query_vector, k=request.k)
        res = {"status": "success", "message": "KNN search completed", "results": closest_images}
        print(res)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to perform KNN search: {e}")

@app.post("/knn_search_rtree/")
async def knn_search_rtree(request: KNNRequest):
    """Realiza una búsqueda KNN en R-tree y devuelve las K imágenes más cercanas."""
    if not os.path.exists(request.query_image_path):
        raise HTTPException(status_code=404, detail="Query image not found")
    try:
        similar_images = knn_rtree.search_similar_images(request.query_image_path, k=request.k)
        return {"status": "success", "message": "KNN search completed", "results": similar_images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to perform KNN search: {e}")

@app.post("/knn_search_high_d/")
async def knn_search_high_d(request: KNNRequest):
    """Realiza una búsqueda KNN utilizando Faiss (alto dimensional)."""
    if not os.path.exists(request.query_image_path):
        raise HTTPException(status_code=404, detail="Query image not found")
    try:
        similar_images = knn_high_d.search_similar_images(request.query_image_path, k=request.k)
        return {"status": "success", "message": "KNN search completed", "results": similar_images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to perform KNN search: {e}")

@app.post("/range_search_sequential/")
async def range_search_sequential(request: RangeSearchRequest):
    """Realiza una búsqueda de rango en el índice KNN secuencial y devuelve las imágenes dentro del radio especificado."""
    if not os.path.exists(request.query_image_path):
        raise HTTPException(status_code=404, detail="Query image not found")
    try:
        query_vector = knn_sequential.extract_features(request.query_image_path)
        query_vector = knn_sequential.normalize_feature_vector(query_vector).cpu().numpy().flatten()
        range_results = knn_sequential.range_search(query_vector, radius=request.radius)
        return {"status": "success", "message": "Range search completed", "results": range_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to perform range search: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

