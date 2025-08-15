# importing from django
from django.conf import settings

# importing constants from django project
from strings import DOCTOR_AI_CONSULTATION_PROMPT

# importing third party libraries
from openai import OpenAI

class ChatGPT:
    def __init__(self):
        print("\nInitializing ChatGPT service...")
        try:
            # Use settings instead of hardcoded key
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            print("OpenAI client initialized successfully")
        except Exception as e:
            print("\n!!! OPENAI INIT ERROR !!!")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            raise

    def __get_transcription(self, audio_file_file: str) -> str:
        print(f"\nStarting transcription: {audio_file_file}")
        try:
            with open(audio_file_file, "rb") as audio_file:
                print("Sending to Whisper API...")
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file, 
                    response_format="text"
                )
                print("Transcription successful!")
                print(f"Transcript: {transcription[:100]}...")  # First 100 chars
                return transcription
        except Exception as e:
            print("\n!!! TRANSCRIPTION ERROR !!!")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            raise

    def __chat(self, text: str = "") -> str:
        print("\nStarting ChatGPT analysis...")
        print(f"Input text: {text[:100]}...")  # First 100 chars
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": DOCTOR_AI_CONSULTATION_PROMPT},
                    {"role": "user", "content": text},
                ],
            )
            result = response.choices[0].message.content
            print("Analysis successful!")
            print(f"Result: {result[:100]}...")  # First 100 chars
            return result
        except Exception as e:
            print("\n!!! CHATGPT ANALYSIS ERROR !!!")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            raise

    def get_doctor_ai_consultation(self, audio_file_path) -> str:
        print(f"\n==== STARTING FULL ANALYSIS ====")
        try:
            transcription = self.__get_transcription(audio_file_path)
            return self.__chat(transcription)
        except Exception as e:
            print("\n!!! FULL PIPELINE FAILED !!!")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            raise
