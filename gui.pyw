from tkinter import *
from PIL import ImageTk,Image
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import speech_recognition as sr
import queue
import threading
from gtts import gTTS
from playsound import playsound
import os
import time
import json

# some global variables
roles = ["Python Developer","Frontend Developer","Django Developer","MERN Developer","MEAN Developer","Android Developer","Software Developer","Ethical Hacker","Database Administrator", " Network Engineer"]
current_question = 0
questions = []
answer_feedback = {}
user_score_obj = {}
user_score = 0
# queue to store speech recognition object and speech clips
speech_queue = queue.SimpleQueue()

# get api key from ApiKey.txt
apiKey = ""
with open("ApiKey.txt",'r') as f:
    apiKey = f.readline()
    apiKey = apiKey.strip()

# function to bring questions
def get_questions(attempt=0):
    global questions
    # create model to predict
    if attempt > 5:
        return
    try:
        llm = OpenAI(openai_api_key=apiKey)
        # Prompt template for getting questions
        prompt_search_questions = PromptTemplate.from_template("Provide minimum 2 interview questions for {role} for {experience} candidate?")
        # format template to final prompt
        questions = prompt_search_questions.format(role = role.get(), experience = experience.get())
        # Getting output of prompt 
        questions_output = llm.predict(questions)

        # convert questions from string to list
        questions_output = questions_output.strip()
        questions_output = questions_output.split("\n")
        questions_lst = []
        for i in questions_output:
            i = i.split('. ')
            questions_lst.append(i[1])
        print(questions_lst)
        # remove f1 => home screeen 
        f1.forget()
        # update question list 
        questions = questions_lst
        # show new frame for question page 
        f2.pack(fill=BOTH)
        # call next question function to render question
        next_question()
    except:
        get_questions(attempt+1)

# this function convert text to speech 
def text_to_speech(text, try_count = 0):
    if try_count > 6:
        return
    try:
        speech = gTTS(text = text, lang='en', tld='co.in')
        speech.save("temp.mp3")
        # play it 
        playsound('temp.mp3')
        os.remove("temp.mp3")
    except:
        time.sleep(0.2)
        text_to_speech(text, try_count+1)

def score_answer(question_number, answer, attempt=0):
    global user_score
    global answer_feedback
    global user_score_obj
    if attempt > 3:
        return
    
    try:
        # create model to predict
        chat = ChatOpenAI(openai_api_key=apiKey)

        # Prompt templates to get score of answer
        system_template = (
            '''
            You are an interviewer, taking interview for {role} of a {experience} candidate.
            Question : {question}
            '''
        )
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
        human_template = "Answer : {answer}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        system_template_1 = "Rate this answer from 0 to 10 and provide score and feedback in json format."
        system_message_prompt_1 = SystemMessagePromptTemplate.from_template(system_template_1)
        # create final chat prompt 
        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt, system_message_prompt_1]
        )
        # Getting output of prompt 
        score_feedback = chat(
            chat_prompt.format_prompt(
                role = role.get(), experience=experience.get(), question=questions[question_number], answer = answer
            ).to_messages()
        )
        score_feedback = json.loads(score_feedback.content)
        user_score += int(score_feedback["score"])
        answer_feedback[question_number] = score_feedback['feedback']
        user_score_obj[question_number] = score_feedback['score']
    except:
        score_answer(question_number,answer,attempt+1)
    

# this function read queue, if it has any clips then convert it to text
def process_speech_to_text_queue():
    # print("in queue processing function")
    while(record_users_answer.get() or speech_queue.qsize() >0):
        if(speech_queue.qsize() > 0):
            # print(f"in queue {speech_queue.qsize()}")
            # get speech recognition object and audio clip
            object_audio = speech_queue.get()
            try:
                text = ""
                # convert clip to text 
                text = object_audio[0].recognize_google(object_audio[1])
                user_answer.set(user_answer.get() + text +". ")
            except:
                # print("Something went wrong")
                pass

        time.sleep(0.5)
    next_question()


# this code records audio 
def record_audio():
    # print("in record function")
    while(record_users_answer.get()):
        # print(record_users_answer.get())
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
                # print(f'inside record = {speech_queue.qsize()}')
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
        except sr.UnknownValueError:
            print("unknown error occurred")


