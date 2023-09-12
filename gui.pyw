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
import speedtest

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
    if attempt > 2:
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
        # remove check_internet_mic => instrction screeen 
        check_internet_mic.forget()
        # update question list 
        questions = questions_lst
        # show new frame for question page 
        f2.pack(fill=BOTH)
        # call next question function to render question
        update_status("Ready to go")
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
    global consider_textarea_answer
    update_status("Get Ready for question")
    if(consider_textarea_answer.get()):
        user_answer.set(textarea.get(1.0,END))
    if current_question <= len(questions) and current_question > 0:
        threading.Thread(target=score_answer, args=[current_question-1,user_answer.get(),]).start()
    
    # print(user_answer.get())
    user_answer.set("")
    textarea.delete(1.0,END)
    f2_checkbox["state"] = "normal"
    consider_textarea_answer.set(False)
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

        update_status("Waiting for your response")
    else:
        show_result()

def show_result():
    update_status("Wait until your report is getting ready")
    while(len(answer_feedback.keys()) != len(questions)):
        time.sleep(1)
    update_status("Your Report is ready")
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
        update_status("Recording...")
        # set flag to true, to start recording 
        record_users_answer.set(True)
        recording_btn.config(text="Stop Recording", background='#d93b3b')
        # disable next btn and consider text area checkbox
        next_button["state"] = "disabled"
        f2_checkbox["state"] = "disabled"
        # call record and convert functions
        threading.Thread(target=record_audio).start()
        threading.Thread(target=process_speech_to_text_queue).start()
    else:
        update_status("Evaluating your answer")
        recording_btn.config(text="Start Recording", background='#2c70e6')
        record_users_answer.set(False)
        recording_btn['state'] = "disabled"
        mic_lable.unbind("<Button-1>")

# function to start interview 
def start_interview():
    # calling this function with thread to avoid freezing of screen
    start_button["state"] = "disabled"
    update_status("Please wait, checking internet and microphone (this may take 2-3 min)")
    threading.Thread(target=check_speed_mic).start()

def move_forward():
    update_status("Please wait, finding the right interviewer for you")
    threading.Thread(target=get_questions).start()

def checkMic():
    try:
        obj = sr.Microphone()
    except:
        return False
    return True

def check_internet(attempt=0):
    if(attempt>1):
        return 0
    try:
        st = speedtest.Speedtest()
        speed = st.download()/(1024*1024)
        speed = str(speed)
        speed = speed[:speed.find(".")+2]
        speed = float(speed)
        return speed
    except:
        return check_internet(attempt+1)

def check_speed_mic():
    download = check_internet()
    mic_working = checkMic()

    created_by.forget()
    f1.forget()

    for widget in check_internet_mic.winfo_children():
            widget.destroy()
    check_internet_mic.pack()
    Label(check_internet_mic,text=f"Your download speed is {download} Mbps",font="calibre 16 bold",fg="black").pack(ipady=5)
    if(mic_working):
        Label(check_internet_mic,text="Your microphone is working properly",font="calibre 16 bold",fg="black").pack(ipady=5)
    else:
        Label(check_internet_mic,text="Your default microphone is not available, check the system settings",font="calibre 16 bold",fg="black").pack(ipady=5,)
        update_status("Come back later after fixing mic")
        return
    
    if(download<1):
        update_status("Your internet connection is either dead or your speed is too low")
        return
    
    Label(check_internet_mic,text="Instructions",font="calibre 20 bold",fg="black").pack(ipady=5)
    Label(check_internet_mic,text="1.) You can start giving answer after the interviewer speak question",font="calibre 15 bold",fg="black",wraplength=1100).pack(ipady=3)
    Label(check_internet_mic,text="2.) You can give your answer either by speaking or by writing",font="calibre 15 bold",fg="black",wraplength=1100).pack(ipady=3)
    Label(check_internet_mic,text="3.) Use textarea to write answer only when needed",font="calibre 15 bold",fg="black",wraplength=1100).pack(ipady=3)
    Label(check_internet_mic,text="4.) When you are using the text area to give an answer, tick the checkbox",font="calibre 15 bold",fg="black",wraplength=1100).pack(ipady=3)
    Label(check_internet_mic,text="",font="calibre 15 bold").pack()
    
    Button(check_internet_mic,text="Move Forward",command=move_forward,font="calibre 17 bold",width=18,background='#b3fbfc').pack()
    update_status("You are ready to go")
    
def update_status(msg):
    status.set(f"Status : {msg}")


if __name__ == "__main__":
    root = Tk()
    # setup basic window
    root.title("GPT Interview Buddy")
    root.geometry("1200x750")
    root.minsize(1150,700)

    # define Variables 
    role = StringVar(value=roles[0])
    experience = StringVar(value="Fresher")
    user_question = StringVar(value="nothing")
    user_answer = StringVar(value="")
    record_users_answer = BooleanVar(value=False)
    consider_textarea_answer = BooleanVar(value=False)
    status = StringVar(value="Status : Ready to go")
    # Variable of result page 
    resultPage_current_score = StringVar(value="")
    resultPage_total_score = StringVar(value="")
    resultPage_question = StringVar(value="")
    resultPage_feedback = StringVar(value="")

    # Main headings 
    Label(root,text="GPT Interview Buddy",font="calibre 30 bold").pack()
    created_by = Label(root,text="Created By Rapid Coders",font="calibre 15 normal",fg="#ff0066")
    created_by.pack()
    Label(root,text="",font="calibre 5 bold").pack()

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

    # check and show internet and mic status and show instructions
    check_internet_mic = Frame(root)

    # this will be rendered later
    # frame 2 is second page(question page)
    f2 = Frame(root)
    # lable to show question
    Label(f2,textvariable=user_question,padx=15,font="calibre 15 normal",wraplength=1100).pack()
    # show input box as an option to write answer
    textarea_frame = Frame(f2)
    textarea_frame.pack(ipady=8)
    textarea=Text(textarea_frame,font=("Ariel",14,"normal"),height=7,width=70)
    textarea.pack(side=LEFT)
    # adding Scrollbar to textarea
    Scroll =Scrollbar(textarea_frame)
    Scroll.pack(side=RIGHT,fill=Y)
    Scroll.config(command=textarea.yview)
    textarea.config(yscrollcommand=Scroll.set)
    # show check box to switch between text area and mic 
    # if checkbox is ticked then answer written in text area will be considered
    f2_checkbox = Checkbutton(f2,text="Consider the answer given in textarea instead of audio",variable=consider_textarea_answer,font="calibre 15 normal")
    f2_checkbox.pack()
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
    Label(f3,textvariable=resultPage_question, font="calibre 17 bold" ,wraplength=1100).pack(pady=5)
    Label(f3,textvariable=resultPage_current_score,font="calibre 14 bold").pack()
    Label(f3,textvariable=resultPage_feedback,font="calibre 14 normal",wraplength=1100).pack(pady=5)
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

    # status bar 
    status_frame = Frame(root,bg="#7ae9fa",relief='solid',border=2)
    status_frame.pack(side=BOTTOM,fill=X)
    Label(status_frame,textvariable=status,font="calibre 18 bold",bg="#7ae9fa").pack(side=LEFT, ipadx=10,ipady=10)
    root.mainloop()