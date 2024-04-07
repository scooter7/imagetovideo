import streamlit as st
from PIL import Image
import numpy as np
from moviepy.editor import concatenate_videoclips, AudioFileClip, CompositeAudioClip
from moviepy.video.VideoClip import ImageClip
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
        clip = ImageClip(img).set_duration(duration_per_image)
        if fade_duration > 0 and len(clips) > 0:  # Apply fade transition if not the first image
            clip = clip.crossfadein(fade_duration)
        clips.append(clip)

    # Adjust duration to include fades
    total_duration = duration_per_image * len(image_files) + fade_duration * (len(image_files) - 1)
    video = concatenate_videoclips(clips, method="compose", padding=-fade_duration if fade_duration > 0 else 0)
    video = video.set_duration(total_duration)

    return video

def add_audio_to_video(video_clip, speech_audio=None, background_audio=None):
    audio_clips = []
    if speech_audio:
        speech_audio.seek(0)  # Reset pointer to start of file
        speech_clip = AudioFileClip(speech_audio.name)
        audio_clips.append(speech_clip)
    if background_audio:
        background_audio.seek(0)  # Reset pointer to start of file
        background_clip = AudioFileClip(background_audio.name).volumex(0.1)
        audio_clips.append(background_clip)
    
    if audio_clips:
        final_audio = CompositeAudioClip(audio_clips).set_duration(video_clip.duration)
        video_clip = video_clip.set_audio(final_audio)
    return video_clip

st.title('Video Generator App')

uploaded_images = st.file_uploader("Upload Images", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
image_display_duration = st.slider("Select how many seconds to display each image:", min_value=1, max_value=10, value=3)
add_fades = st.checkbox("Add fade transitions between images", value=True)
fade_duration = 1 if add_fades else 0

uploaded_speech = st.file_uploader("Upload Speech Audio (MP3)", type=['mp3'], accept_multiple_files=False)
uploaded_background = st.file_uploader("Upload Background Audio (MP3)", type=['mp3'], accept_multiple_files=False)

if st.button('Generate Video') and uploaded_images:
    speech_temp = tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") if uploaded_speech else None
    background_temp = tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") if uploaded_background else None

    if speech_temp:
        speech_temp.write(uploaded_speech.getvalue())
        speech_temp.seek(0)
    if background_temp:
        background_temp.write(uploaded_background.getvalue())
        background_temp.seek(0)

    video_clip = generate_video_from_images(uploaded_images, duration_per_image=image_display_duration, fade_duration=fade_duration)
    video_clip = add_audio_to_video(video_clip, speech_temp, background_temp)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as final_video_file:
        video_clip.write_videofile(final_video_file.name, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio.m4a", remove_temp=True, fps=24)
        st.video(final_video_file.name)
        final_video_file.seek(0)
        st.download_button(label="Download Video", data=final_video_file.read(), file_name="final_video.mp4", mime="video/mp4")
else:
    st.error("Please upload the required images.")
