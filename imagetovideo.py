import streamlit as st
from PIL import Image
from moviepy.editor import VideoClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
import numpy as np
import io

def generate_video_from_images(image_files, fps=30, duration_per_image=3):
    clips = []
    for img_file in image_files:
        img = Image.open(img_file)
        img = img.resize((640, 480))  # Resize image to 640x480
        img_np = np.array(img)  # Convert PIL image to numpy array
        clip = VideoClip(lambda t: img_np, duration=duration_per_image)  # Create a clip for each image
        clips.append(clip)
    video = concatenate_videoclips(clips, method="compose")
    return video

def add_audio_to_video(video, speech_audio, background_audio):
    speech_clip = AudioFileClip(speech_audio.name)
    background_clip = AudioFileClip(background_audio.name).volumex(0.1)  # Reduce volume of background
    composite_audio = CompositeAudioClip([speech_clip, background_clip.set_duration(speech_clip.duration)])
    final_video = video.set_audio(composite_audio)
    return final_video

st.title('Video Generator App')

uploaded_images = st.file_uploader("Upload Images", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
uploaded_speech = st.file_uploader("Upload Speech Audio (MP3)", type=['mp3'])
uploaded_background = st.file_uploader("Upload Background Audio (MP3)", type=['mp3'])

if st.button('Generate Video') and uploaded_images and uploaded_speech and uploaded_background:
    video = generate_video_from_images(uploaded_images)
    final_video = add_audio_to_video(video, uploaded_speech, uploaded_background)
    
    # Save final video to a temporary file to display in Streamlit and offer for download
    with io.BytesIO() as video_file:
        final_video.write_videofile(video_file.name, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio.m4a", remove_temp=True, fps=24)
        video_file.seek(0)
        st.video(video_file)
        video_file.seek(0)
        st.download_button(
            label="Download Video",
            data=video_file,
            file_name="final_video.mp4",
            mime="video/mp4"
        )
else:
    st.error("Please upload the required images and audio files.")
