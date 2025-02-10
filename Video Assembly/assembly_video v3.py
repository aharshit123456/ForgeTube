''' 
README : The video assembler takes all the images in the Images folder and all the audio files in the Audio folder and the text-to-script from json file and concatenates 
them into a video. The duration of the picture displayed is same as the duration of the audio for that image. The Images and
Audio files sorted alphabetically and then compiled in that order. It is recommended to store the Audio and Image files by 
numbering them.

Moviepy also supports addition of video clips, so if in future if we have access to video generation it will be useful.

'''
''' MAIN THINGS TODO
1. TODO Implement Subtitles. (Done)
2. TODO: Read json and extract important parameters from it. (Done)
3. TODO: Add support for video clips as well. 
4. TODO: Add the ability to compile multiple images (stored in a folder) for the one audio stream into a single clip. (Shopno )
5. TODO: Add transition from clip to clip.
'''
'''
Additional TODOs
TODO: 1. Add a small delay to ensure smoother transition from clip to clip.
TODO: 2. Experiment with adding Title screen, text and transitions, and other effects.
TODO  3. Test the script against a large number of images with higher resolutions and audio files, document the performance.
TODO: 4. Test the script with various different audio and video extensions and codecs, find the best combination.
WARNING: No testing has been done with .png and .wav audio file formats.
TODO: 5. Allow the script to automatically assign the proper codec with the respective file extension.
TODO: 6. Run proper tests to document when video compiler corruption happens.
'''
import os
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip,TextClip,CompositeVideoClip, vfx
from moviepy.video.tools.subtitles import SubtitlesClip
import pysrt 
import json

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
    
'''
TODO:
1. ADD THE JSON EXTRACTION
2. ADD THE SCRIPT TO THE SUBTITLES
3. IMPLEMENT THE TRANSITIONS AND THE INTRO OUTRO CLIPS.
'''
'''
FIXME Subtitles timings are same and not correct.
FIX Create a single srt file with the correct duration of all the subtitles paired with the respective audio file.
'''
def create_srt(text_file :str, 
            audio_file : AudioFileClip, 
            outfile_name:str,
            duration:int,
            chunk_size=6):
    with open(text_file, "r") as file:
        words = file.read().split()

    word_count = len(words)
    word_duration = audio_file.duration / word_count 
    # Generate subtitle file
    subs = pysrt.SubRipFile()
    start_time = duration 
    # Automatic chunk_size calculation
    # target_duration = 2 # Number of seconds the subtitle is displayed on the screen
    # chunk_size = round(target_duration/word_duration)
    
    

    for i in range(0, word_count, chunk_size):
        end_time = start_time + (chunk_size * word_duration)  

        subtitle = pysrt.SubRipItem(index=len(subs) + 1,
                                    start=pysrt.SubRipTime(seconds=start_time),
                                    end=pysrt.SubRipTime(seconds=end_time),
                                    text=" ".join(words[i:i + chunk_size]))

        subs.append(subtitle)
        start_time = end_time  

    out = f"samples/subtitles/.srt/{outfile_name}.srt"
    subs.save(out)
    return out

'''
extract_topic_from_json extract() takes json file path as input.
- Opens the file as read-only and loads the JSON data from it.
- Extracts the topic from the JSON data.

On success, it returns the topic of the video.
'''
def extract_topic_from_json(file_path):
    try:
        # Open the JSON file
        with open(file_path, 'r') as file:
            # Load JSON data from the file
            data = json.load(file)
            
            # Extract the topic, and audio_script from the JSON data
            topic = data.get('topic', 'No topic found')
            
            return topic
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} contains invalid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

'''
extract_audio_topic_from_json() takes json file path as input.
- Opens the file as read-only and loads the JSON data from it.
- Extracts the audio_script from the JSON data.

On success, it returns audio_script.
'''
def extract_audio_from_json(file_path):
    try:
        # Open the JSON file
        with open(file_path, 'r') as file:
            # Load JSON data from the file
            data = json.load(file)
            
            # Extract the topic, audio_script and visual_script
            topic = data.get('topic', 'No topic found')
            audio_script = data.get('audio_script', [])
            # visual_script = data.get('visual_script', [])

            return audio_script
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} contains invalid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

