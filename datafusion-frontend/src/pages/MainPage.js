import React, { useState } from "react";
import styled from "styled-components";
import { motion } from "framer-motion";
import SQLQueryGenerator from "./SQLQueryGenerator";
import QueryForm from "./QueryForm";
import Results from "./Results";

const MainPageContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
`;

const Title = styled(motion.h1)`
  font-size: 2rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 1rem;
`;

const SQLButton = styled(motion.button)`
  padding: 0.5rem 1rem;
  font-size: 1rem;
  color: #fff;
  background-color: #007bff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin-bottom: 1rem;
  &:hover {
    background-color: #0056b3;
  }
`;

export default function MainPage() {
  const [results, setResults] = useState([]);
  const [isSQLModalOpen, setIsSQLModalOpen] = useState(false);
  const [generatedQuery, setGeneratedQuery] = useState("");
  const [executionTime, setExecutionTime] = useState(null);

  const handleSearch = (data) => {
    setResults(data);
  };

  const handleGenerateQuery = async (query) => {
    setGeneratedQuery(query);
    setIsSQLModalOpen(false);

    // Simulacion de resultados
    const startTime = Date.now();
    const simulatedResults = await fetchResults(query); // test de resultados
    setExecutionTime(Date.now() - startTime);
    setResults(simulatedResults);
  };

  return (
    <MainPageContainer>
      <Title initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 1 }}>
        DataFusion DB - Búsqueda Avanzada
      </Title>
      <SQLButton onClick={() => setIsSQLModalOpen(true)} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
        Generar Consulta SQL-like
      </SQLButton>
      <QueryForm onSearch={handleSearch} />
      <Results results={results} query={generatedQuery} executionTime={executionTime} />
      {isSQLModalOpen && (
        <SQLQueryGenerator
          onClose={() => setIsSQLModalOpen(false)}
          onGenerateQuery={handleGenerateQuery}
        />
      )}
    </MainPageContainer>
  );
}

// TEST ara obtener resultados de búsqueda
async function fetchResults(query) {
  // TEST
  return [
    { title: "Resultado 1", content: "Contenido relacionado con " + query },
    { title: "Resultado 2", content: "Contenido adicional para " + query },
  ];
}
