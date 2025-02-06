''' 
README : The video assembler takes all the images in the Images folder and all the audio files in the Audio folder and concatenates 
them into a video. The duration of the picture displayed is same as the duration of the audio for that image. The Images and
Audio files sorted alphabetically and then compiled in that order. It is recommended to store the Audio and Image files by 
numbering them.

Moviepy also supports addition of video clips, so if in future if we have access to video generation it will be useful.

MAIN TODO
1. TODO: Implement Subtitles.
2. TODO: Read json and extract important parameters from it. 
3. TODO: Add support for video clips as well. 
4. TODO: Add the ability to compile multiple images (stored in a folder) for the one audio stream into a single clip. (Shopno )
5. TODO: Add transition from clip to clip.
'''
'''
Additional TODOs
# TODO: 1. Add a small delay to ensure smoother transition from clip to clip.
# TODO: 2. Experiment with adding Title screen, text and transitions, and other effects.
# TODO  3. Test the script against a large number of images with higher resolutions and audio files, document the performance.
# TODO: 4. Test the script with various different audio and video extensions and codecs, find the best combination.
# WARNING: No testing has been done with .png and .wav audio file formats.
# TODO: 5. Allow the script to automatically assign the proper codec with the respective file extension.
# TODO: 6. Run proper tests to document when video compiler corruption happens.
'''
import os
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip

# Function to Read all the files from a folder.
def get_files(folder, extensions):
    """
    Retrieves files with specified extensions from a folder.
    Parameters:
        folder (str): Path to the folder.
        extensions (tuple): File extensions to include (e.g., ('.jpg', '.png')).
    Returns:
        list: List of file paths.
    """
    return [
        os.path.join(folder, file)
        # Files are numbered , so that after sorting they are compiled into the video in that order.
        for file in sorted(os.listdir(folder))  
        if file.lower().endswith(extensions)
    ]

def create_video(image_folder, audio_folder,output_file):
    """
    Combines images from a folder and audio files from another folder into a video.
    Parameters:
        image_folder (str): Path to the folder containing images.
        audio_folder (str): Path to the folder containing audio files.
        output_file (str): Name of the output video file.
    """
    try:
        images = get_files(image_folder, ('.jpg', '.png'))
        audio_files = get_files(audio_folder, ('.mp3', '.wav'))
        clips = []
        
        # Create video clips with image and audio.
        for img, audio in zip(images,audio_files):
            audio_clip = AudioFileClip(audio)
            image_clip = ImageClip(img).with_duration(audio_clip.duration).with_audio(audio_clip)
            clips.append(image_clip)
            
        video = concatenate_videoclips(clips, method="compose")
        video.write_videofile(output_file, fps=24)
        print(f"Video created successfully: {output_file}")
        
    except FileNotFoundError:
        if not images:
            raise FileNotFoundError("No images found in the specified folder.")
        if not audio_files:
            raise FileNotFoundError("No audio files found in the specified folder.")
        
        
if __name__ == "__main__":
    # Replace the folders with the correct folder.
    image_folder = "samples/Images/"  
    audio_folder = "samples/Audio/.wav/"  
    output_file = "samples/video/Cats.mp4" #.mp4 or .mkv works
    create_video(image_folder, audio_folder, output_file)
