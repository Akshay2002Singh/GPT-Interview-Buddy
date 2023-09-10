# This code takes input from microphone and converts to speech_to_text

import speech_recognition as sr
import queue
import threading
import time

# queue to store speech recognition object and speech clips
speech_queue = queue.SimpleQueue()
# variable to exit code 
exit_code = 0

# this function read queue, if it has any clips then convert it to text
# if exit code is 1 then loop will break
def process_speech_to_text_queue():
    print("in queue processing function")
    while(1):
        if(speech_queue.qsize() > 0):
            # print(f"in queue {speech_queue.qsize()}")
            # get speech recognition object and audio clip
            object_audio = speech_queue.get()
            try:
                text = ""
                # convert clip to text 
                text = object_audio[0].recognize_google(object_audio[1])
                print(text, end=" ")
            except:
                # print("Something went wrong")
                pass

        time.sleep(1)
        
        if exit_code:
            break



def record_audio():
    print("in record funcion")
    index = 0
    while(1):
        try:
            # use the microphone as source for input.
            with sr.Microphone() as source2:
                # Initialize the recognizer
                r = sr.Recognizer()
                # wait for a second to let the recognizer adjust the energy threshold based on the surrounding noiselevel
                r.adjust_for_ambient_noise(source2, duration=0.1)
                # listens for the user's input
                audio2 = r.listen(source2)
                # put recognizer object and audio clip in queue 
                speech_queue.put([r,audio2])
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
        except sr.UnknownValueError:
            print("unknown error occurred")

        if exit_code:
            break

    return ""


print("Starting thread")
threading.Thread(target=record_audio).start()
threading.Thread(target=process_speech_to_text_queue).start()

exit_code = int(input("Quit code : "))