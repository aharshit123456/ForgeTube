<a>
  <h1 align="center"> MLSA Project Wing: ML </h1>
</a>
<p align="center"> <img src="https://avatars.githubusercontent.com/u/79008924?s=280&v=4">
</p>


# ForgeTube Video Assembler
The current video assembler, built using **`MoviePy`** (which relies on **`FFmpeg`** for video processing), takes all images from the ***Images*** folder and all audio files from the** *Audio*** folder and combines them into a single video. Each image is displayed for the exact duration of its corresponding audio file, ensuring perfect synchronisation between visuals and sound.  

Both images and audio files are sorted alphabetically before being compiled in sequence. To maintain the correct order, it is recommended to name the files numerically (e.g., `01.jpg`, `01.mp3`, `02.jpg`, `02.mp3`, etc.).

## Salient features:
- **Automatic Subtitles** : If the `create_video` function is called with the `with_subtitle` argument set to `True` then subtitles will be embedded into the video. Subtitles are grabbed from the `json` file containing the `audio` and `visual script`.
  
  Additionally an `.srt` file is also created so that video players can use the file to add subtitles manually for flexibility.
- **Transition effects clip to clip**: A small fade in and fade out effect is added when switching from clip to clip.
- **Intro and Outro Clips:** An intro clip of 5 seconds showcasing the video title is automatically added followed by an outro clip at the end.

## Get started 
1. Clone the repo on your system.
2. create a python virtual environment.
3. Install the following dependencies :

Install MoviePy via `pip install moviepy>=2.1.2`.

Install FFmpeg from [here](https://www.ffmpeg.org/download.html)

Install PySrt `via pip install pysrt>=1.1.2`.


## Project Structure
```
├───Moviepy Showcase : Contains a simple script showcasing different features of moviepy and how it works
│   └───resources
│       └───font
├───Samples : Contains various different media for testing
|   ├───Audio
│   │   ├───.mp4
│   │   ├───.wav
│   │   └───Deep Space
│   ├───font
│   ├───Images
│   │   ├───Cats New
│   │   ├───Cats Old
│   │   └───Deep Space
│   │   ├───.mp4
│   │   └───.wav
│   ├───raw : Contains individual clips so that they can be used for other purposes.
│   ├───Subtitles
|   |   ├───.srt
│   │   └───.txt
│   ├───templates : Contains Mock scripts for testing
│   └───videos : Output videos are stored in this folder
└───Video Assembly : Contains the custom video assembler script
```


> [!IMPORTANT]
> Replace the following folders with your own folders for testing

```py
image_folder = "Samples/Images/Deep Space"  
audio_folder = "Samples/Audio/Deep Space/"  
script_path = "Samples/templates/mock_script 4.json" 
sub_output_file = "samples/subtitles/.srt/Deep Space.srt"
output_file = f"Samples/Videos/Deep Space.mp4"
```

## Coming soon
- Multiple images for the same audio stream
- Support for video clips
- Faster Image generation
