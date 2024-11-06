import os
import io
import random
from dotenv import load_dotenv
from pydub import AudioSegment
from pydub.playback import play
import azure.cognitiveservices.speech as speechsdk

AZURE_VOICES = [
    "en-US-DavisNeural",
    "en-US-TonyNeural",
    "en-US-JasonNeural",
    "en-US-GuyNeural",
    "en-US-JaneNeural",
    "en-US-NancyNeural",
    "en-US-JennyNeural",
    "en-US-AriaNeural",
]

AZURE_VOICE_STYLES = [
    "angry",
    "cheerful",
    "excited",
    "hopeful",
    "sad",
    "shouting",
    "terrified",
    "unfriendly",
    "whispering"
]

AZURE_PREFIXES = {
    "(angry)" : "angry",
    "(cheerful)" : "cheerful",
    "(excited)" : "excited",
    "(hopeful)" : "hopeful",
    "(sad)" : "sad",
    "(shouting)" : "shouting",
    "(shout)" : "shouting",
    "(terrified)" : "terrified",
    "(unfriendly)" : "unfriendly",
    "(whispering)" : "whispering",
    "(whisper)" : "whispering",
    "(random)" : "random"
}

# Get the api key and region saved from azure
# from environment variables stroed on pc

api_key = os.getenv('api_key')
region = os.getenv('region')

def play_aufio_from_bytes(audio_data, format='wave'):
    audio_data_io = io.BytesIO(audio_data)
    audio_segment = AudioSegment.from_file(audio_data_io, format=format)
    play(audio_segment)

class AzureTextToSpeechRequest:
    def __init__(self, apiKey, regionKey):

        # Use the API Key and Region provided in azure to fill in to the parameters, and then configure the speech thing after getting your api data
        # Then, use a voice provided by azure, (more voices below) and synthesis the actual speech with the speech configuration accordindly
        # https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts#prebuilt-neural-voices

        self.apiKey = apiKey
        self.regionKey = regionKey
        self.speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)
        self.audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    
    def speechMessage(self, message: str, voiceStyle: str = "", speed: int = 0) -> bool:

        # TODO: add functionality to pass in voice styles and names, like a constants at the beginning of the script with a bunch of names and styles also style prefixes (ex: (anger) MANGO)

        # Get the resulting speech from a systhesied message passed in from parameter and play it.

        message = message.lower()

        if(message[0] == "(" and ")" in message):
            prefix = message[0:message.find(")") + 1]
            if(voiceStyle == ""):
                if prefix in AZURE_PREFIXES:
                    print(prefix)
                    voiceStyle = AZURE_PREFIXES[prefix]
                    message = message[message.find(prefix[-1]) + 1:]
        if(len(message) == 0):
            print("This message is empty")
            return
        if(voiceStyle == "random"):
            voiceStyle = random.choice(AZURE_VOICE_STYLES)


        synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)

        ssml_text = f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='https://www.w3.org/2001/mstts' xml:lang='en-US'> \
                        <voice name='en-US-DavisNeural'> \
                            <prosody rate='+{speed}%'> \
                                <mstts:express-as style='{voiceStyle}' styledegree='2'> \
                                        {message}。\
                                    </mstts:express-as> \
                                </prosody> \
                        </voice> \
                    </speak>"
        
        result =  synthesizer.speak_ssml_async(ssml_text).get()

        # Print certain debugging messages based on the output from the result

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized to speaker for text [{}]".format(message))
            return True

        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
           

            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
            print("Did you update the subscription info?")
            return False

