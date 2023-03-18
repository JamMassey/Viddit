import cv2
import numpy as np
from moviepy.editor import AudioFileClip, concatenate_videoclips
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
import logging

logger = logging.getLogger(__name__)

WAIT_TIME_SECONDS=2
def generate_video_from_content(background_video_path, png_paths, audio_paths, output_name="output.mp4"):
    # Open the background video file
    cap = cv2.VideoCapture(background_video_path)

    # Get the video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    logger.debug(f'Video properties: {fps} fps, {width}x{height} pixels')
    clips = []
    for i in range(len(png_paths)):
        # Read the PNG image to be overlayed
        png = cv2.imread(png_paths[i], cv2.IMREAD_UNCHANGED)
        
        # Calculate the total number of frames to display the PNG image using the audio duration
        audio_clip = AudioFileClip(audio_paths[i])
        expected_duration = audio_clip.duration + WAIT_TIME_SECONDS
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

        logger.debug(f'Overlaying PNG image {i} for {num_frames} frames')
        for i in range(num_frames): # Each one of these complete loop completions is a clip associated with a single image/audio pair
            ret, frame = cap.read()
            if ret:
                # Extract the RGB channels of the video frame
                frame_rgb = frame[:, :, :3]

                # Multiply the PNG RGB channels with the alpha mask and add them to the frame RGB channels
                frame_rgb[y:y+png_height, x:x+png_width] = (1 - alpha_mask[:, :, np.newaxis]) * frame_rgb[y:y+png_height, x:x+png_width] + alpha_mask[:, :, np.newaxis] * png_rgb


                # Add the frame to the list of frames
                frames.append(frame_rgb) 
            else:
                break
        #create_video(f"temp_{str(i)}.mp4")
        video_clip = ImageSequenceClip(frames, fps=fps).set_audio(audio_clip)
        clips.append(video_clip)
    result_clip = concatenate_videoclips(clips)
    result_clip.write_videofile(output_name)

def create_video(frames, output, fps=30):
    # Get the shape of the frames
    height, width, _ = frames[0].shape

    # Create the video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Set the video codec
    out = cv2.VideoWriter(output, fourcc, fps, (width, height))

    # Write each frame to the video
    for frame in frames:
        out.write(frame)

    # Release the video writer
    out.release()