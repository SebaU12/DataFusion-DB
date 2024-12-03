import React, { useState } from "react";
import "./App.css";

// Componente para mostrar previsualización de una imagen en los resultados
function ImagePreview({ path, altText }) {
  return (
    <div className="image-preview">
      <img
        src={path}
        alt={altText}
        className="thumbnail"
        style={{ width: "100px", height: "100px", objectFit: "cover" }}
      />
      <p>{altText}</p>
    </div>
  );
}

function App() {
  const [method, setMethod] = useState("sequential");
  const [searchType, setSearchType] = useState("knn");
  const [imagePath, setImagePath] = useState(""); // Ruta de imagen para insertar
  const [searchImagePath, setSearchImagePath] = useState(""); // Ruta de imagen para búsqueda
  const [radius, setRadius] = useState(1.0);
  const [k, setK] = useState(1);
  const [results, setResults] = useState([]); // Lista de resultados
  const [insertMessage, setInsertMessage] = useState("");

  const handleInsert = async (url) => {
    if (!imagePath) {
      alert("Por favor, ingresa la ruta de una imagen.");
      return;
    }

    const body = { image_path: imagePath };

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await response.json();
      setInsertMessage(data.message || "Imagen insertada correctamente.");
    } catch (error) {
      setInsertMessage("Error al insertar la imagen.");
      console.error("Error al insertar la imagen", error);
    }
  };

  const handleSearch = async () => {
    if (!searchImagePath) {
      alert("Por favor, ingresa la ruta de la imagen para la búsqueda.");
      return;
    }

    const body = {
      query_image_path: searchImagePath,
      k: searchType === "knn" ? parseInt(k) : undefined,
      radius: searchType === "range" ? parseFloat(radius) : undefined,
    };

    let url = "";
    if (method === "sequential") {
      url = searchType === "knn"
        ? "http://127.0.0.1:8000/knn_search_sequential/"
        : "http://127.0.0.1:8000/range_search_sequential/";
    } else if (method === "rtree" || method === "high_d") {
      url = "http://127.0.0.1:8000/knn_search_rtree/"; // o el endpoint adecuado para high_d
    }

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await response.json();
      setResults(data.results || []);
    } catch (error) {
      console.error("Error al realizar la búsqueda", error);
    }
  };

  const resetResults = () => {
    setResults([]);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Busqueda de Imágenes con KNN</h1>
      </header>
      <main>
        {/* Insertar Imagen */}
        <section>
          <h2>Insertar Imagen</h2>
          <input
            type="text"
            placeholder="Ruta de la imagen"
            value={imagePath}
            onChange={(e) => setImagePath(e.target.value)}
          />
          <div>
            <button onClick={() => handleInsert("http://127.0.0.1:8000/insert_image_sequential/")}>
              Insertar en Secuencial
            </button>
            <button onClick={() => handleInsert("http://127.0.0.1:8000/insert_image_rtree/")}>
              Insertar en R-tree
            </button>
            <button onClick={() => handleInsert("http://127.0.0.1:8000/insert_image_high_d/")}>
              Insertar en Alta Dimensión
            </button>
          </div>
          {insertMessage && <p>{insertMessage}</p>}
        </section>

        {/* Selección de técnica */}
        <section>
          <h2>Selecciona una técnica de búsqueda</h2>
          <select
            onChange={(e) => {
              const selectedMethod = e.target.value;
              setMethod(selectedMethod);
              if (selectedMethod === "rtree" || selectedMethod === "high_d") {
                setSearchType("knn");
              }
            }}
            value={method}
          >
            <option value="sequential">Secuencial</option>
            <option value="rtree">R-tree</option>
            <option value="high_d">Alta Dimensión</option>
          </select>
        </section>

        {/* Configuración de búsqueda */}
        {method === "sequential" && (
          <section>
            <h2>Elige el tipo de búsqueda</h2>
            <select onChange={(e) => setSearchType(e.target.value)} value={searchType}>
              <option value="knn">KNN</option>
              <option value="range">Búsqueda por Rango</option>
            </select>
          </section>
        )}

        {searchType === "knn" && (
          <section>
            <h2>Introduce el número de vecinos (k)</h2>
            <input
              type="number"
              value={k}
              onChange={(e) => setK(e.target.value)}
              placeholder="Número de vecinos"
            />
          </section>
        )}

        {method === "sequential" && searchType === "range" && (
          <section>
            <h2>Introduce el radio de búsqueda</h2>
            <input
              type="number"
              step="0.1"
              value={radius}
              onChange={(e) => setRadius(e.target.value)}
              placeholder="Radio"
            />
          </section>
        )}

        {/* Imagen para búsqueda */}
        <section>
          <h2>Ruta de imagen para búsqueda</h2>
          <input
            type="text"
            placeholder="Ruta de la imagen"
            value={searchImagePath}
            onChange={(e) => setSearchImagePath(e.target.value)}
          />
        </section>

        <button onClick={handleSearch}>Buscar</button>
        <button onClick={resetResults}>Reiniciar Resultados</button>

        {/* Resultados */}
        <section>
          {results.length > 0 && (
            <div className="results">
              <h2>Resultados</h2>
              <div className="image-grid">
                {results.map((result, index) => (
                  <ImagePreview
                    key={index}
                    path={result}
                    altText={`Resultado ${index + 1}`}
                  />
                ))}
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
