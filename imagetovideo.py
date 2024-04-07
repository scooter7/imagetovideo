import streamlit as st
from PIL import Image
import numpy as np
from moviepy.editor import ImageSequenceClip, CompositeAudioClip
import io

def resize_and_pad(img, size, pad_color=0):
    """
    Resize PIL image keeping ratio and using white background.
    """
    img.thumbnail(size, Image.ANTIALIAS)
    background = Image.new('RGB', size, (pad_color, pad_color, pad_color))
    img_w, img_h = img.size
    bg_w, bg_h = size
    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
    background.paste(img, offset)
    return np.array(background)

def generate_video_from_images(image_files, size=(640, 480), fps=1, duration_per_image=3):
    images = [resize_and_pad(Image.open(img_file), size) for img_file in image_files]
    video = ImageSequenceClip(images, fps=fps)
    return video.set_duration(duration_per_image * len(image_files))

uploaded_images = st.file_uploader("Upload Images", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
uploaded_speech = st.file_uploader("Upload Speech Audio (MP3)", type=['mp3'], accept_multiple_files=False)
uploaded_background = st.file_uploader("Upload Background Audio (MP3)", type=['mp3'], accept_multiple_files=False)

if st.button('Generate Video') and uploaded_images:
    video = generate_video_from_images(uploaded_images, duration_per_image=3)
    if uploaded_speech and uploaded_background:
        speech_clip = AudioFileClip(uploaded_speech.name)
        background_clip = AudioFileClip(uploaded_background.name).volumex(0.1)
        composite_audio = CompositeAudioClip([speech_clip, background_clip.set_duration(speech_clip.duration)])
        final_video = video.set_audio(composite_audio)
    else:
        final_video = video
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as final_video_file:
        final_video.write_videofile(final_video_file.name, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio.m4a", remove_temp=True, fps=24)
        st.video(final_video_file.name)
        with open(final_video_file.name, "rb") as file:
            st.download_button(label="Download Video", data=file, file_name="final_video.mp4", mime="video/mp4")
else:
    st.error("Please upload the required images.")
