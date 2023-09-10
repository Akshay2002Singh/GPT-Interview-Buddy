# This code takes input from microphone and converts to speech_to_text


import speech_recognition as sr

def speech_to_text():
    text = ""
    # Initialize the recognizer
    r = sr.Recognizer()

    # Exception handling to handle exceptions at the runtime
    try:
        # use the microphone as source for input.
        with sr.Microphone() as source2:
            # wait for a second to let the recognizer adjust the energy threshold based on the surrounding noiselevel
            r.adjust_for_ambient_noise(source2, duration=0.1)
            # listens for the user's input
            audio2 = r.listen(source2)
            
            # Using google to recognize audio
            text = r.recognize_google(audio2)
            text = text.lower() 
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
    except sr.UnknownValueError:
        print("unknown error occurred")
    
    return text

output = speech_to_text()
print(output)