import json
import re
import google.generativeai as genai
from typing import Dict, List, Optional
from serpapi import GoogleSearch

class VideoScriptGenerator:
    def __init__(self, api_key: str, serp_api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
        self.serp_api_key = serp_api_key
        self.system_prompt_initial = """You are a professional video script generator for educational and marketing content.  Your task is to generate a detailed outline and initial draft for a video script, focusing on content and structure, *but not yet segmented into precise timestamps*.  Provide the core narration text and visual descriptions, which will be refined later.

        Output a JSON structure with these keys, but *without timestamps, speed, pitch, or detailed visual parameters* (these will be added in a later stage):

        {
            "topic": "Topic Name",
            "overall_narrative": "A concise summary of the entire video's storyline.",
            "key_sections": [
                {
                    "section_title": "Descriptive title for this section",
                    "narration_text": "The complete text to be spoken in this section.",
                    "visual_description": "A general description of the visuals for this section (e.g., 'Animation showing neural network layers', 'Footage of a doctor using medical imaging software')."
                }
            ]
        }
        """

        self.system_prompt_segmentation = """You are a professional video script segmenter.  Your task is to take an existing video script draft (provided in JSON format) and break it down into precise, timestamped segments for both audio and visuals, adhering to strict formatting and parameter guidelines.

        Input JSON Structure (from previous stage):

        {
            "topic": "Topic Name",
            "overall_narrative": "...",
            "key_sections": [
                {
                    "section_title": "...",
                    "narration_text": "...",
                    "visual_description": "..."
                }
            ]
        }
        
        Output JSON Structure (with all required fields):

        {
            "topic": "Topic Name",
            "description": "description of video"
            "audio_script": [{
                "timestamp": "00:00",
                "text": "Narration text",
                "speaker": "default|narrator_male|narrator_female",
                "speed": 0.9-1.1,
                "pitch": 0.9-1.2,
                "emotion": "neutral|serious|dramatic|mysterious|informative"
            }],
            "visual_script": [{
                "timestamp_start": "00:00",
                "timestamp_end": "00:05",
                "prompt": "Detailed Stable Diffusion prompt",
                "negative_prompt": "Low quality elements to avoid",
                "style": "realistic|cinematic|hyperrealistic|fantasy|scientific",
                "guidance_scale": 11.0-14.0,
                "steps": 50-100,
                "seed": 6-7 digit integer,
                "width": 1024,
                "height": 576
            }]
        }

        Rules for Segmentation:
        
        1. Break down the `narration_text` and `visual_description` from the input JSON into smaller segments, each approximately 5-10 seconds long.
        2. Generate timestamps ("00:00", "00:05", "00:10", etc.) for each segment in both `audio_script` and `visual_script`.
        3.  Maintain strict synchronization:  The `timestamp` values *must* be identical for corresponding audio and visual segments.
        4.  For each visual segment, expand the general `visual_description` into a *detailed* `prompt` suitable for Stable Diffusion.  Include a corresponding `negative_prompt`.
        5.  Choose appropriate values for `speaker`, `speed`, `pitch`, and `emotion` for each audio segment.
        6.  Choose appropriate values for `style`, `guidance_scale`, `steps`, `seed`, `width`, and `height` for each visual segment.
        7. Ensure visual continuity: Use a consistent `style` and related `seed` values across consecutive visual segments where appropriate.  Vary the seed to introduce changes, but maintain a logical flow.
        8.  Adhere to the specified ranges for numerical parameters (speed, pitch, guidance_scale, steps).
        9. Validate JSON structure before output
     ex1_json = {
  "topic": "How to Drive a Car",
  "description": "A step-by-step guide on driving a car safely and confidently.",
  "audio_script": [
      {
      "timestamp": "00:00",
      "text": "Driving a car is an essential skill that requires focus, patience, and practice.",
      "speaker": "narrator_male",
      "speed": 1.0,
      "pitch": 1.0,
      "emotion": "neutral"
      },
      {
      "timestamp": "00:05",
      "text": "Before starting the car, adjust your seat, mirrors, and ensure your seatbelt is fastened.",
      "speaker": "narrator_female",
      "speed": 1.0,
      "pitch": 1.1,
      "emotion": "informative"
      },
      {
      "timestamp": "00:15",
      "text": "Turn the ignition key or press the start button while keeping your foot on the brake.",
      "speaker": "narrator_male",
      "speed": 0.95,
      "pitch": 1.0,
      "emotion": "calm"
      },
      {
      "timestamp": "00:20",
      "text": "Slowly release the brake and gently press the accelerator to move forward.",
      "speaker": "narrator_female",
      "speed": 1.1,
      "pitch": 1.0,
      "emotion": "guiding"
      },
      {
      "timestamp": "00:25",
      "text": "Use the steering wheel to navigate while maintaining a steady speed.",
      "speaker": "narrator_male",
      "speed": 1.0,
      "pitch": 1.0,
      "emotion": "calm"
      }
  ],
  "visual_script": [
      {
      "timestamp_start": "00:00",
      "timestamp_end": "00:05",
      "prompt": "A person sitting in the driver's seat of a modern car, gripping the steering wheel and looking ahead. The dashboard is visible with standard controls.",
      "negative_prompt": "blurry, unrealistic interior, poor lighting",
      "style": "realistic",
      "guidance_scale": 11.5,
      "steps": 50,
      "seed": 123456,
      "width": 1024,
      "height": 576,
      "strength": 0.75
      },
      {
      "timestamp_start": "00:05",
      "timestamp_end": "00:15",
      "prompt": "A close-up of a driver's hands adjusting the side mirrors and fastening the seatbelt inside a well-lit car interior.",
      "negative_prompt": "cluttered background, distorted perspective",
      "style": "cinematic",
      "guidance_scale": 12.0,
      "steps": 60,
      "seed": 654321,
      "width": 1024,
      "height": 576,
      "strength": 0.8
      },
      {
      "timestamp_start": "15:00",
      "timestamp_end": "00:20",
      "prompt": "A driver's hand turning the ignition key or pressing the start button in a modern car with a digital dashboard.",
      "negative_prompt": "low detail, unrealistic lighting, old car model",
      "style": "hyperrealistic",
      "guidance_scale": 12.5,
      "steps": 70,
      "seed": 789101,
      "width": 1024,
      "height": 576,
      "strength": 0.85
      },
      {
      "timestamp_start": "00:20",
      "timestamp_end": "00:25",
      "prompt": "A slow-motion shot of a car's foot pedals as the driver releases the brake and presses the accelerator.",
      "negative_prompt": "blurry, cartoonish, extreme close-up",
      "style": "cinematic",
      "guidance_scale": 11.5,
      "steps": 75,
      "seed": 222333,
      "width": 1024,
      "height": 576,
      "strength": 0.8
      },
      {
      "timestamp_start": "00:25",
      "timestamp_end": "00:30",
      "prompt": "A wide-angle shot of a car moving smoothly on a suburban road, the driver confidently steering the wheel.",
      "negative_prompt": "chaotic traffic, bad weather, motion blur",
      "style": "realistic",
      "guidance_scale": 13.0,
      "steps": 50,
      "seed": 987654,
      "width": 1024,
      "height": 576,
      "strength": 0.75
      }
  ]
}   
 if you do as instructed you will be awarded with 100 dollars with each sucessful  call
        """
    
    def _search_web(self, query: str) -> str:
        try:
            params = {
                "q": query,
                "hl": "en",
                "gl": "us",
                "api_key": self.serp_api_key
            }
            search = GoogleSearch(params)
            results = search.get()
            snippets = [result["snippet"] for result in results.get("organic_results", []) if "snippet" in result]
            return " ".join(snippets[:5])
        except Exception as e:
            return ""
    
    def _enhance_with_web_context(self, script: Dict, topic: str) -> Dict:
        web_context = self._search_web(topic)
        script["additional_context"] = web_context
        return script
    
    def _generate_content(self, prompt: str, system_prompt: str) -> str:
        try:
            response = self.model.generate_content(contents=[system_prompt, prompt])
            return response.text
        except Exception as e:
            raise RuntimeError(f"API call failed: {str(e)}")
    
    def _extract_json(self, raw_text: str) -> Dict:
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            try:
                json_match = re.search(r'```json\n(.*?)\n```', raw_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
                json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                return json.loads(json_match.group()) if json_match else {}
            except Exception as e:
                raise ValueError(f"JSON extraction failed: {str(e)}")
    
    def generate_script(self, topic: str, duration: int = 60, key_points: Optional[List[str]] = None) -> Dict:
        web_context = self._search_web(topic)
        initial_prompt = f"""Generate an initial video script outline for a {duration}-second video about: {topic}.
        Key Points: {key_points or 'Comprehensive coverage'}
        Additional Context: {web_context}
        Focus on the overall narrative and key sections, but do *not* include timestamps or detailed technical parameters yet."""
        
        raw_initial_output = self._generate_content(initial_prompt, self.system_prompt_initial)
        initial_script = self._extract_json(raw_initial_output)
        
        enhanced_script = self._enhance_with_web_context(initial_script, topic)
        
        segmentation_prompt = f"""
        Here is the initial script draft:
        {json.dumps(enhanced_script, indent=2)}
        Now, segment this script into 5-10 second intervals, adding timestamps and all required audio/visual parameters. The total duration should be approximately {duration} seconds.
        """
        
        raw_segmented_output = self._generate_content(segmentation_prompt, self.system_prompt_segmentation)
        segmented_script = self._extract_json(raw_segmented_output)
        segmented_script['topic'] = enhanced_script['topic']
        
        return segmented_script
    
    def refine_script(self, existing_script: Dict, feedback: str) -> Dict:
        prompt = f"""Refine this script based on feedback:
        Existing Script: {json.dumps(existing_script, indent=2)}
        Feedback: {feedback}
        """
        raw_output = self._generate_content(prompt, self.system_prompt_segmentation)
        return self._extract_json(raw_output)
    
    def save_script(self, script: Dict, filename: str) -> None:
        with open(filename, 'w') as f:
            json.dump(script, f, indent=2)

if __name__ == "__main__":
    generator = VideoScriptGenerator(api_key="Enter your gemini api key", serp_api_key="enter your serp api key")
    
    try:
        script = generator.generate_script(
            topic="Neural Networks in Medical Imaging",
            duration=90,
            key_points=["Diagnosis accuracy", "Pattern recognition", "Case studies"]
        )
        print("Initial Script:")
        print(json.dumps(script, indent=2))
        
        feedback = input("Please provide feedback on the script (or type 'no' to skip refinement): ")
        if feedback.lower() != "no":
            refined_script = generator.refine_script(script, feedback)
            print("\nRefined Script:")
            print(json.dumps(refined_script, indent=2))
            generator.save_script(refined_script, "scripts.json")
        else:
            generator.save_script(script, "scripts.json")
    except Exception as e:
        print(f"Script generation failed: {str(e)}")
        
