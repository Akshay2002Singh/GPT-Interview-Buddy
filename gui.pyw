from tkinter import *

# some global variables
roles = ["Python Developer","Frontend Developer","Django Developer","MERN Developer","MEAN Developer","Android Developer","Software Developer","Ethical Hacker","Database Administrator", " Network Engineer"]
current_question = 0
questions = []


# this function clear f1 frame
def clear_frame():
    for widget in f1.winfo_children():
        widget.destroy()

def next_question():
    if current_question<len(questions):

        current_question+=1
        


def start_interview():
    print(role.get())
    print(experience.get())
    clear_frame()
    Label(f1,text=f"Question : {user_question.get()}",padx=15,font="calibre 15 normal").pack()

    next_button.pack()

if __name__ == "__main__":
    root = Tk()
    # setup basic window
    root.title("GPT Interview Buddy")
    root.geometry("850x650")
    root.minsize(800,600)

    # define Variables 
    role = StringVar(value=roles[0])
    experience = StringVar(value="Fresher")
    user_question = StringVar(value="")
    user_answer = StringVar(value="")

    # Main headings 
    Label(root,text="GPT Interview Buddy",font="calibre 30 bold").pack()
    Label(root,text="Created By Rapid Coders",font="calibre 15 normal",fg="#ff0066").pack()
    Label(root,text="",font="calibre 10 bold").pack()

    # Creating frame to hold all content. We will update this Frame when needed.
    f1 = Frame(root)
    f1.pack(fill=BOTH)

    # Inserting options to select role
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
    next_button = Button(root,text="Next Question",command=next_question,font="calibre 17 bold")


    root.mainloop()