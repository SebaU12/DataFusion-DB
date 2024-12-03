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
        <Search />
      </main>
    </div>
  );
}

const InsertImage = () => {
  const [imagePath, setImagePath] = useState("");
  const [preview, setPreview] = useState(null);
  const [message, setMessage] = useState("");

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      const path = URL.createObjectURL(file);
      setImagePath(file.name);
      setPreview(path);
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
      <input type="file" accept="image/*" onChange={handleFileSelect} />
      {preview && <img src={preview} alt="Preview" className="preview" />}
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

const Search = () => {
  const [method, setMethod] = useState("sequential");
  const [searchType, setSearchType] = useState("knn");
  const [queryImage, setQueryImage] = useState("");
  const [preview, setPreview] = useState(null);
  const [k, setK] = useState(1);
  const [start, setStart] = useState(0);
  const [end, setEnd] = useState(0);
  const [results, setResults] = useState([]);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      const path = URL.createObjectURL(file);
      setQueryImage(file.name);
      setPreview(path);
    }
  };

  const handleSearch = async () => {
    let url = "";
    let body = { query_image_path: queryImage };

    if (method === "sequential") {
      if (searchType === "knn") {
        url = "http://127.0.0.1:8000/knn_search_sequential/";
        body.k = parseInt(k);
      } else {
        url = "http://127.0.0.1:8000/range_search_sequential/";
        body.radius = [parseFloat(start), parseFloat(end)];
      }
    } else if (method === "rtree" || method === "high_d") {
      url = method === "rtree" ? "http://127.0.0.1:8000/knn_search_rtree/" : "http://127.0.0.1:8000/knn_search_high_d/";
      body.k = parseInt(k);
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
      console.error("Error al realizar búsqueda", error);
    }
  };

  return (
    <section>
      <h2>Búsqueda</h2>
      <div>
        <label>Técnica:</label>
        <select value={method} onChange={(e) => setMethod(e.target.value)}>
          <option value="sequential">Secuencial</option>
          <option value="rtree">R-tree</option>
          <option value="high_d">High-D</option>
        </select>
      </div>
      {method === "sequential" && (
        <div>
          <label>Tipo de Búsqueda:</label>
          <select value={searchType} onChange={(e) => setSearchType(e.target.value)}>
            <option value="knn">KNN</option>
            <option value="range">Por Rango</option>
          </select>
        </div>
      )}
      <input type="file" accept="image/*" onChange={handleFileSelect} />
      {preview && <img src={preview} alt="Preview" className="preview" />}
      {searchType === "knn" && (
        <input
          type="number"
          placeholder="Número de vecinos (k)"
          value={k}
          onChange={(e) => setK(e.target.value)}
        />
      )}
      {searchType === "range" && method === "sequential" && (
        <div>
          <input
            type="number"
            placeholder="Inicio del rango"
            value={start}
            onChange={(e) => setStart(e.target.value)}
          />
          <input
            type="number"
            placeholder="Fin del rango"
            value={end}
            onChange={(e) => setEnd(e.target.value)}
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