# this function render new question
def next_question():
    global current_question
    if current_question <= len(questions) and current_question > 0:
        threading.Thread(target=score_answer, args=[current_question-1,user_answer.get(),]).start()
    
    # print(user_answer.get())
    user_answer.set("")
    if current_question<len(questions):
        # hide mic and next btn 
        mic_lable.forget()
        next_button.forget()
        space1.forget()
        recording_btn.forget()

        user_question.set(f'Question : {questions[current_question]}')
        text_to_speech(questions[current_question])
        current_question+=1

        # show mic and next btn 
        mic_lable.pack(ipady=15)
        mic_lable.bind("<Button-1>", mic_clicked)
        recording_btn.pack()
        recording_btn['state'] = "normal"
        space1.pack()
        next_button.pack()
        next_button["state"] = "normal"
    else:
        show_result()

def show_result():
    while(len(answer_feedback.keys()) != len(questions)):
        time.sleep(1)
    global current_question
    current_question = 0
    f2.forget()
    f3.pack()
    resultPage_total_score.set(f"Your Total Score : {user_score}/{len(questions)*10}")
    resultPage_current_score.set(f"Current Question Score : {user_score_obj[current_question]}/10")
    resultPage_question.set(f"Question {current_question+1} : {questions[current_question]}")
    resultPage_feedback.set(f"Feedback : {answer_feedback[current_question]}")
    feedback_previous_btn['state'] = 'disable'

def previous_feedback():
    global current_question
    if feedback_next_btn['state'] == 'disabled':
        feedback_next_btn['state'] = 'normal'
    current_question -= 1
    resultPage_current_score.set(f"Current Question Score : {user_score_obj[current_question]}/10")
    resultPage_question.set(f"Question {current_question+1} : {questions[current_question]}")
    resultPage_feedback.set(f"Feedback : {answer_feedback[current_question]}")
    if(current_question == 0):
        feedback_previous_btn['state'] = 'disabled'

def next_feedback():
    global current_question
    if feedback_previous_btn['state'] == 'disabled':
        feedback_previous_btn['state'] = 'normal'
    current_question += 1
    resultPage_current_score.set(f"Current Question Score : {user_score_obj[current_question]}/10")
    resultPage_question.set(f"Question {current_question+1} : {questions[current_question]}")
    resultPage_feedback.set(f"Feedback : {answer_feedback[current_question]}")
    if( current_question == (len(questions)-1) ):
        feedback_next_btn['state'] = 'disabled'

# check_current answer and show next question
def check_and_call_next():
    threading.Thread(target=next_question).start()

# this function handle mic click 
def mic_clicked(temp = None):
    if recording_btn.cget('text') == "Start Recording":
        # set flag to true, to start recording 
        record_users_answer.set(True)
        recording_btn.config(text="Stop Recording", background='#d93b3b')
        # disable next btn 
        next_button["state"] = "disabled"
        # call record and convert functions
        threading.Thread(target=record_audio).start()
        threading.Thread(target=process_speech_to_text_queue).start()
    else:
        recording_btn.config(text="Start Recording", background='#2c70e6')
        record_users_answer.set(False)
        recording_btn['state'] = "disabled"
        mic_lable.unbind("<Button-1>")

# function to start interview 
def start_interview():
    global mic
    # calling this function with thread to avoid freezing of screen
    start_button["state"] = "disabled"
    threading.Thread(target=get_questions).start()

