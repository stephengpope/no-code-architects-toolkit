import { useState } from "react";

const MAX_COMMENT_LENGTH = 250;

export interface Video {
  name: string;
  presigned_url: string;
  size: number;
  last_modified: string;
}

interface CommentData {
  comment_id: string;
  timestamp: string;
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

export function VideoPlayer({ video, onError }: VideoPlayerProps) {
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
