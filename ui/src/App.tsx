import { useState, useEffect } from "react";

const MAX_COMMENT_LENGTH = 250;

interface Video {
  name: string;
  presigned_url: string;
  size: number;
  last_modified: string;
}

interface CommentData {
  comment_id: string;
  timestamp: string;
  comment: string;
  drawing?: string; // Optional drawing data
}

interface VideoDetails {
  video_url: string;
  comments: CommentData[];
}

interface VideoPlayerProps {
  video: Video;
  onError: (error: string) => void;
}

function VideoPlayer({ video, onError }: VideoPlayerProps) {
  const [isVideoLoading, setIsVideoLoading] = useState(false);
  const [currentComment, setCurrentComment] = useState("");
  const [videoDetails, setVideoDetails] = useState<VideoDetails>({
    video_url: video.presigned_url,
    comments: [],
  });

  const handleVideoCanPlay = () => {
    setIsVideoLoading(false);
  };

  const handleVideoError = (
    e: React.SyntheticEvent<HTMLVideoElement, Event>
  ) => {
    const target = e.target as HTMLVideoElement;
    onError(
      `Failed to load video: ${target.error?.message || "Unknown error"}`
    );
    setIsVideoLoading(false);
  };

  const handleCommentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = e.target.value;
    if (text.length <= MAX_COMMENT_LENGTH) {
      setCurrentComment(text);
    }
  };

  const handleAddComment = () => {
    if (!currentComment.trim()) return;

    const newComment: CommentData = {
      comment_id: crypto.randomUUID(),
      timestamp: "00:00:00", // TODO: Get current video timestamp
      comment: currentComment.trim(),
    };

    setVideoDetails((prev) => ({
      ...prev,
      comments: [...prev.comments, newComment],
    }));
    setCurrentComment("");
  };

  return (
    <div className="flex gap-4">
      {/* Left side - Video Player */}
      <div className="w-2/3 relative">
        <video
          key={video.presigned_url}
          src={video.presigned_url}
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
      </div>

      {/* Right side - Comments Panel */}
      <div className="w-1/3 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
        <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
          Comments
        </h3>

        {/* Comment List */}
        <div className="mb-4 space-y-2 max-h-[calc(100vh-20rem)] overflow-y-auto">
          {videoDetails.comments.map((comment) => (
            <div
              key={comment.comment_id}
              className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
            >
              <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">
                {comment.timestamp}
              </div>
              <div className="text-gray-700 dark:text-gray-300">
                {comment.comment}
              </div>
            </div>
          ))}
        </div>

        {/* Add Comment */}
        <div className="space-y-2">
          <textarea
            value={currentComment}
            onChange={handleCommentChange}
            placeholder="Add a comment..."
            className="w-full p-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 resize-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            rows={3}
          />
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {currentComment.length}/{MAX_COMMENT_LENGTH}
            </span>
            <button
              onClick={handleAddComment}
              disabled={!currentComment.trim()}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Add Comment
            </button>
          </div>
        </div>
      </div>
    </div>
  );
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
        <div className="flex items-center justify-center min-h-[calc(100vh-8rem)]">
          {selectedVideo ? (
            <VideoPlayer video={selectedVideo} onError={setError} />
          ) : (
            <p className="text-gray-500 dark:text-gray-400 text-lg">
              No Video Loaded
            </p>
          )}
          {error && (
            <div className="absolute inset-0 flex items-center justify-center bg-red-900 bg-opacity-50 rounded-lg">
              <div className="text-white text-lg px-4 text-center">{error}</div>
            </div>
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
