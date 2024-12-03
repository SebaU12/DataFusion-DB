import React from "react";

const FilePicker = ({ onFileChange }) => {
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      onFileChange(URL.createObjectURL(file));
    }
  };

  return (
    <div>
      <input type="file" accept="image/*" onChange={handleFileChange} />
    </div>
  );
};

export default FilePicker;
