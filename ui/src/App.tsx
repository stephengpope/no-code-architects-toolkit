import { useState, useEffect } from "react";

function App() {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    // Check if user has a dark mode preference
    const darkModePreference = localStorage.getItem("darkMode") === "true";
    setIsDarkMode(darkModePreference);
    if (darkModePreference) {
      document.documentElement.classList.add("dark");
    }
  }, []);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle("dark");
    localStorage.setItem("darkMode", (!isDarkMode).toString());
  };

  const handleLoadVideos = () => {
    // TODO: Implement video loading functionality
    console.log("Loading videos...");
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      {/* Navigation Bar */}
      <nav className="border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 transition-colors duration-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Left side */}
            <div className="flex items-center">
              <button
                onClick={toggleDarkMode}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
                aria-label="Toggle dark mode"
              >
                {isDarkMode ? "🌞" : "🌙"}
              </button>
              <h1 className="ml-4 text-xl font-bold text-gray-800 dark:text-white">
                No-Code Architects Toolkit
              </h1>
            </div>

            {/* Right side */}
            <button
              onClick={handleLoadVideos}
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 active:transform active:scale-95 transition-all"
            >
              Load Videos
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-center h-[calc(100vh-8rem)]">
          <p className="text-gray-500 dark:text-gray-400 text-lg">
            No Video Loaded
          </p>
        </div>
      </main>
    </div>
  );
}

export default App;