if __name__ == "__main__":
    root = Tk()
    # setup basic window
    root.title("GPT Interview Buddy")
    root.geometry("850x650")
    root.minsize(800,600)

    # define Variables 
    role = StringVar(value=roles[0])
    experience = StringVar(value="Fresher")
    user_question = StringVar(value="nothing")
    user_answer = StringVar(value="")
    record_users_answer = BooleanVar(value=False)
    # Variable of result page 
    resultPage_current_score = StringVar(value="")
    resultPage_total_score = StringVar(value="")
    resultPage_question = StringVar(value="")
    resultPage_feedback = StringVar(value="")

    # Main headings 
    Label(root,text="GPT Interview Buddy",font="calibre 30 bold").pack()
    Label(root,text="Created By Rapid Coders",font="calibre 15 normal",fg="#ff0066").pack()
    Label(root,text="",font="calibre 10 bold").pack()

    # Creating frame to hold all content. We will update this Frame when needed.
    f1 = Frame(root)
    f1.pack(fill=BOTH)

    # Inserting options to select role
    # frame 1 is home page 
    Label(f1,text="Select Your Role",font="calibre 20 bold",fg="black",bg='#bcecf5', relief='sunken' , pady=2).pack(side=TOP, ipady=5, ipadx=8)
    i = 0
    while(i<len(roles)):
        temp_frame = Frame(f1)
        temp_frame.pack(side=TOP,fill=Y)
        Radiobutton(temp_frame,text=roles[i], font="cosmicsansms 15", width=20 , padx=15,variable=role,value=roles[i]).pack(side=LEFT)
        i+=1
        if(i<len(roles)):
            Radiobutton(temp_frame,text=roles[i], font="cosmicsansms 15", width=20, padx=15,variable=role,value=roles[i]).pack(side=RIGHT)
            i+=1
            
    # Creating frame to insert experience options
    temp_frame = Frame(f1, pady=15)
    temp_frame.pack(fill=Y)
    Label(temp_frame,text="Select Your Experience",font="calibre 20 bold",fg="black" ,bg='#bcecf5', relief='sunken', pady=2).pack(side=TOP, ipady=5, ipadx=8)
    Radiobutton(temp_frame,text='Fresher', font="cosmicsansms 15", width=20 , padx=15, variable=experience, value="Fresher").pack(side=LEFT, ipady=15)
    Radiobutton(temp_frame,text='Intermediate', font="cosmicsansms 15", width=20 , padx=15, variable=experience, value="Intermediate").pack(side=LEFT, ipady=15)
    Radiobutton(temp_frame,text='Senior', font="cosmicsansms 15", width=20 , padx=15, variable=experience, value="Senior").pack(side=LEFT, ipady=15)

    # Button to start interview 
    start_button = Button(f1,text="Start Interview",command=start_interview,font="calibre 17 bold")
    start_button.pack()


    # this will be rendered later
    # frame 2 is second page(question page)
    f2 = Frame(root)
    # lable to show question
    Label(f2,textvariable=user_question,padx=15,font="calibre 15 normal",wraplength=750).pack()
    # show mic image and set onclick event
    mic = ImageTk.PhotoImage(Image.open('mic.png'), height=20, width= 20)
    mic_lable = Label(f2, image=mic)
    mic_lable.bind("<Button-1>", mic_clicked)
    recording_btn = Button(f2,text="Start Recording", command=mic_clicked, font="calibre 17 bold",borderwidth=2, background='#2c70e6', fg='#edfa00')
    space1 = Label(f2,text="")
    next_button = Button(f2,text="Next Question",command=check_and_call_next,font="calibre 17 bold")

    # this page will be rendered later
    # frame 3 is third page(Result page)
    f3 = Frame(root)
    Label(f3,textvariable=resultPage_total_score,font="calibre 22 bold").pack(pady=5)
    Label(f3,textvariable=resultPage_question, font="calibre 17 bold" ,wraplength=750).pack(pady=5)
    Label(f3,textvariable=resultPage_current_score,font="calibre 14 bold").pack()
    Label(f3,textvariable=resultPage_feedback,font="calibre 14 normal",wraplength=750).pack(pady=5)
    temp_f3 = Frame(f3)
    temp_f3.pack(pady=20)
    feedback_previous_btn =  Button(temp_f3,text="Previous Question",command=previous_feedback,font="calibre 17 bold",width=18,background='#b3fbfc')
    feedback_previous_btn.pack(side=LEFT)
    Label(temp_f3,text="\t \t \t \t").pack(side=LEFT)
    feedback_next_btn = Button(temp_f3,text="Next Question",command=next_feedback,font="calibre 17 bold",width=18,background='#b3fbfc')
    feedback_next_btn.pack(side=RIGHT)

    Button(f3,text="Home Page",command=quit,font="calibre 17 bold",width=20,background='#f3b5ff').pack(side=TOP)
    Label(f3,text="").pack(pady=2)
    Button(f3,text="Quit",command=quit,font="calibre 17 bold",width=20,bg='#f3b5ff').pack(side=TOP)

    root.mainloop()