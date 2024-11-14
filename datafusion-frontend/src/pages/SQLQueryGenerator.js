import React, { useState } from "react";
import styled from "styled-components";

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: #fff;
  padding: 2rem;
  width: 90%;
  max-width: 500px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  text-align: center;
`;

const Title = styled.h2`
  font-size: 1.5rem;
  margin-bottom: 1rem;
`;

const TextArea = styled.textarea`
  width: 100%;
  height: 80px;
  margin-bottom: 1rem;
  padding: 0.5rem;
  font-size: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: none;
`;

const Button = styled.button`
  background-color: #007bff;
  color: #fff;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  margin: 0 0.5rem;
  &:hover {
    background-color: #0056b3;
  }
`;

export default function SQLQueryGenerator({ onClose, onGenerateQuery }) {
  const [query, setQuery] = useState("");

  const handleGenerate = () => {
    onGenerateQuery(query || "select * from Audio where lyric @@ 'amor en tiempos de guerra' limit 10");
  };

  return (
    <ModalOverlay>
      <ModalContent>
        <Title>Generar Consulta SQL-like</Title>
        <TextArea
          placeholder="Escribe tu consulta SQL-like aquí..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <div>
          <Button onClick={handleGenerate}>Generar</Button>
          <Button onClick={onClose}>Cerrar</Button>
        </div>
      </ModalContent>
    </ModalOverlay>
  );
}
