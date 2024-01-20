import os

import azure.cognitiveservices.speech as speech_sdk
from dotenv import load_dotenv

global speech_config
global translation_config


def main():
    try:

        # Set Configuration Settings
        input_language = input('Enter input language: '
                               '\n en = English'
                               '\n hi = Hindi\n'
                               ).lower()

        set_config(input_language)

        target_language = ''
        while target_language != 'quit':

            target_language = (input(
                '\nEnter a target language'
                '\n fr = French'
                '\n es = Spanish'
                '\n hi = Hindi'
                '\n it = Italian'
                '\n de = Deutsch'
                '\n Enter anything else to stop\n')
                               .lower())
            if target_language in translation_config.target_languages:
                translate(target_language)
            else:
                target_language = 'quit'

    except Exception as ex:
        print(ex)


def set_config(language):
    global speech_config
    global translation_config

    load_dotenv()
    ai_key = os.getenv('SPEECH_KEY')
    ai_region = os.getenv('SPEECH_REGION')

    # Configure translation
    translation_config = speech_sdk.translation.SpeechTranslationConfig(ai_key, ai_region)

    if language == 'hi':
        translation_config.speech_recognition_language = 'hi-IN'
    else:
        translation_config.speech_recognition_language = 'en-US'

    translation_config.add_target_language('fr')
    translation_config.add_target_language('es')
    translation_config.add_target_language('it')
    translation_config.add_target_language('hi')
    translation_config.add_target_language('de')

    # Configure speech
    speech_config = speech_sdk.SpeechConfig(ai_key, ai_region)


def translate(target_language):
    translation = ''

    # Translate speech
    audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
    translator = speech_sdk.translation.TranslationRecognizer(translation_config, audio_config=audio_config)
    print('Speak now...')

    result = translator.recognize_once_async().get()

    if result.reason is not speech_sdk.ResultReason.TranslatedSpeech:
        print(result.Reason)
        return translation

    print('Translating "{}"'.format(result.text))
    translation = result.translations[target_language]
    print(translation)

    # Synthesize translation
    convert_to_audio(target_language, translation)


def convert_to_audio(target_language, text):
    # https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts
    voices = {
        "fr": "fr-FR-HenriNeural",
        "es": "es-ES-ElviraNeural",
        "hi": "hi-IN-MadhurNeural",
        "de": "de-DE-KatjaNeural",
        "it": "it-IT-Neural",
    }

    speech_config.speech_synthesis_voice_name = voices.get(target_language)
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)

    speak = speech_synthesizer.speak_text_async(text).get()

    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)


if __name__ == "__main__":
    main()
