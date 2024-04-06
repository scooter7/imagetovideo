import streamlit as st
from PIL import Image
import numpy as np
from moviepy.editor import ImageSequenceClip, AudioFileClip, CompositeAudioClip
import io
import tempfile

def generate_video_from_images(image_files, fps=1, duration_per_image=3):
    images = []
    for img_file in image_files:
        img = Image.open(img_file)
        img = img.resize((640, 480))  # Resize image to 640x480
        img_np = np.array(img)  # Convert PIL image to numpy array
        images.append(img_np)
    # Create a video clip from the sequence of images
    video = ImageSequenceClip(images, fps=fps)
    return video.set_duration(duration_per_image * len(image_files))

def add_audio_to_video(video, speech_audio=None, background_audio=None):
    if speech_audio and background_audio:
        # Use tempfile to create a temporary file on disk to bypass MoviePy's limitation
        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as tmp_speech, tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as tmp_background:
            tmp_speech.write(speech_audio.getvalue())
            tmp_background.write(background_audio.getvalue())
            speech_clip = AudioFileClip(tmp_speech.name)
            background_clip = AudioFileClip(tmp_background.name).volumex(0.1)  # Reduce volume of background
            composite_audio = CompositeAudioClip([speech_clip, background_clip.set_duration(speech_clip.duration)])
            final_video = video.set_audio(composite_audio)
            return final_video
    else:
        return video  # Return the original video if no audio is provided

st.title('Video Generator App')

uploaded_images = st.file_uploader("Upload Images", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
uploaded_speech = st.file_uploader("Upload Speech Audio (MP3)", type=['mp3'], accept_multiple_files=False)
uploaded_background = st.file_uploader("Upload Background Audio (MP3)", type=['mp3'], accept_multiple_files=False)

if st.button('Generate Video') and uploaded_images:
    video = generate_video_from_images(uploaded_images, duration_per_image=3)
    if uploaded_speech and uploaded_background:
        final_video = add_audio_to_video(video, uploaded_speech, uploaded_background)
    else:
        final_video = video  # Use the video without audio if no audio files were uploaded
    
    # Save final video to a temporary file to display in Streamlit and offer for download
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as final_video_file:
        final_video.write_videofile(final_video_file.name, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio.m4a", remove_temp=True, fps=24)
        st.video(final_video_file.name)
        with open(final_video_file.name, "rb") as file:
            st.download_button(
                label="Download Video",
                data=file,
                file_name="final_video.mp4",
                mime="video/mp4"
            )
else:
    st.error("Please upload the required images.")
