import React, { useState } from "react";
import "./App.css";

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>KNN Image Search</h1>
      </header>
      <main>
        <InsertImage />
        <KnnSearch />
        <RangeSearch />
      </main>
    </div>
  );
}

const InsertImage = () => {
  const [imagePath, setImagePath] = useState("");
  const [preview, setPreview] = useState(null);
  const [message, setMessage] = useState("");

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setImagePath(file.path); // Esto funciona en entornos donde se puede acceder a file.path (Electron, etc.)
      setPreview(URL.createObjectURL(file));
    }
  };

  const handleInsert = async (url) => {
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_path: imagePath }),
      });
      const data = await response.json();
      setMessage(data.message);
    } catch (error) {
      setMessage("Error al insertar la imagen.");
    }
  };

  return (
    <section>
      <h2>Insertar Imagen</h2>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      {preview && <img src={preview} alt="Vista previa" className="preview" />}
      <p>Ruta seleccionada: {imagePath || "Ninguna"}</p>
      <div>
        <button onClick={() => handleInsert("http://127.0.0.1:8000/insert_image_sequential/")}>
          Índice Secuencial
        </button>
        <button onClick={() => handleInsert("http://127.0.0.1:8000/insert_image_rtree/")}>
          Índice R-tree
        </button>
        <button onClick={() => handleInsert("http://127.0.0.1:8000/insert_image_high_d/")}>
          Índice Alta Dimensión
        </button>
      </div>
      {message && <p>{message}</p>}
    </section>
  );
};

const KnnSearch = () => {
  const [queryImage, setQueryImage] = useState("");
  const [k, setK] = useState(1);
  const [results, setResults] = useState([]);
  const [preview, setPreview] = useState(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setQueryImage(file.path); // Ruta de la imagen
      setPreview(URL.createObjectURL(file)); // Vista previa
    }
  };

  const handleSearch = async (url) => {
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query_image_path: queryImage, k: parseInt(k) }),
      });
      const data = await response.json();
      setResults(data.results || []);
    } catch (error) {
      console.error("Error al buscar imágenes", error);
    }
  };

  return (
    <section>
      <h2>Búsqueda KNN</h2>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      {preview && <img src={preview} alt="Vista previa" className="preview" />}
      <p>Ruta seleccionada: {queryImage || "Ninguna"}</p>
      <input
        type="number"
        placeholder="Número de vecinos (k)"
        value={k}
        onChange={(e) => setK(e.target.value)}
      />
      <div>
        <button onClick={() => handleSearch("http://127.0.0.1:8000/knn_search_sequential/")}>
          Secuencial
        </button>
        <button onClick={() => handleSearch("http://127.0.0.1:8000/knn_search_rtree/")}>
          R-tree
        </button>
        <button onClick={() => handleSearch("http://127.0.0.1:8000/knn_search_high_d/")}>
          Alta Dimensión
        </button>
      </div>
      <div className="results">
        {results.map((result, index) => (
          <div key={index}>
            <p>{result}</p>
            <img src={result} alt={`Resultado ${index}`} className="preview" />
          </div>
        ))}
      </div>
    </section>
  );
};

const RangeSearch = () => {
  const [queryImage, setQueryImage] = useState("");
  const [radius, setRadius] = useState(1.0);
  const [results, setResults] = useState([]);
  const [preview, setPreview] = useState(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setQueryImage(file.path); // Ruta de la imagen
      setPreview(URL.createObjectURL(file)); // Vista previa
    }
  };

  const handleSearch = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/range_search_sequential/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query_image_path: queryImage, radius: parseFloat(radius) }),
      });
      const data = await response.json();
      setResults(data.results || []);
    } catch (error) {
      console.error("Error al realizar búsqueda por rango", error);
    }
  };

  return (
    <section>
      <h2>Búsqueda por Rango</h2>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      {preview && <img src={preview} alt="Vista previa" className="preview" />}
      <p>Ruta seleccionada: {queryImage || "Ninguna"}</p>
      <input
        type="number"
        step="0.1"
        placeholder="Radio"
        value={radius}
        onChange={(e) => setRadius(e.target.value)}
      />
      <button onClick={handleSearch}>Buscar</button>
      <div className="results">
        {results.map((result, index) => (
          <div key={index}>
            <p>{result}</p>
            <img src={result} alt={`Resultado ${index}`} className="preview" />
          </div>
        ))}
      </div>
    </section>
  );
};

export default App;
