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
        <SearchImage />
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
      const fileURL = URL.createObjectURL(file);
      setPreview(fileURL);
      setImagePath(file.path || file.name);
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
      setMessage(data.message || "Imagen insertada correctamente.");
    } catch (error) {
      setMessage("Error al insertar la imagen.");
    }
  };

  return (
    <section>
      <h2>Insertar Imagen</h2>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      {preview && <img src={preview} alt="Vista previa" className="preview" />}
      <div>
        <button onClick={() => handleInsert("http://127.0.0.1:8000/insert_image_sequential/")}>
          Índice Secuencial
        </button>
        <button onClick={() => handleInsert("http://127.0.0.1:8000/insert_image_rtree/")}>
          Índice R-tree
        </button>
        <button onClick={() => handleInsert("http://127.0.0.1:8000/insert_image_high_d/")}>
          Índice High-D
        </button>
      </div>
      {message && <p>{message}</p>}
    </section>
  );
};

const SearchImage = () => {
  const [queryImage, setQueryImage] = useState("");
  const [preview, setPreview] = useState(null);
  const [mode, setMode] = useState("knn");
  const [technique, setTechnique] = useState("sequential");
  const [k, setK] = useState(1);
  const [rangeStart, setRangeStart] = useState(0);
  const [rangeEnd, setRangeEnd] = useState(1);
  const [results, setResults] = useState([]);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const fileURL = URL.createObjectURL(file);
      setPreview(fileURL);
      setQueryImage(file.path || file.name);
    }
  };

  const handleSearch = async () => {
    let url = "";
    let body = {};

    if (mode === "knn") {
      url =
        technique === "sequential"
          ? "http://127.0.0.1:8000/knn_search_sequential/"
          : technique === "rtree"
          ? "http://127.0.0.1:8000/knn_search_rtree/"
          : "http://127.0.0.1:8000/knn_search_high_d/";

      body = { query_image_path: queryImage, k: parseInt(k) };
    } else {
      url = "http://127.0.0.1:8000/range_search_sequential/";
      body = { query_image_path: queryImage, radius: parseFloat(rangeEnd - rangeStart) };
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
      console.error("Error en la búsqueda:", error);
    }
  };

  return (
    <section>
      <h2>Búsqueda de Imágenes</h2>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      {preview && <img src={preview} alt="Vista previa" className="preview" />}
      <div>
        <label>
          <input
            type="radio"
            value="knn"
            checked={mode === "knn"}
            onChange={() => setMode("knn")}
          />
          Búsqueda KNN
        </label>
        <label>
          <input
            type="radio"
            value="range"
            checked={mode === "range"}
            onChange={() => setMode("range")}
          />
          Búsqueda por Rango
        </label>
      </div>
      <div>
        <label>
          Técnica:
          <select value={technique} onChange={(e) => setTechnique(e.target.value)}>
            <option value="sequential">Secuencial</option>
            <option value="rtree">R-tree</option>
            <option value="high_d">High-D</option>
          </select>
        </label>
      </div>
      {mode === "knn" ? (
        <input
          type="number"
          placeholder="Número de vecinos (k)"
          value={k}
          onChange={(e) => setK(e.target.value)}
        />
      ) : (
        <div>
          <input
            type="number"
            placeholder="Inicio del rango"
            value={rangeStart}
            onChange={(e) => setRangeStart(e.target.value)}
          />
          <input
            type="number"
            placeholder="Fin del rango"
            value={rangeEnd}
            onChange={(e) => setRangeEnd(e.target.value)}
          />
        </div>
      )}
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