'''
json_extract() takes json file path as input.
- Calls the extract_audio_from_json() to extract the text-to-speech / subtitles from the json file,
  and the topic of the video.

On success, it returns the subtitles in list format, and the topic.
'''
def json_extract(json_path):
    
    # Extract parameters from json file
    audio_script = extract_audio_from_json(json_path)
    if audio_script:
        # print("Extracted Audio Parameters:")
        audio_data = []
        for item in audio_script:
            if 'text' in item:
                text = item['text']
                audio_data.append(text)
        return audio_data
    else:
        return "No audio script found in the JSON file."

def add_effects(clip):
    """
    Adds a random effect from a curated list to the video clip.
    Parameters:
        clip (VideoClip): Video clip to which effects are to be added.
    Returns:
        VideoClip: Video clip with one random effect applied.
    """
    list_of_effects = [
        # Serious
        [
            vfx.FadeIn(duration=1),
            vfx.FadeOut(duration=1)
        ],
        # # Dramatic
        # [
        #     vfx.CrossFadeIn(duration=1),
        #     vfx.CrossFadeOut(duration=1)
        # ],
        # # Smooth transitions
        # [
        #     vfx.SlideIn(duration=1, side="left"),
        #     vfx.SlideOut(duration=1, side="right")
        # ]
    ]
    
    # Choose a random effect from a random category
    random_effect = random.choice(random.choice(list_of_effects))
    print(random_effect)
    return clip.with_effects([random_effect])

def create_video(image_folder :str, 
                audio_folder : str,
                sub_folder : str,
                font_path : str ,
                output_file : str,
                with_subtitles = False):
    """
    Summary:
    Combines images from a folder and audio files from another folder into a video, using concatenate function, the reason is because 
    the Compose method automatically resizes clips by adding the clip with the largest dimension as the default and adds black bars
    to fill the rest of the clips and maintain aspect ratio.
    
    Args:
    -----
        image_folder (str) : 
            Path to the folder containing images.
        audio_folder (str) : Path to the folder containing audio files.
        sub_folder (str)   : Path to the folder containing subtitle text files.
        font_path (str)    :
        output_file (str)  : Name of the output video file.
        
    Raises:
        FileNotFoundError: If images, audio or subtitles are not detected.
    """

    try:
        images = get_files(image_folder, ('.jpg', '.png'))
        audio_files = get_files(audio_folder, ('.mp3', '.wav'))
        # sub_files = get_files(sub_folder,(".txt"))
        # replace
        sub_files = json_extract(sub_folder)
        
        raw_clips = [] 
        subtitles = []
        
        dur = 0
        i = 0
        
            
        # Create different clips
        for img, audio,subtitle_txt in zip(images,audio_files,sub_files):
            audio_clip = AudioFileClip(audio)
            image_clip = ImageClip(img).with_duration(audio_clip.duration).with_audio(audio_clip)
            
            
            subtitle_srt = create_srt(text_file=subtitle_txt,
                                    outfile_name=(sub_files.index(subtitle_txt)+1),
                                    duration=dur,
                                    audio_file=audio_clip)
            subtitle_clip_gen = lambda text:(TextClip(text=text,
                                    font=font_path, 
                                    color='white', 
                                    bg_color='black', 
                                    size=(1000, 100),
                                    method='caption',
                                    text_align = "center",
                                    horizontal_align = "center",
                                    vertical_align="bottom",
                                    ).with_position(("center", "bottom"))) #.with_duration(audio_clip.duration).with_start(dur)
            subtitle_clip = SubtitlesClip(subtitles=subtitle_srt,
                                        make_textclip=subtitle_clip_gen)
            i += 1
            print(f"Video Clip and Subtitle clip no. {i} successfully created")
            dur += audio_clip.duration
            image_clip = add_effects(image_clip)
            raw_clips.append(image_clip)
            subtitles.append(subtitle_clip)
            
            
        #     Store individual clips without subtitles for preview / debug 
        #     clip = None
        #     clip = CompositeVideoClip([img,sub])
        #     clip.write_videofile(f"samples/raw/{raw_clips.index(image_clip)+1}.mp4",fps = 24,threads = 16)
        
        
        '''
        FIXME: 1. Size of the subtitles are improperly implemented.
        FIX: Make it such that concatenation is done only on the image clips and composite video clip is added later on with the 
        
        FIXME 2. Subtitles are not properly synchronised with the audio.
        FIX : Get the duration data and implement it as such, also segment the subtitles such that speed of the audio clip matches the
        word per minute shown of the audio.
        
        FIXME 3. Subtitles do not appear at the right position in the video. Preferable position is Vertical : bottom, Horizontal = Center,
        '''
        video = concatenate_videoclips(raw_clips, method="compose")
        if with_subtitles == True:
            clips_with_subtitle = []
            clips_with_subtitle.append(video)
            for i in subtitles:
                clips_with_subtitle.append(i)
            final_video = CompositeVideoClip(clips_with_subtitle)
        else:
            final_video = video
        final_video.write_videofile(output_file, fps=1,threads = 16)
        print(f"Video created successfully: {output_file}")
        
    except FileNotFoundError:
        if not images:
            raise FileNotFoundError("No images found in the specified folder.")
        if not audio_files:
            raise FileNotFoundError("No audio files found in the specified folder.")
        if not sub_files:
            raise FileNotFoundError("No subtitles found in the specified folder. ")
        
