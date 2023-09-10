# This code convert text to speech 

from gtts import gTTS
from playsound import playsound
import os

def text_to_speech(text):
    speech = gTTS(text = text, lang='en', tld='co.in')
    speech.save("temp.mp3")
    # play it 
    playsound('temp.mp3')
    os.remove("temp.mp3")

text_to_speech("How do you handle multi-threading in Python applications?")
