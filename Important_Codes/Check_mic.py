# This code check for mic

import speech_recognition as sr

def checkMic():
    try:
        obj = sr.Microphone()
    except:
        print("unknown error occurred")
        return False
    
    return True

output = checkMic()
print(output)