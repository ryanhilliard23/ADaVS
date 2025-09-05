import { useState } from "react";

function App() {

  const [response, setResponse] = useState("");

  /* Temporary test to communicate with backend */
  const handleClick = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/test");
      const data = await res.json();
      setResponse(data.message);
    } catch (err) {
      setResponse("Error: Could not reach backend");
    }
  };

  return (
    <div>
      <h1>ADaVS Dashboard</h1>
      <p>Welcome! The frontend is running.</p>

      {/* Temporary Test Button */}
      <h2>Backend Test</h2>
      <button onClick={handleClick}>Ping Backend</button>
      {response && <p>{response}</p>}
    </div>
  );
}

export default App;
