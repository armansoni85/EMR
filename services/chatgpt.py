# importing from django
from django.conf import settings

# importing constants from django project
from strings import DOCTOR_AI_CONSULTATION_PROMPT, AI_CHAT_SUPPORT_PROMPT

# importing third party libraries
from openai import OpenAI
from base.decorators import retry


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
        print(settings.OPENAI_API_KEY)

    @retry(tries=settings.MAX_RETRY_LIMIT, delay=1, log=True)
    def get_transcription(self, audio_file_file: str) -> str:
        audio_file = open(audio_file_file, "rb")
        transcription = self.client.audio.transcriptions.create(
            model=settings.AI_AUDIO_TRANSCRIPT_MODEL,
            file=audio_file,
            response_format="text",
        )
        audio_file.close()
        return transcription

    @retry(tries=settings.MAX_RETRY_LIMIT, delay=1, log=True)
    def chat(self, system_prompt: str, text: str = "") -> str:
        response = self.client.chat.completions.create(
            model=settings.AI_TEXT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        )
        return response.choices[0].message.content

    def get_doctor_ai_consultation(self, audio_file_path) -> str:
        return self.chat(
            system_prompt=DOCTOR_AI_CONSULTATION_PROMPT,
            text=self.get_transcription(audio_file_path),
        )

    def ai_chat_support(self, text: str):
        return self.chat(system_prompt=AI_CHAT_SUPPORT_PROMPT, text=text)
