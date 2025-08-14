import React, { useState } from "react";
import FileUploader from "./components/FileUploader";
import ResultsView from "./components/ResultsView";

function App() {
  const [results, setResults] = useState(null);

  return (
    <div
      style={{
        maxWidth: "900px",
        margin: "0 auto",
        padding: "20px",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",     // ✅ Center children horizontally
        justifyContent: "center", // ✅ Center vertically if height allows
        minHeight: "100vh",       // Full viewport height
        textAlign: "center",      // ✅ Center text inside elements
      }}
    >
      <h1>USB PD Specification Parser</h1>

      {/* File upload area */}
      <FileUploader onUploadComplete={(data) => setResults(data)} />

      {/* Results table (shows after upload completes) */}
      {results && <ResultsView results={results} />}
    </div>
  );
}

export default App;
