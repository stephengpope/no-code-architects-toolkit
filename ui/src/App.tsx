import "./App.css";

function App() {
  const handleLoadVideos = () => {
    // TODO: Implement video loading functionality
    console.log("Loading videos...");
  };

  return (
    <div className="app-container">
      <h1>No-Code Architects Toolkit</h1>
      <button onClick={handleLoadVideos} className="load-button">
        Load Videos
      </button>
    </div>
  );
}

export default App;
