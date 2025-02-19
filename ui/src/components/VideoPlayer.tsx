import { useState, useRef, useEffect } from "react";
import { Canvas } from "fabric";

const MAX_COMMENT_LENGTH = 250;
const TOOLBAR_COLORS = [
  "#000000",
  "#FF0000",
  "#00FF00",
  "#0000FF",
  "#FFFF00",
  "#FF00FF",
  "#00FFFF",
];

export interface Video {
  name: string;
  presigned_url: string;
  size: number;
  last_modified: string;
}

interface CommentData {
  comment_id: string;
  timestamp: number;
  comment: string;
  drawing?: string; // JSON string of Fabric.js canvas data
}

interface VideoDetails {
  video_url: string;
  comments: CommentData[];
}

interface VideoPlayerProps {
  video: Video;
  onError: (error: string) => void;
}

function formatTimestamp(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours.toString().padStart(2, "0")}:${minutes
      .toString()
      .padStart(2, "0")}:${remainingSeconds.toString().padStart(2, "0")}`;
  }
  return `${minutes.toString().padStart(2, "0")}:${remainingSeconds
    .toString()
    .padStart(2, "0")}`;
}

export function VideoPlayer({ video, onError }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fabricCanvasRef = useRef<Canvas | null>(null);
  const [isVideoLoading, setIsVideoLoading] = useState(false);
  const [currentComment, setCurrentComment] = useState("");
  const [isDrawingMode, setIsDrawingMode] = useState(false);
  const [selectedColor, setSelectedColor] = useState(TOOLBAR_COLORS[0]);
  const [videoDetails, setVideoDetails] = useState<VideoDetails>({
    video_url: video.presigned_url,
    comments: [],
  });

  // Initialize Fabric.js canvas
  useEffect(() => {
    if (canvasRef.current && videoRef.current) {
      const video = videoRef.current;
      const canvas = new Canvas(canvasRef.current, {
        width: video.clientWidth,
        height: video.clientHeight,
        isDrawingMode: false,
      });

      fabricCanvasRef.current = canvas;
      if (canvas.freeDrawingBrush) {
        canvas.freeDrawingBrush.width = 2;
        canvas.freeDrawingBrush.color = selectedColor;
      }

      // Cleanup
      return () => {
        canvas.dispose();
        fabricCanvasRef.current = null;
      };
    }
  }, []);

  // Update brush color when selected color changes
  useEffect(() => {
    if (fabricCanvasRef.current?.freeDrawingBrush) {
      fabricCanvasRef.current.freeDrawingBrush.color = selectedColor;
    }
  }, [selectedColor]);

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
    if (!currentComment.trim() || !videoRef.current || !fabricCanvasRef.current)
      return;

    const newComment: CommentData = {
      comment_id: crypto.randomUUID(),
      timestamp: videoRef.current.currentTime,
      comment: currentComment.trim(),
      drawing: fabricCanvasRef.current.isEmpty()
        ? undefined
        : JSON.stringify(fabricCanvasRef.current.toJSON()),
    };

    setVideoDetails((prev) => ({
      ...prev,
      comments: [...prev.comments, newComment].sort(
        (a, b) => a.timestamp - b.timestamp
      ),
    }));

    // Clear the canvas and comment
    fabricCanvasRef.current.clear();
    setCurrentComment("");
    setIsDrawingMode(false);
  };

  const handleCommentClick = (timestamp: number, drawing?: string) => {
    if (videoRef.current && fabricCanvasRef.current) {
      videoRef.current.currentTime = timestamp;

      // Clear current canvas
      fabricCanvasRef.current.clear();

      // Load drawing if exists
      if (drawing) {
        fabricCanvasRef.current.loadFromJSON(drawing, () => {
          fabricCanvasRef.current?.renderAll();
        });
      }
    }
  };

  const toggleDrawingMode = () => {
    if (fabricCanvasRef.current) {
      const newMode = !isDrawingMode;
      setIsDrawingMode(newMode);
      fabricCanvasRef.current.isDrawingMode = newMode;
    }
  };

  return (
    <div className="flex w-full">
      {/* Left side - Video Player */}
      <div
        id="video-player"
        className="flex-1 p-8 flex flex-col items-center justify-center"
      >
        <div className="w-full max-w-4xl relative">
          <video
            ref={videoRef}
            key={video.presigned_url}
            src={video.presigned_url}
            controls
            className="w-full rounded-lg shadow-lg"
            onCanPlay={handleVideoCanPlay}
            onError={handleVideoError}
          >
            Your browser does not support the video tag.
          </video>
          <canvas
            ref={canvasRef}
            className="absolute inset-0 pointer-events-auto"
          />
          {isVideoLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-50 rounded-lg">
              <div className="text-white text-lg">Loading video...</div>
            </div>
          )}
        </div>

        {/* Drawing Toolbar */}
        <div className="mt-4 p-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg flex items-center space-x-4">
          <button
            onClick={toggleDrawingMode}
            className={`p-2 rounded-lg transition-colors ${
              isDrawingMode
                ? "bg-indigo-100 dark:bg-indigo-900"
                : "hover:bg-gray-100 dark:hover:bg-gray-700"
            }`}
            title={isDrawingMode ? "Disable drawing" : "Enable drawing"}
          >
            ✏️
          </button>
          <div className="flex items-center space-x-2">
            {TOOLBAR_COLORS.map((color) => (
              <button
                key={color}
                onClick={() => setSelectedColor(color)}
                className={`w-6 h-6 rounded-full border-2 transition-all ${
                  selectedColor === color
                    ? "border-indigo-500 scale-110"
                    : "border-gray-300 hover:scale-105"
                }`}
                style={{ backgroundColor: color }}
                title={`Select ${color} color`}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Right side - Comments Panel */}
      <div
        id="comments-panel"
        className="w-96 h-[calc(100vh-64px)] bg-white dark:bg-gray-800 shadow-lg overflow-hidden flex flex-col border-l border-gray-200 dark:border-gray-700"
      >
        <h3 className="text-lg font-semibold p-4 text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700">
          Comments
        </h3>

        {/* Comment List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {videoDetails.comments.map((comment) => (
            <div
              key={comment.comment_id}
              className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
              onClick={() =>
                handleCommentClick(comment.timestamp, comment.drawing)
              }
            >
              <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">
                {formatTimestamp(comment.timestamp)}
                {comment.drawing && (
                  <span className="ml-2 text-indigo-500">✏️</span>
                )}
              </div>
              <div className="text-gray-700 dark:text-gray-300">
                {comment.comment}
              </div>
            </div>
          ))}
        </div>

        {/* Add Comment */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-4 space-y-2">
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
