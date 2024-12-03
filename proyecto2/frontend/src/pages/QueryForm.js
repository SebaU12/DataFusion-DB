import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const FormContainer = styled(motion.div)`
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  width: 100%;
  max-width: 600px;
  box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
`;

const Input = styled.input`
  width: 100%;
  padding: 10px;
  margin-top: 10px;
  font-size: 1rem;
  border-radius: 4px;
  border: 1px solid #ddd;
  margin-bottom: 15px;
`;

const Select = styled.select`
  width: 100%;
  padding: 10px;
  font-size: 1rem;
  border-radius: 4px;
  border: 1px solid #ddd;
  margin-bottom: 15px;
`;

const Button = styled(motion.button)`
  width: 100%;
  padding: 12px;
  font-size: 1.1rem;
  color: white;
  background-color: #4a90e2;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  &:hover {
    background-color: #357ABD;
  }
`;

export default function QueryForm({ onSearch }) {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(10);
  const [indexMethod, setIndexMethod] = useState('Propio');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch({ query, topK, indexMethod });
  };

  return (
    <FormContainer
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      <h2>Realiza tu Búsqueda</h2>
      <form onSubmit={handleSubmit}>
        <label>Consulta</label>
        <Input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Escribe tu consulta..."
        />
        <label>Top K Resultados</label>
        <Input
          type="number"
          value={topK}
          onChange={(e) => setTopK(e.target.value)}
        />
        <label>Método de Indexación</label>
        <Select value={indexMethod} onChange={(e) => setIndexMethod(e.target.value)}>
          <option value="Propio">Implementación Propia</option>
          <option value="PostgreSQL">PostgreSQL</option>
          <option value="MongoDB">MongoDB</option>
        </Select>
        <Button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} type="submit">
          Buscar
        </Button>
      </form>
    </FormContainer>
  );
}