def create_complete_srt(text_file_folder :str, 
            audio_file_folder : str, 
            outfile_name:str,
            chunk_size=5):
    """
    Creates an SRT file from text and audio files in the given folders.

    Parameters:
    text_file_folder (str): Path to the folder containing text files.
    audio_file_folder (str): Path to the folder containing audio files.
    outfile_name (str): Name of the output SRT file (without extension).
    chunk_size (str): Number of words per subtitle chunk. If set to `sentence` , chunks are automatically segmented sentence wise.

    Returns:
    str: Path to the generated SRT file.
    """
    # text_files = get_files(text_file_folder,(".txt"))
    # replace
    text_files = json_extract(text_file_folder)
    audio_files = get_files(audio_file_folder,(".wav"))
    subs = pysrt.SubRipFile()
    start_time = 0 
    for text_file, audio_file in zip(text_files, audio_files):
        # with open(text_file, "r") as text_file:
            # words = text_file.read().split()
        words = text_file.split()
        audio_clip = AudioFileClip(audio_file)
        
        # Calculate average word duration
        word_count = len(words)
        word_duration = (audio_clip.duration / word_count)  # Seconds per word
        # char_duration = char_count / audio_clip.duration #Characters per second
        if chunk_size != 0:
            for i in range(0, word_count, chunk_size):
                end_time = start_time + (  chunk_size * word_duration)
                subtitle = pysrt.SubRipItem(
                    index=len(subs) + 1,
                    start=pysrt.SubRipTime(seconds=start_time),
                    end=pysrt.SubRipTime(seconds=end_time),
                    text=" ".join(words[i:i + chunk_size])
                )
                subs.append(subtitle)
                start_time = end_time
        elif chunk_size == 0:
            chunk_size = word_count
            end_time = start_time + audio_clip.duration
            subtitle = pysrt.SubRipItem(
                    index=len(subs) + 1,
                    start=pysrt.SubRipTime(seconds=start_time),
                    end=pysrt.SubRipTime(seconds=end_time),
                    text=" ".join(words)
                )
            subs.append(subtitle)
            start_time = end_time


    # for i in range(0, word_count, chunk_size):
    #     end_time = start_time + (chunk_size * word_duration)  

    #     subtitle = pysrt.SubRipItem(index=len(subs) + 1,
    #                                 start=pysrt.SubRipTime(seconds=start_time),
    #                                 end=pysrt.SubRipTime(seconds=end_time),
    #                                 text=" ".join(words[i:i + chunk_size]))

    #     subs.append(subtitle)
    #     start_time = end_time  

    # Save as an SRT subtitle file
    out = f"./samples/subtitles/.srt/{outfile_name}.srt"
    subs.save(out)
    print(f"File saved successfully at {out}")

        
if __name__ == "__main__":
    image_folder = "samples/Images new/"  
    audio_folder = "samples/Audio/.wav/"  
    # sub_folder = "samples/subtitles/.txt/"
    sub_folder = "samples/templates/mock_script 3.json"
    font_path = "Samples/font/font.ttf"
    # mp4 or .mkv
    # output_file = "samples/videos/Cats.mp4"
    topic = extract_topic_from_json(sub_folder)
    output_file = f"samples/videos/{topic}.mp4"
    create_complete_srt(text_file_folder=sub_folder,
                        audio_file_folder=audio_folder,
                        outfile_name="cats v8",
                        chunk_size = 5)
    
    create_video(image_folder, audio_folder,sub_folder,font_path, output_file,with_subtitles=True)
    
