import json
# from datetime import datetime, timedelta

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

# # Calculating the end timestamp of the subtitle
# def calculate_endtimestamp(start_time, duration):
#     start_dt = datetime.strptime(start_time, "%M:%S")
#     end_dt = start_dt + timedelta(seconds=duration)
#     return end_dt.strftime("%M:%S")

# # Calculating the duration of the subtitle
# def calculate_duration(text, speed):
#     words_per_minute = 150  # Average speaking rate
#     words = len(text.split())
#     duration = (words / words_per_minute) * 60 / speed
#     return duration

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

json_path = "samples/templates/mock_script.json"
topic = extract_topic_from_json(json_path)
audio_data = json_extract(json_path)
print(topic, audio_data)