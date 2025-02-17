import { useState, useEffect } from "react";

// Available videos list
const AVAILABLE_VIDEOS = [
  {
    name: "stephen_horizontal_video.mp4",
    url: import.meta.env.VITE_EXAMPLE_HARDCODED_VIDEO_URL,
  },
];

function App() {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedVideo, setSelectedVideo] = useState<{
    name: string;
    url: string;
  } | null>(null);

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
    setIsDialogOpen(true);
  };

  const handleVideoSelect = (video: { name: string; url: string }) => {
    setSelectedVideo(video);
    setIsDialogOpen(false);
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
          {selectedVideo ? (
            <div className="w-full max-w-4xl">
              <video
                src={selectedVideo.url}
                controls
                className="w-full rounded-lg shadow-lg"
              >
                Your browser does not support the video tag.
              </video>
            </div>
          ) : (
            <p className="text-gray-500 dark:text-gray-400 text-lg">
              No Video Loaded
            </p>
          )}
        </div>
      </main>

      {/* Video Selection Dialog */}
      {isDialogOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
                Select a Video
              </h2>
              <div className="space-y-2">
                {AVAILABLE_VIDEOS.map((video) => (
                  <button
                    key={video.name}
                    onClick={() => handleVideoSelect(video)}
                    className="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 transition-colors duration-200"
                  >
                    {video.name}
                  </button>
                ))}
              </div>
              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setIsDialogOpen(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors duration-200"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
