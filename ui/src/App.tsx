function App() {
  const handleLoadVideos = () => {
    // TODO: Implement video loading functionality
    console.log("Loading videos...");
  };

  return (
    <div className="max-w-7xl mx-auto p-8 text-center">
      <div className="flex flex-col items-center gap-8">
        <h1 className="text-4xl font-bold text-gray-800">
          No-Code Architects Toolkit
        </h1>
        <button
          onClick={handleLoadVideos}
          className="bg-indigo-600 text-white px-6 py-3 rounded-lg text-lg font-medium hover:bg-indigo-700 active:transform active:scale-95 transition-all"
        >
          Load Videos
        </button>
      </div>
    </div>
  );
}

export default App;
