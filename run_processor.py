"""
Main script to run the video processor with simulated feeds
"""
import asyncio
import cv2
import numpy as np
from services.video_processor import VideoProcessor
from services.video_simulator import VideoSimulator
import requests
import config
import random


async def process_frame_callback(camera_id: str, result: dict, frame: np.ndarray):
    """Callback to send analysis results to API"""
    try:
        # Send to API
        response = requests.post(
            f"http://localhost:8000/api/analysis/{camera_id}",
            json=result,
            timeout=1
        )
    except Exception as e:
        print(f"Error sending analysis for {camera_id}: {e}")


def make_callback(cam_id: str):
    """Create a callback function for a specific camera"""
    async def callback(result: dict, frame: np.ndarray):
        await process_frame_callback(cam_id, result, frame)
    return callback


async def main():
    """Main processing loop"""
    processor = VideoProcessor()
    
    # Create simulators for each camera
    simulators = {}
    for camera_id in config.CAMERAS.keys():
        simulator = VideoSimulator(width=640, height=480)
        simulators[camera_id] = simulator
        
        # Create a temporary video file for each camera
        video_path = f"data/{camera_id}_feed.mp4"
        print(f"Creating simulated video for {camera_id}...")
        simulator.create_video_file(video_path, duration_seconds=300, fps=10)
        
        # Add camera to processor
        processor.add_camera(camera_id, video_path)
        
        # Set callback
        processor.set_frame_callback(camera_id, make_callback(camera_id))
    
    print("Starting video processing...")
    print("Press Ctrl+C to stop")
    
    try:
        await processor.start_processing()
    except KeyboardInterrupt:
        print("\nStopping processor...")
        processor.stop_processing()
        print("Processor stopped.")


if __name__ == "__main__":
    asyncio.run(main())
