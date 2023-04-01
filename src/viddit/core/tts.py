import os
from google.oauth2 import service_account
from google.cloud import texttospeech

class GoogleCloudTTS:
    def __init__(self, json_key_file_path):
        credentials = service_account.Credentials.from_service_account_file(json_key_file_path)
        self.client = texttospeech.TextToSpeechClient(credentials=credentials)

    def text_to_speech(self, input_text, output_filename, language_code='en-US', voice_name='en-US-Wavenet-A', speaking_rate=1.0, pitch=0.0):
        # Set the input text
        synthesis_input = texttospeech.SynthesisInput(text=input_text)

        # Set the voice configuration
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name,
        )

        # Set the audio configuration
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speaking_rate,
            pitch=pitch
        )

        # Perform text-to-speech
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # Write the resulting audio to a file
        with open(output_filename, 'wb') as out:
            out.write(response.audio_content)
            print(f'Audio content written to "{output_filename}"')

    def list_voices(self):
        voices = self.client.list_voices()
        for voice in voices.voices:
            print(f"Name: {voice.name}")
            print(f"Language code: {voice.language_codes[0]}")
            print(f"SSML Gender: {texttospeech.SsmlVoiceGender(voice.ssml_gender).name}")
            print("----")