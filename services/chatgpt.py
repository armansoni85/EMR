# importing from django
from django.conf import settings

# importing constants from django project
from strings import DOCTOR_AI_CONSULTATION_PROMPT

# importing third party libraries
from openai import OpenAI


class ChatGPT:
    """
    A class to interact with OpenAI's GPT-3.5-turbo and Whisper models for transcription and chat functionalities.
    Methods
    -------
    __init__():
        Initializes the ChatGPT instance with an OpenAI client using the provided API key.
    get_transcription(audio_file: bytes) -> str:
        Transcribes the given audio file using the Whisper model and returns the transcription as a string.
        Parameters:
        audio_file (bytes): The audio file to be transcribed.
        Returns:
        str: The transcription of the audio file.
    chat(text: str = '') -> str:
        Generates a chat response using the GPT-3.5-turbo model based on the provided text and a predefined system prompt.
        Parameters:
        text (str): The input text for the chat model.
        Returns:
        str: The generated response from the chat model.
    """

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def __get_transcription(self, audio_file_file: str) -> str:
        audio_file = open(audio_file_file, "rb")
        transcription = self.client.audio.transcriptions.create(
            model="whisper-1", file=audio_file, response_format="text"
        )
        audio_file.close()
        return transcription

    def __chat(self, text: str = "") -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": DOCTOR_AI_CONSULTATION_PROMPT},
                {"role": "user", "content": text},
            ],
        )
        return response.choices[0].message.content

    def get_doctor_ai_consultation(self, audio_file_path) -> str:
        return self.__chat(self.__get_transcription(audio_file_path))
