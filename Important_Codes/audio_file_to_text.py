# This code takes file name as input and convert it to text


import speech_recognition as sr

def speech_to_text(filename):
    text = ""
    # Initialize the recognizer
    r = sr.Recognizer()
 
    # Exception handling to handle exceptions at the runtime
    try:
        audio_data = sr.AudioFile(filename)
        with audio_data as source:
            audio = r.record(source)
            try:
                text = r.recognize_google(audio)
            except Exception as e:
                print("Exception: "+str(e))
    except:
        print("No such file exist")        

    return text

output = speech_to_text("mic.wav")
print(output)