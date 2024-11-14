import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const ResultsContainer = styled.div`
  width: 100%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
`;

const ResultItem = styled(motion.div)`
  background-color: #fff;
  padding: 15px;
  margin: 8px 0;
  border-radius: 5px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
`;

const QueryInfo = styled.p`
  color: #666;
  font-size: 0.9rem;
`;

export default function Results({ results, query, executionTime }) {
  return (
    <ResultsContainer>
      {query && <QueryInfo>Consulta: {query}</QueryInfo>}
      {executionTime && <QueryInfo>Tiempo de ejecución: {executionTime} ms</QueryInfo>}
      {results.map((result, index) => (
        <ResultItem
          key={index}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h3>{result.title}</h3>
          <p>{result.content}</p>
        </ResultItem>
      ))}
    </ResultsContainer>
  );
}
