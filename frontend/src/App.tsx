import { useEffect, useState } from "react";

function App() {
  const [status, setStatus] = useState("Checking...");

  useEffect(() => {
    fetch("/api/health")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Backend request failed");
        }
        return response.json();
      })
      .then((data) => {
        setStatus(data.status);
      })
      .catch((error) => {
        console.error(error);
        setStatus("Connection failed");
      });
  }, []);

  return (
    <div>
      <h1>AI Resume Builder</h1>
      <p>Backend status: {status}</p>
    </div>
  );
}

export default App;
