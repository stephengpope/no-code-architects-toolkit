# Copyright (c) 2025 Stephen G. Pope
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os
import requests
import logging
import time
from typing import Dict, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

class RunpodWhisperClient:
    """Client for interacting with Runpod Whisper API service."""
    
    def __init__(self):
        self.api_key = os.environ.get('RUNPOD_API_KEY')
        if not self.api_key:
            raise ValueError("RUNPOD_API_KEY environment variable is not set")
        
        self.base_url = "https://api.runpod.ai/v2/n8j2ln49qh2n4x/run"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Configuration from environment variables
        self.webhook_url = os.environ.get('RUNPOD_WEBHOOK_URL')
        self.max_wait_time = int(os.environ.get('RUNPOD_MAX_WAIT_TIME', '600'))
        self.poll_interval = int(os.environ.get('RUNPOD_POLL_INTERVAL', '5'))

    def transcribe_audio(self, audio_url: str, model: str = "large-v3", language: Optional[str] = None, webhook_url: Optional[str] = None, initial_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio using Runpod Whisper API.
        
        Args:
            audio_url: URL of the audio/video file to transcribe
            model: Whisper model to use (default: "large-v")
            language: Language code for transcription (optional)
            webhook_url: Webhook URL for async processing (optional)
        
        Returns:
            Dictionary containing transcription results in Whisper format
        """
        try:
            # Prepare the request payload
            payload = {
                "input": {
                    "audio": audio_url,
                    "model": model,
                    "temperature": 0.0,  # Default temperature for transcription
                    # "enable_vad": True,  # Enable Voice Activity Detection
                }
            }
            
            # Add language if specified
            if language and language != 'auto':
                payload["input"]["language"] = language

            if initial_prompt:
                payload["input"]["initial_prompt"] = initial_prompt

            # Add webhook if provided for async processing, or use default webhook
            webhook_to_use = webhook_url or self.webhook_url
            if webhook_to_use:
                payload["webhook"] = webhook_to_use
                logger.info(f"Using async processing with webhook: {webhook_to_use}")
            else:
                logger.info("No webhook provided, will use synchronous polling")
            
            logger.info(f"Sending transcription request to Runpod API for audio: {audio_url}")
            logger.info(f"Using model: {model}, language: {language}")
            
            # Make the API call
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=300  # 5 minute timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info("Runpod API call successful")
            
            # If webhook is provided, return job information for async processing
            webhook_to_use = webhook_url or self.webhook_url
            if webhook_to_use:
                logger.info(f"Async job submitted. Job ID: {result.get('id', 'unknown')}")
                return {
                    "status": "submitted",
                    "job_id": result.get("id"),
                    "webhook_url": webhook_to_use,
                    "async": True
                }
            
            # For synchronous processing, poll for results
            return self._poll_for_results(result, self.max_wait_time, self.poll_interval)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Runpod API request failed: {str(e)}")
            raise Exception(f"Runpod API request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error in Runpod transcription: {str(e)}")
            raise
    
    def _poll_for_results(self, initial_response: Dict[str, Any], max_wait_time: int = 600, poll_interval: int = 5) -> Dict[str, Any]:
        """
        Poll Runpod API for job completion when no webhook is provided.
        
        Args:
            initial_response: Initial response from Runpod API
            max_wait_time: Maximum time to wait in seconds (default: 10 minutes)
            poll_interval: Time between polls in seconds (default: 5 seconds)
            
        Returns:
            Dictionary containing transcription results in Whisper format
        """
        job_id = initial_response.get("id")
        if not job_id:
            # If no job ID, assume synchronous response with results
            return self._transform_runpod_response(initial_response)
        
        logger.info(f"Polling for job completion. Job ID: {job_id}")
        
        status_url = f"https://api.runpod.ai/v2/n8j2ln49qh2n4x/status/{job_id}"
        start_time = time.time()
        
        while (time.time() - start_time) < max_wait_time:
            try:
                response = requests.get(status_url, headers=self.headers, timeout=30)
                response.raise_for_status()
                status_data = response.json()
                
                status = status_data.get("status")
                logger.info(f"Job status: {status}")
                
                if status == "COMPLETED":
                    output = status_data.get("output", {})
                    logger.info("Job completed successfully")
                    return self._transform_runpod_response(output)
                elif status == "FAILED":
                    error_msg = status_data.get("error", "Unknown error")
                    logger.error(f"Job failed: {error_msg}")
                    raise Exception(f"Runpod job failed: {error_msg}")
                elif status in ["IN_QUEUE", "IN_PROGRESS"]:
                    logger.info(f"Job still processing... waiting {poll_interval} seconds")
                    time.sleep(poll_interval)
                else:
                    logger.warning(f"Unknown job status: {status}")
                    time.sleep(poll_interval)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Error polling job status: {str(e)}")
                time.sleep(poll_interval)
        
        raise Exception(f"Job timed out after {max_wait_time} seconds")
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a Runpod job.
        
        Args:
            job_id: The job ID to check
            
        Returns:
            Dictionary containing job status information
        """
        try:
            status_url = f"https://api.runpod.ai/v2/n8j2ln49qh2n4x/status/{job_id}"
            response = requests.get(status_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting job status: {str(e)}")
            raise Exception(f"Error getting job status: {str(e)}")
    
    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        """
        Get the result of a completed Runpod job.
        
        Args:
            job_id: The job ID to get results for
            
        Returns:
            Dictionary containing transcription results in Whisper format
        """
        try:
            status_data = self.get_job_status(job_id)
            
            if status_data.get("status") == "COMPLETED":
                output = status_data.get("output", {})
                return self._transform_runpod_response(output)
            elif status_data.get("status") == "FAILED":
                error_msg = status_data.get("error", "Unknown error")
                raise Exception(f"Job failed: {error_msg}")
            else:
                return {
                    "status": status_data.get("status"),
                    "job_id": job_id,
                    "completed": False
                }
        except Exception as e:
            logger.error(f"Error getting job result: {str(e)}")
            raise
    
    def _transform_runpod_response(self, runpod_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Runpod response format to match local Whisper response format.
        
        Args:
            runpod_result: Response from Runpod API
            
        Returns:
            Dictionary in Whisper format with 'text' and 'segments' keys
        """
        try:
            # Extract the main transcription text
            text = runpod_result.get('transcription', '')
            
            # Extract segments
            segments = runpod_result.get('segments', [])
            
            # Transform segments to match Whisper format
            whisper_segments = []
            for segment in segments:
                whisper_segment = {
                    'id': segment.get('id', 0),
                    'start': segment.get('start', 0.0),
                    'end': segment.get('end', 0.0),
                    'text': segment.get('text', ''),
                    'words': []  # Runpod doesn't provide word-level timestamps by default
                }
                
                # If word-level data exists in the future, we can enhance this
                # For now, we generate approximate word timestamps if needed
                if segment.get('text'):
                    words_list = segment['text'].strip().split()
                    if words_list:
                        segment_duration = segment.get('end', 0.0) - segment.get('start', 0.0)
                        word_duration = segment_duration / len(words_list) if len(words_list) > 0 else 0.0
                        
                        for i, word in enumerate(words_list):
                            word_start = segment.get('start', 0.0) + (i * word_duration)
                            word_end = word_start + word_duration
                            
                            whisper_segment['words'].append({
                                'word': f' {word}',  # Whisper format includes leading space
                                'start': word_start,
                                'end': word_end,
                                'probability': 0.8  # Default probability since we don't have actual data
                            })
                
                whisper_segments.append(whisper_segment)
            
            # Create the final result in Whisper format
            whisper_result = {
                'text': text,
                'segments': whisper_segments,
                'language': runpod_result.get('detected_language', 'en')
            }
            
            logger.info(f"Transformed Runpod response: {len(whisper_segments)} segments, language: {whisper_result['language']}")
            logger.info(f"Generated approximate word timestamps for {sum(len(seg['words']) for seg in whisper_segments)} words")
            
            return whisper_result
            
        except Exception as e:
            logger.error(f"Error transforming Runpod response: {str(e)}")
            raise Exception(f"Error transforming Runpod response: {str(e)}")

# Global instance for easy access
runpod_client = RunpodWhisperClient()

def transcribe_with_runpod(audio_url: str, model: str = "large-v3", language: Optional[str] = None, webhook_url: Optional[str] = None, initial_prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to transcribe audio using Runpod.
    
    Args:
        audio_url: URL of the audio/video file to transcribe
        model: Whisper model to use (default: "large-v3")
        language: Language code for transcription (optional)
        webhook_url: Webhook URL for async processing (optional)
    
    Returns:
        Dictionary containing transcription results in Whisper format
        or job information if webhook is provided
    """
    return runpod_client.transcribe_audio(audio_url, model, language, webhook_url, initial_prompt="")

def get_runpod_job_status(job_id: str) -> Dict[str, Any]:
    """
    Get the status of a Runpod job.
    
    Args:
        job_id: The job ID to check
        
    Returns:
        Dictionary containing job status information
    """
    return runpod_client.get_job_status(job_id)

def get_runpod_job_result(job_id: str) -> Dict[str, Any]:
    """
    Get the result of a completed Runpod job.
    
    Args:
        job_id: The job ID to get results for
        
    Returns:
        Dictionary containing transcription results in Whisper format
    """
    return runpod_client.get_job_result(job_id)
