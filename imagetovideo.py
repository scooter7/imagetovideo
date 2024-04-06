import streamlit as st
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import os
import tempfile

# Function to generate video from images
def generate_video_from_images(image_files, frame_rate=45, video_width=640, video_height=480, image_display_duration=3000, transition_duration=50):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_video = cv2.VideoWriter(temp_video_file.name, fourcc, frame_rate, (video_width, video_height))
        
        for i in range(len(image_files) - 1):
            image1 = cv2.imdecode(np.frombuffer(image_files[i].getvalue(), np.uint8), cv2.IMREAD_COLOR)
            image2 = cv2.imdecode(np.frombuffer(image_files[i + 1].getvalue(), np.uint8), cv2.IMREAD_COLOR)
            
            image1 = cv2.resize(image1, (video_width, video_height))
            image2 = cv2.resize(image2, (video_width, video_height))
            
            for _ in range(int(image_display_duration * frame_rate / 1000)):
                output_video.write(np.uint8(image1))
            
            for frame in range(transition_duration + 1):
                alpha = frame / transition_duration
                blended = cv2.addWeighted(image1, 1 - alpha, image2, alpha, 0)
                output_video.write(np.uint8(blended))
                
        output_video.release()
        return temp_video_file.name

# Function to add audio to video
def add_audio_to_video(video_path, speech_audio, background_audio):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as final_video_file:
        video_clip = VideoFileClip(video_path)
        speech_audio_clip = AudioFileClip(speech_audio.name)
        background_audio_clip = AudioFileClip(background_audio.name)

        # Ensure the audio matches the video length
        video_duration = video_clip.duration
        speech_audio_clip = speech_audio_clip.subclip(0, video_duration)
        background_audio_clip = background_audio_clip.subclip(0, video_duration).volumex(3.0)

        # Combine the audio clips
        final_audio = CompositeAudioClip([background_audio_clip, speech_audio_clip.volumex(0.1)])
        final_clip = video_clip.set_audio(final_audio)
        final_clip.write_videofile(final_video_file.name, codec="libx264", audio_codec="aac")
        
        return final_video_file.name

# Streamlit UI
st.title('Video Generator App')

uploaded_images = st.file_uploader("Upload Images", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
uploaded_speech = st.file_uploader("Upload Speech Audio (MP3)", type=['mp3'])
uploaded_background = st.file_uploader("Upload Background Audio (MP3)", type=['mp3'])

if st.button('Generate Video'):
    if uploaded_images and uploaded_speech and uploaded_background:
        # Generate video from images
        video_path = generate_video_from_images(uploaded_images)
        
        # Add audio to video
        final_video_path = add_audio_to_video(video_path, uploaded_speech, uploaded_background)
        
        # Display the result or provide a download link
        st.video(final_video_path)
        with open(final_video_path, "rb") as file:
            btn = st.download_button(
                label="Download video",
                data=file,
                file_name="final_video.mp4",
                mime="video/mp4"
            )
    else:
        st.error("Please upload the required images and audio files.")
