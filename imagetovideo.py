import streamlit as st
from PIL import Image
import numpy as np
from moviepy.editor import ImageSequenceClip, CompositeAudioClip, AudioFileClip
import tempfile
from io import BytesIO

def resize_and_pad(img, size, pad_color=(255, 255, 255)):
    img.thumbnail(size, Image.Resampling.LANCZOS)
    background = Image.new('RGB', size, pad_color)
    img_w, img_h = img.size
    bg_w, bg_h = size
    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
    background.paste(img, offset)
    return np.array(background)

def generate_video_from_images(image_files, size=(640, 480), fps=1, duration_per_image=3):
    images = [resize_and_pad(Image.open(img_file), size) for img_file in image_files]
    video = ImageSequenceClip(images, fps=fps)
    return video.set_duration(duration_per_image * len(images))

def add_audio_to_video(video_clip, speech_audio=None, background_audio=None):
    if speech_audio and background_audio:
        speech_clip = AudioFileClip(speech_audio)
        background_clip = AudioFileClip(background_audio).volumex(0.1)
        final_audio = CompositeAudioClip([background_clip, speech_clip.set_start(0).set_duration(video_clip.duration)])
        video_clip = video_clip.set_audio(final_audio)
    return video_clip

st.title('Video Generator App')

uploaded_images = st.file_uploader("Upload Images", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
uploaded_speech = st.file_uploader("Upload Speech Audio (MP3)", type=['mp3'], accept_multiple_files=False)
uploaded_background = st.file_uploader("Upload Background Audio (MP3)", type=['mp3'], accept_multiple_files=False)

if st.button('Generate Video') and uploaded_images:
    video_clip = generate_video_from_images(uploaded_images, duration_per_image=3)

    if uploaded_speech and uploaded_background:
        with tempfile.NamedTemporaryFile(delete=True, suffix='.mp3') as speech_tempfile, tempfile.NamedTemporaryFile(delete=True, suffix='.mp3') as background_tempfile:
            speech_tempfile.write(uploaded_speech.getvalue())
            background_tempfile.write(uploaded_background.getvalue())
            speech_tempfile.seek(0)
            background_tempfile.seek(0)
            video_clip = add_audio_to_video(video_clip, speech_tempfile.name, background_tempfile.name)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as final_video_file:
        video_clip.write_videofile(final_video_file.name, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio.m4a", remove_temp=True, fps=24)
        st.video(final_video_file.name)
        # Fix: Open the file in binary read mode and pass the content to st.download_button
        with open(final_video_file.name, "rb") as file:
            file_content = file.read()
            st.download_button(label="Download Video", data=file_content, file_name="final_video.mp4", mime="video/mp4")
else:
    st.error("Please upload the required images.")
