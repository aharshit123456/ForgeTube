''' 
README : The video assembler takes all the images in the Images folder and all the audio files in the Audio folder and concatenates 
them into a video. The duration of the picture displayed is same as the duration of the audio for that image. The Images and
Audio files sorted alphabetically and then compiled in that order. It is recommended to store the Audio and Image files by 
numbering them.

Moviepy also supports addition of video clips, so if in future if we have access to video generation it will be useful.

'''
''' MAIN TODO
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
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip,TextClip,CompositeVideoClip

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

def create_video(image_folder, audio_folder,sub_folder,font_path ,output_file):
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
        sub_files = get_files(sub_folder,(".txt"))
        raw_clips = []
        subtitles = []
        
        dur = 0
        i = 0
        # print(list(zip(images, audio_files,sub_files)))
        # Create different clips
        for img, audio, subtitle in zip(images,audio_files,sub_files):
            audio_clip = AudioFileClip(audio)
            image_clip = ImageClip(img).with_duration(audio_clip.duration).with_audio(audio_clip)
            subtitle_clip = TextClip(filename=subtitle,
                                    font=font_path, 
                                    font_size=50, 
                                    color='white', 
                                    bg_color='black', 
                                    size=(1000, 100)).with_position(("center", "bottom")).with_duration(audio_clip.duration)
            dur += audio_clip.duration
            raw_clips.append(image_clip)
            subtitles.append(subtitle_clip)
            
            # raw_clips.append([image_clip,subtitle_clip])
        
        '''
        README: 
        1. Create Individual clips with subtitles so that they can composed into one video later
        2. Combine all individual clips into one video, using concatenate method, the reason is because the Compose method automatically 
        resizes clips by adding the clip with the largest dimension as the default and adds black bars to fill to fil the rest of the clips.
        FIXME: 
        1. Subtitles are not properly synchronised with the audio.
        2. Size of the subtitles are improperly implemented.
        FIX: Make it such that concatenation is done only on the image clips and composite video clip is added later on with the 
        subtitles having proper synchronisation.
        '''
        clip = None
        clips_with_subtitle = []
        # cn = 0
        # for i in raw_clips:
        #     cn += 1
        #     img = i[0]
        #     sub = i[1]
        #     print(f"Starting raw clip no. {cn} ..... ")
        #     clip = CompositeVideoClip([img,sub])
        #     # Store individual clips for preview / debug
        #     # clip.write_videofile(f"samples/raw/{raw_clips.index(i)+1}.mp4",fps = 24,threads = 16)
        #     print(f"Clip no. {cn} finished !")
        #     clips_with_subtitle.append(clip)
        
        
        
        
        final_video = None
        video = concatenate_videoclips(raw_clips, method="compose")
        for i in subtitle_clip:
            final_video = CompositeVideoClip(video,i)
        final_video.write_videofile(output_file, fps=24)
        print(f"Video created successfully: {output_file}")
        
    except FileNotFoundError:
        if not images:
            print("No images found in the specified folder.")
        if not audio_files:
            raise FileNotFoundError("No audio files found in the specified folder.")
        if not sub_files:
            raise FileNotFoundError("No subtile found in the specified folder. ")
        
        
if __name__ == "__main__":
    image_folder = "samples/Images/"  
    audio_folder = "samples/Audio/.wav/"  
    sub_folder = "samples/subtitles/"
    font_path = "Samples/font/font.ttf"
    # mp4 or .mkv
    output_file = "samples/Cats.mp4"
    create_video(image_folder, audio_folder,sub_folder,font_path, output_file)
