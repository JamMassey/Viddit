import logging
import os
import cv2
import numpy as np
from moviepy.editor import AudioFileClip, concatenate_videoclips
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
import random

logger = logging.getLogger(__name__)

def generate_video_from_content(background_video_path, png_paths, audio_paths, output_name="output.mp4", wait_time=2):
    # Check background video exists
    if not os.path.exists(background_video_path):
        raise FileNotFoundError(f"Background video {background_video_path} does not exist.")
    
    # Open the background video file
    cap = cv2.VideoCapture(background_video_path)
    logger.info(f"Generating video from {len(png_paths)} images and {len(audio_paths)} audio files")
    # Get the video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    logger.debug(f"Video properties: {fps} fps, {width}x{height} pixels")


    all_audio = [AudioFileClip(audio_path) for audio_path in audio_paths]
    total_audio_duration = sum([audio.duration for audio in all_audio]) + len(audio_paths) * wait_time
    total_video_duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        
    # Choose a random starting point for the background video
    max_start_time = total_video_duration - total_audio_duration
    if max_start_time > 0:
        random_start_time = random.uniform(0, max_start_time)
    else:
        random_start_time = 0
    # Set the starting frame for the background video
    start_frame = int(random_start_time * cap.get(cv2.CAP_PROP_FPS))
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
    clips = []
    total_frames = 0
    for j in range(len(png_paths)):
        # Read the PNG image to be overlayed
        png = cv2.imread(png_paths[j], cv2.IMREAD_UNCHANGED)

        # Calculate the total number of frames to display the PNG image using the audio duration
        audio_clip = all_audio[j]
        expected_duration = all_audio[j].duration + wait_time
        num_frames = int(expected_duration * fps)

        # Calculate the coordinates to place the PNG image in the center of the video frame
        png_height, png_width, png_channels = png.shape
        x = int((width - png_width) / 2)
        y = int((height - png_height) / 2)

        # Create a mask for the PNG image alpha channel
        alpha_mask = png[:, :, 3] / 255.0

        # Extract the RGB channels of the PNG image
        png_rgb = png[:, :, :3]
        frames = []
        logger.info(f"Creating clip {j} of {len(png_paths)}, there are {num_frames} frames.")
        for i in range(num_frames):
            logger.debug(f"Frame {str(i)} of {str(num_frames)}")
            ret, frame = cap.read()
            if ret:
                # Overlay the PNG image on the video frame using the alpha mask and NumPy operations
                frame[y:y+png_height, x:x+png_width, :3] = np.where(
                    alpha_mask[..., np.newaxis],
                    png_rgb,
                    frame[y:y+png_height, x:x+png_width, :3]
                )

                # Add the frame to the list of frames
                frames.append(frame)
            else:
                break
        total_frames += len(frames)

        # create_video(f"temp_{str(i)}.mp4")
        video_clip = ImageSequenceClip(frames, fps=fps).set_audio(all_audio[j])
        clips.append(video_clip)
        del video_clip
    del all_audio
    logger.info(f"Concatenating clips and writing file to {output_name}, expected length: {str(total_frames / fps)} seconds")
    result_clip = concatenate_videoclips(clips)
    result_clip.write_videofile(output_name)
    result_clip.close()
    cap.release()
    del cap
    del result_clip
    del clips




def create_video(frames, output, fps=30):
    # Get the shape of the frames
    height, width, _ = frames[0].shape

    # Create the video writer
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Set the video codec
    out = cv2.VideoWriter(output, fourcc, fps, (width, height))

    # Write each frame to the video
    for frame in frames:
        out.write(frame)

    # Release the video writer
    out.release()
