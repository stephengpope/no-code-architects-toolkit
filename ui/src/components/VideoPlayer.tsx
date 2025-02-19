import { useState, useRef } from "react";

const MAX_COMMENT_LENGTH = 250;

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
  drawing?: string;
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
    if (!currentComment.trim() || !videoRef.current) return;

    const newComment: CommentData = {
      comment_id: crypto.randomUUID(),
      timestamp: videoRef.current.currentTime,
      comment: currentComment.trim(),
    };

    setVideoDetails((prev) => ({
      ...prev,
      comments: [...prev.comments, newComment].sort(
        (a, b) => a.timestamp - b.timestamp
      ),
    }));
    setCurrentComment("");
  };

  const handleCommentClick = (timestamp: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = timestamp;
    }
  };

  return (
    <div className="flex w-full">
      {/* Left side - Video Player */}
      <div
        id="video-player"
        className="flex-1 p-8 flex items-center justify-center"
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
          {isVideoLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-50 rounded-lg">
              <div className="text-white text-lg">Loading video...</div>
            </div>
          )}
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
              onClick={() => handleCommentClick(comment.timestamp)}
            >
              <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">
                {formatTimestamp(comment.timestamp)}
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
