import React, { useState } from "react";
import "./App.css";

function App() {
  const [method, setMethod] = useState("sequential");
  const [searchType, setSearchType] = useState("knn");
  const [imagePath, setImagePath] = useState("");
  const [searchImagePath, setSearchImagePath] = useState(""); // Para la ruta de búsqueda
  const [radius, setRadius] = useState(1.0);
  const [k, setK] = useState(1);
  const [results, setResults] = useState([]);
  const [insertMessage, setInsertMessage] = useState("");

  const handleInsert = async (url) => {
    if (!imagePath) {
      alert("Por favor, ingresa la ruta de una imagen.");
      return;
    }

    const insertUrl = `${url}?image_path=${encodeURIComponent(imagePath)}`;

    try {
      const response = await fetch(insertUrl, {
        method: "POST",
        headers: { "accept": "application/json" },
        body: "",
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
    console.log(body)

    let url = "";
    if (method === "sequential") {
      url = searchType === "knn"
        ? "http://127.0.0.1:8000/knn_search_sequential/"
        : "http://127.0.0.1:8000/range_search_sequential/";
    } else if (method === "rtree") {
      url = "http://127.0.0.1:8000/knn_search_rtree/";
    } else if (method === "high_d") {
      url = "http://127.0.0.1:8000/knn_search_high_d/";
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

  return (
    <div className="App">
      <header className="App-header">
        <h1>Busqueda de Imágenes con KNN</h1>
      </header>
      <main>
        <section>
          <h2>Insertar Imagen</h2>
          <input
            type="text"
            placeholder="Ingresa el path local de la imagen"
            value={imagePath}
            onChange={(e) => setImagePath(e.target.value)}
          />
          <p>{imagePath && `Ruta seleccionada: ${imagePath}`}</p>
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
          {imagePath && <img src={imagePath} alt="Imagen seleccionada" className="preview" />}
        </section>

        <section>
          <h2>Selecciona una técnica de búsqueda</h2>
          <select onChange={(e) => setMethod(e.target.value)} value={method}>
            <option value="sequential">Secuencial</option>
            <option value="rtree">R-tree</option>
            <option value="high_d">Alta Dimensión</option>
          </select>
        </section>

        {method === "sequential" && (
          <section>
            <h2>Elige el tipo de búsqueda</h2>
            <select onChange={(e) => setSearchType(e.target.value)} value={searchType}>
              <option value="knn">KNN</option>
              <option value="range">Búsqueda por Rango</option>
            </select>
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

        {method === "sequential" && searchType === "knn" && (
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

        <section>
          <h2>Ruta de imagen para búsqueda</h2>
          <input
            type="text"
            placeholder="Ingresa el path local de la imagen para búsqueda"
            value={searchImagePath}
            onChange={(e) => setSearchImagePath(e.target.value)}
          />
          {searchImagePath && <img src={searchImagePath} alt="Imagen seleccionada para búsqueda" className="preview" />}
        </section>

        <button onClick={handleSearch}>Buscar</button>

        <section>
          {results.length > 0 && (
            <div className="results">
              <h2>Resultados</h2>
              {results.map((result, index) => (
                <div key={index} className="result-item">
                  <p>{result}</p>
                  <img src={result} alt={`Resultado ${index}`} className="preview" />
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
