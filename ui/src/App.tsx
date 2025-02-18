import { useState, useEffect } from "react";

interface Video {
  name: string;
  presigned_url: string;
  size: number;
  last_modified: string;
}

function App() {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null);
  const [videos, setVideos] = useState<Video[]>([]);
  const [isVideoLoading, setIsVideoLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  const handleLoadVideos = async () => {
    setError(null);
    try {
      const response = await fetch(
        `${
          import.meta.env.VITE_BACKEND_URL || "http://localhost:8080"
        }/v1/videos`,
        {
          headers: {
            "x-api-key": import.meta.env.VITE_API_KEY || "",
          },
        }
      );
      if (!response.ok) {
        throw new Error("Failed to fetch videos");
      }
      const data = await response.json();
      setVideos(data.videos);
      setIsDialogOpen(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      console.error("Error loading videos:", err);
    } finally {
      setIsVideoLoading(false);
    }
  };

  const handleVideoSelect = (video: Video) => {
    setSelectedVideo(video);
    setIsDialogOpen(false);
    setIsVideoLoading(true);
  };

  const handleVideoCanPlay = () => {
    setIsVideoLoading(false);
  };

  const handleVideoError = (
    e: React.SyntheticEvent<HTMLVideoElement, Event>
  ) => {
    const target = e.target as HTMLVideoElement;
    setError(
      `Failed to load video: ${target.error?.message || "Unknown error"}`
    );
    setIsVideoLoading(false);
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
            <div className="w-full max-w-4xl relative">
              <video
                key={selectedVideo.presigned_url}
                src={selectedVideo.presigned_url}
                controls
                className="w-full rounded-lg shadow-lg"
                onCanPlay={handleVideoCanPlay}
                onError={handleVideoError}
              >
                Your browser does not support the video tag.
              </video>
              {isVideoLoading && (
                <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-50 rounded-lg">
                  <div className="text-white text-lg">Loading video...</div>
                </div>
              )}
              {error && (
                <div className="absolute inset-0 flex items-center justify-center bg-red-900 bg-opacity-50 rounded-lg">
                  <div className="text-white text-lg px-4 text-center">
                    {error}
                  </div>
                </div>
              )}
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
                {videos.map((video) => (
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
