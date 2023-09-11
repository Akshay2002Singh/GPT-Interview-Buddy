from tkinter import *
from PIL import ImageTk,Image
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import threading
import time

# some global variables
roles = ["Python Developer","Frontend Developer","Django Developer","MERN Developer","MEAN Developer","Android Developer","Software Developer","Ethical Hacker","Database Administrator", " Network Engineer"]
current_question = 0
questions = []

# get api key from ApiKey.txt
apiKey = ""
with open("ApiKey.txt",'r') as f:
    apiKey = f.readline()
    apiKey = apiKey.strip()

# function to bring questions
def get_questions():
    global questions
    # create model to predict
    llm = OpenAI(openai_api_key=apiKey)
    # Prompt template for getting questions
    prompt_search_questions = PromptTemplate.from_template("Provide minimum 15 interview questions for {role} for {experience} candidate?")
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

    # remove f1 => home screeen 
    f1.forget()
    # update question list 
    questions = questions_lst
    # show new frame for question page 
    f2.pack(fill=BOTH)
    # call next question function to render question
    next_question()

# this function clear f1 frame
def clear_frame():
    for widget in f1.winfo_children():
        widget.destroy()

# this function render new question
def next_question():
    global current_question
    print(questions)
    if current_question<len(questions):
        user_question.set(f'Question : {questions[current_question]}')
        current_question+=1

# this function handle mic click 
def mic_clicked(temp=None):
    if recording_btn.cget('text') == "Start Recording":
        recording_btn.config(text="Stop Recording", background='#d93b3b')
    else:
        recording_btn.config(text="Start Recording", background='#2c70e6')

# function to start interview 
def start_interview():
    global mic
    print(role.get())
    print(experience.get())
    # calling this function with thread to avoid freezing of screen
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
    Label(f2,textvariable=user_question,padx=15,font="calibre 15 normal").pack()
    # show mic image and set onclick event
    mic = ImageTk.PhotoImage(Image.open('mic.png'), height=20, width= 20)
    mic_lable = Label(f2, image=mic)
    mic_lable.bind("<Button-1>", mic_clicked)
    mic_lable.pack(ipady=15)
    recording_btn = Button(f2,text="Start Recording", command=mic_clicked, font="calibre 17 bold",borderwidth=2, background='#2c70e6', fg='#edfa00')
    recording_btn.pack()
    Label(f2,text="").pack()
    next_button = Button(f2,text="Next Question",command=next_question,font="calibre 17 bold")
    next_button.pack()

    root.mainloop()