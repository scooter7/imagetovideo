import streamlit as st
from PIL import Image
import numpy as np
from moviepy.editor import ImageSequenceClip, CompositeAudioClip, AudioFileClip, concatenate_videoclips
import tempfile

def resize_and_pad(img, size, pad_color=(255, 255, 255)):
    img.thumbnail(size, Image.Resampling.LANCZOS)
    background = Image.new('RGB', size, pad_color)
    img_w, img_h = img.size
    bg_w, bg_h = size
    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
    background.paste(img, offset)
    return np.array(background)

def generate_video_from_images(image_files, size=(640, 480), duration_per_image=3, fade_duration=1):
    clips = []
    for img_file in image_files:
        img = resize_and_pad(Image.open(img_file), size)
        clip = ImageSequenceClip([img], fps=1)
        clip = clip.set_duration(duration_per_image)
        if fade_duration > 0:
            clip = clip.crossfadein(fade_duration)
        clips.append(clip)
    if fade_duration > 0:
        video = concatenate_videoclips(clips, padding=-fade_duration, method="compose")
    else:
        video = concatenate_videoclips(clips, method="compose")
    return video

def add_audio_to_video(video_clip, speech_audio=None, background_audio=None):
    audio_clips = []
    if speech_audio:
        speech_clip = AudioFileClip(speech_audio).set_duration(video_clip.duration)
        audio_clips.append(speech_clip)
    if background_audio:
        background_clip = AudioFileClip(background_audio).volumex(0.1).set_duration(video_clip.duration)
        audio_clips.append(background_clip)
    
    if audio_clips:
        final_audio = CompositeAudioClip(audio_clips)
        video_clip = video_clip.set_audio(final_audio)
    return video_clip

st.title('Enhanced Video Generator App')

uploaded_images = st.file_uploader("Upload Images", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
image_display_duration = st.slider("Select how many seconds to display each image:", min_value=1, max_value=10, value=3)
add_fades = st.checkbox("Add fade transitions between images", value=True)
fade_duration = 1 if add_fades else 0

uploaded_speech = st.file_uploader("Upload Speech Audio (MP3)", type=['mp3'], accept_multiple_files=False)
uploaded_background = st.file_uploader("Upload Background Audio (MP3)", type=['mp3'], accept_multiple_files=False)

if st.button('Generate Video') and uploaded_images:
    video_clip = generate_video_from_images(uploaded_images, duration_per_image=image_display_duration, fade_duration=fade_duration)

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
        with open(final_video_file.name, "rb") as file:
            file_content = file.read()
            st.download_button(label="Download Video", data=file_content, file_name="final_video.mp4", mime="video/mp4")
else:
    st.error("Please upload the required images.")
