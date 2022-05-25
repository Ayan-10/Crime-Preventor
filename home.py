import os
import cv2
import shutil 
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

from PIL import Image
from PIL import ImageTk
import threading
from simple_facerec import SimpleFacerec

import shutil
from facerec import *
from register import *
from dbHandler import *
from tkinter.ttk import * 
from tkinter import *
from tkinter import messagebox
from PIL import Image 
from selenium import*
from match import *
from selenium import*
from selenium. common. exceptions import *
from PIL import Image
from selenium import*

#####################

active_page = 0
thread_event = None
left_frame = None
right_frame = None
heading = None
webcam = None
img_label = None
img_read = None
img_list = []
slide_caption = None
slide_control_panel = None
current_slide = -1
#######################


root = tk.Tk()
root.title('Crime Preventor')
root.geometry('1500x900+200+100')
root.resizable(True, True)

#########################


# create Pages
pages = []
for i in range(5):
    pages.append(tk.Frame(root, bg="#660033"))
    pages[i].pack(side="top", fill="both", expand=True)
    pages[i].place(x=0, y=0, relwidth=1, relheight=1)


def goBack():
    global active_page, thread_event, webcam

    if (active_page==4 and not thread_event.is_set()):
        thread_event.set()
        webcam.release()

    for widget in pages[active_page].winfo_children():
        widget.destroy()

    pages[0].lift()
    active_page = 0


def basicPageSetup(pageNo):
    global left_frame, right_frame, heading

    back_img = tk.PhotoImage(file="back.png")
    back_button = tk.Button(pages[pageNo], image=back_img, bg="#660033", bd=0, highlightthickness=0,
           activebackground="#660033", command=goBack)
    back_button.image = back_img
    back_button.place(x=1, y=0)

    heading = tk.Label(pages[pageNo], fg="white", bg="#660033", font="Arial 20 bold", pady=10)
    heading.pack()

    content = tk.Frame(pages[pageNo], bg="#660033", pady=20)
    content.pack(expand="true", fill="both")

    left_frame = tk.Frame(content, bg="#660033")
    left_frame.grid(row=0, column=0, sticky="nsew")

    right_frame = tk.LabelFrame(content, text="Detected Criminals", bg="#660033", font="Arial 20 bold", bd=4,
                             foreground="#2ea3ef", labelanchor="n")
    right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    content.grid_columnconfigure(0, weight=1, uniform="group1")
    content.grid_columnconfigure(1, weight=1, uniform="group1")
    content.grid_rowconfigure(0, weight=1)


def showImage(frame, img_size):
    global img_label, left_frame

    img = cv2.resize(frame, (img_size, img_size))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(img)
    if (img_label == None):
        img_label = tk.Label(left_frame, image=img, bg="#660033")
        img_label.image = img
        img_label.pack(padx=20)
    else:
        print("aaaaaaaaaaaaaaaa")
        img_label.configure(image=img)
        img_label.image = img


def getNewSlide(control):
    global img_list, current_slide

    if(len(img_list) > 1):
        if(control == "prev"):
            current_slide = (current_slide-1) % len(img_list)
        else:
            current_slide = (current_slide+1) % len(img_list)

        img_size = left_frame.winfo_height() - 200
        showImage(img_list[current_slide], img_size)

        slide_caption.configure(text = "Image {} of {}".format(current_slide+1, len(img_list)))


def selectMultiImage(opt_menu, menu_var):
    global img_list, current_slide, slide_caption, slide_control_panel

    filetype = [("images", "*.jpg *.jpeg *.png")]
    path_list = filedialog.askopenfilenames(title="Choose an image", filetypes=filetype)

    if(len(path_list) < 0):
        messagebox.showerror("Error", "Choose an images.")
    else:
        img_list = []
        current_slide = -1

        # Resetting slide control panel
        if (slide_control_panel != None):
            slide_control_panel.destroy()

        # Creating Image list
        for path in path_list:
            img_list.append(cv2.imread(path))

        # Creating choices for profile pic menu
        menu_var.set("")
        opt_menu['menu'].delete(0, 'end')

        for i in range(len(img_list)):
            ch = "Image " + str(i+1)
            opt_menu['menu'].add_command(label=ch, command= tk._setit(menu_var, ch))
            menu_var.set("Image 1")


        # Creating slideshow of images
        img_size =  left_frame.winfo_height() - 200
        current_slide += 1
        showImage(img_list[current_slide], img_size)

        slide_control_panel = tk.Frame(left_frame, bg="#660033", pady=20)
        slide_control_panel.pack()

        back_img = tk.PhotoImage(file="previous.png")
        next_img = tk.PhotoImage(file="next.png")

        prev_slide = tk.Button(slide_control_panel, image=back_img, bg="#660033", bd=0, highlightthickness=0,
                            activebackground="#660033", command=lambda : getNewSlide("prev"))
        prev_slide.image = back_img
        prev_slide.grid(row=0, column=0, padx=60)

        slide_caption = tk.Label(slide_control_panel, text="Image 1 of {}".format(len(img_list)), fg="#ff9800",
                              bg="#660033", font="Arial 15 bold")
        slide_caption.grid(row=0, column=1)

        next_slide = tk.Button(slide_control_panel, image=next_img, bg="#660033", bd=0, highlightthickness=0,
                            activebackground="#660033", command=lambda : getNewSlide("next"))
        next_slide.image = next_img
        next_slide.grid(row=0, column=2, padx=60)


def register(entries, required, menu_var):
    global img_list

    # Checking if no image selected
    if(len(img_list) == 0):
        messagebox.showerror("Error", "Select Images first.")
        return

    # Fetching data from entries
    entry_data = {}
    for i, entry in enumerate(entries):
        val = entry[1].get()

        if (len(val) == 0 and required[i] == 1):
            messagebox.showerror("Field Error", "Required field missing :\n\n%s" % (entry[0]))
            return
        else:
            entry_data[entry[0]] = val


    # Setting Directory
    path = os.path.join('face_samples', "temp_criminal")
    if not os.path.isdir(path):
        os.mkdir(path)

    no_face = []
    for i, img in enumerate(img_list):
        # Storing Images in directory
        id = registerCriminal(img, path, i + 1)
        if(id != None):
            no_face.append(id)

    # check if any image doesn't contain face
    if(len(no_face) > 0):
        no_face_st = ""
        for i in no_face:
            no_face_st += "Image " + str(i) + ", "
        messagebox.showerror("Registration Error", "Registration failed!\n\nFollowing images doesn't contain"
                        " face or Face is too small:\n\n%s"%(no_face_st))
        shutil.rmtree(path, ignore_errors=True)
    else:
        # Storing data in database
        rowId = insertData(entry_data)

        if(rowId!=""):
            messagebox.showinfo("Success", "Criminal Registered Successfully.")
            shutil.move(path, os.path.join('face_samples', entry_data["Name"]))

            # save profile pic
            profile_img_num = int(menu_var.get().split(' ')[1]) - 1
            if not os.path.isdir("profile_pics"):
                os.mkdir("profile_pics")
            cv2.imwrite("profile_pics/criminal %s.png"%rowId, img_list[profile_img_num])

            goBack()
        else:
            shutil.rmtree(path, ignore_errors=True)
            messagebox.showerror("Database Error", "Some error occured while storing data.")


## update scrollregion when all widgets are in canvas
def on_configure(event, canvas, win):
    canvas.configure(scrollregion=canvas.bbox('all'))
    canvas.itemconfig(win, width=event.width)

## Register Page ##
def getPage1():
    global active_page, left_frame, right_frame, heading, img_label
    active_page = 1
    img_label = None
    opt_menu = None
    menu_var = tk.StringVar(root)
    pages[1].lift()

    basicPageSetup(1)
    heading.configure(text="Register Criminal")
    right_frame.configure(text="Enter Details")

    btn_grid = tk.Frame(left_frame, bg="#660033")
    btn_grid.pack()

    tk.Button(btn_grid, text="Select Images", command=lambda: selectMultiImage(opt_menu, menu_var), font="Arial 15 bold", bg="#2196f3",
           fg="white", pady=10, bd=0, highlightthickness=0, activebackground="#091428",
           activeforeground="white").grid(row=0, column=0, padx=25, pady=25)


    # Creating Scrollable Frame
    canvas = tk.Canvas(right_frame, bg="#660033", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand="true", padx=30)
    scrollbar = tk.Scrollbar(right_frame, command=canvas.yview, width=20, troughcolor="#660033", bd=0,
                          activebackground="#00bcd4", bg="#2196f3", relief="raised")
    scrollbar.pack(side="left", fill="y")

    scroll_frame = tk.Frame(canvas, bg="#660033", pady=20)
    scroll_win = canvas.create_window((0, 0), window=scroll_frame, anchor='nw')

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda event, canvas=canvas, win=scroll_win: on_configure(event, canvas, win))


    tk.Label(scroll_frame, text="* Required Fields", bg="#660033", fg="yellow", font="Arial 13 bold").pack()
    # Adding Input Fields
    input_fields = ("Name", "Father's Name", "Mother's Name", "Gender", "DOB(yyyy-mm-dd)", "Blood Group",
                    "Identification Mark", "Nationality", "Religion", "Crimes Done", "Profile Image")
    ip_len = len(input_fields)
    required = [1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0]

    entries = []
    for i, field in enumerate(input_fields):
        row = tk.Frame(scroll_frame, bg="#660033")
        row.pack(side="top", fill="x", pady=15)

        label = tk.Text(row, width=20, height=1, bg="#660033", fg="#ffffff", font="Arial 13", highlightthickness=0, bd=0)
        label.insert("insert", field)
        label.pack(side="left")

        if(required[i] == 1):
            label.tag_configure("star", foreground="yellow", font="Arial 13 bold")
            label.insert("end", "  *", "star")
        label.configure(state="disabled")

        if(i != ip_len-1):
            ent = tk.Entry(row, font="Arial 13", selectbackground="#90ceff")
            ent.pack(side="right", expand="true", fill="x", padx=10)
            entries.append((field, ent))
        else:
            menu_var.set("Image 1")
            choices = ["Image 1"]
            opt_menu = tk.OptionMenu(row, menu_var, *choices)
            opt_menu.pack(side="right", fill="x", expand="true", padx=10)
            opt_menu.configure(font="Arial 13", bg="#2196f3", fg="white", bd=0, highlightthickness=0, activebackground="#90ceff")
            menu = opt_menu.nametowidget(opt_menu.menuname)
            menu.configure(font="Arial 13", bg="white", activebackground="#90ceff", bd=0)

    tk.Button(scroll_frame, text="Register", command=lambda: register(entries, required, menu_var), font="Arial 15 bold",
           bg="#2196f3", fg="white", pady=10, padx=30, bd=0, highlightthickness=0, activebackground="#091428",
           activeforeground="white").pack(pady=25)


def showCriminalProfile(name):
    top = tk.Toplevel(bg="#660033")
    top.title("Criminal Profile")
    top.geometry("1500x900+%d+%d"%(root.winfo_x()+10, root.winfo_y()+10))

    tk.Label(top, text="Criminal Profile", fg="white", bg="#660033", font="Arial 20 bold", pady=10).pack()

    content = tk.Frame(top, bg="#660033", pady=20)
    content.pack(expand="true", fill="both")
    content.grid_columnconfigure(0, weight=3, uniform="group1")
    content.grid_columnconfigure(1, weight=5, uniform="group1")
    content.grid_rowconfigure(0, weight=1)

    (id, crim_data) = retrieveData(name)

    path = os.path.join("profile_pics", "criminal %s.png"%id)
    # profile_img = cv2.imread(path)

    # #profile_img = cv2.resize(profile_img, (500, 500))
    # img = cv2.cvtColor(profile_img, cv2.COLOR_BGR2RGB)
    # img = Image.fromarray(img)
    # img = ImageTk.PhotoImage(img)
    # img_label = tk.Label(content, image=img, bg="#660033")
    # img_label.image = img
    # img_label.grid(row=0, column=0)

    info_frame = tk.Frame(content, bg="#660033")
    info_frame.grid(row=0, column=1, sticky='w')

    for i, item in enumerate(crim_data.items()):
        tk.Label(info_frame, text=item[0], pady=15, fg="yellow", font="Arial 15 bold", bg="#660033").grid(row=i, column=0, sticky='w')
        tk.Label(info_frame, text=":", fg="yellow", padx=50, font="Arial 15 bold", bg="#660033").grid(row=i, column=1)
        val = "---" if (item[1]=="") else item[1]
        tk.Label(info_frame, text=val.capitalize(), fg="white", font="Arial 15", bg="#660033").grid(row=i, column=2, sticky='w')

def showMissingPeople(name):
    top = tk.Toplevel(bg="#660033")
    top.title("Police Station Details")
    top.geometry("1500x900+%d+%d"%(root.winfo_x()+10, root.winfo_y()+10))

    tk.Label(top, text="Police Station Details", fg="white", bg="#660033", font="Arial 20 bold", pady=10).pack()

    content = tk.Frame(top, bg="#660033", pady=20)
    content.pack(expand="true", fill="both")
    content.grid_columnconfigure(0, weight=3, uniform="group1")
    content.grid_columnconfigure(1, weight=5, uniform="group1")
    content.grid_rowconfigure(0, weight=1)

    (id, crim_data) = retrieveMissingPeopleData(name)

    path = os.path.join("profile_pics", "criminal %s.png"%id)
    # profile_img = cv2.imread(path)

    # #profile_img = cv2.resize(profile_img, (500, 500))
    # img = cv2.cvtColor(profile_img, cv2.COLOR_BGR2RGB)
    # img = Image.fromarray(img)
    # img = ImageTk.PhotoImage(img)
    # img_label = tk.Label(content, image=img, bg="#660033")
    # img_label.image = img
    # img_label.grid(row=0, column=0)

    info_frame = tk.Frame(content, bg="#660033")
    info_frame.grid(row=0, column=1, sticky='w')

    for i, item in enumerate(crim_data.items()):
        tk.Label(info_frame, text=item[0], pady=15, fg="yellow", font="Arial 15 bold", bg="#660033").grid(row=i, column=0, sticky='w')
        tk.Label(info_frame, text=":", fg="yellow", padx=50, font="Arial 15 bold", bg="#660033").grid(row=i, column=1)
        val = "---" if (item[1]=="") else item[1]
        tk.Label(info_frame, text=val, fg="white", font="Arial 15", bg="#660033").grid(row=i, column=2, sticky='w')


def startRecognitionMissingPeople():
    global img_read, img_label

    if(img_label == None):
        messagebox.showerror("Error", "No image selected. ")
        return
    
    messagebox.showinfo("Show Information", "Under Process")
    
    crims_found_labels = []
    for wid in right_frame.winfo_children():
        wid.destroy()

    frame = cv2.flip(img_read, 1, 0)
    #gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    face_coords = detect_faces(gray_frame)

    if (len(face_coords) == 0):
        messagebox.showerror("Error", "Image doesn't contain any face or face is too small.")
    else:
        (known_face_names, known_face_encodings) = train_model_for_missing_people()
        #print(names)
        print('Training Successful. Detecting Faces')
        (frame, name) = recognize_face(frame,known_face_names,known_face_encodings)

        img_size = left_frame.winfo_height() - 40
        #frame = cv2.flip(frame, 1, 0)
        showImage(frame, img_size)
        messagebox.showinfo("Show Information", "Process Finished")
        if (len(name) == 0):
            messagebox.showerror("Error", "No reports found.")
            return
        print(name)

        for i in range(len(name)):
            print("lem ", len(name))
            print("name "+name[i], len(name))
            (ide,data) = retrieveMissingPeopleData(name[i])
            crims_found_labels.append(tk.Label(right_frame, text=data['Name'], bg="orange",
                                            font="Arial 15 bold", pady=20))
            crims_found_labels[i].pack(fill="x", padx=20, pady=10)
            crims_found_labels[i].bind("<Button-1>", lambda e, name=name[i]:showMissingPeople(name))

def startRecognition():
    global img_read, img_label

    if(img_label == None):
        messagebox.showerror("Error", "No image selected. ")
        return

    messagebox.showinfo("Show Information","Under Process")
    crims_found_labels = []
    for wid in right_frame.winfo_children():
        wid.destroy()

    frame = cv2.flip(img_read, 1, 0)
    #gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    face_coords = detect_faces(gray_frame)

    if (len(face_coords) == 0):
        messagebox.showerror("Error", "Image doesn't contain any face or face is too small.")
    else:
        (known_face_names, known_face_encodings) = train_model()
        #print(names)
        print('Training Successful. Detecting Faces')
        messagebox.showinfo("Show Information","Process Finished")
        (frame, name) = recognize_face(frame,known_face_names,known_face_encodings)

        img_size = left_frame.winfo_height() - 40
        #frame = cv2.flip(frame, 1, 0)
        showImage(frame, img_size)

        if (len(name) == 0):
            messagebox.showerror("Error", "No criminal recognized.")
            return
        print(name)

        for i in range(len(name)):
            crims_found_labels.append(tk.Label(right_frame, text=name[i], bg="orange",
                                            font="Arial 15 bold", pady=20))
            crims_found_labels[i].pack(fill="x", padx=20, pady=10)
            crims_found_labels[i].bind("<Button-1>", lambda e, name=name[i]:showCriminalProfile(name))


def selectImage():
    global left_frame, img_label, img_read
    for wid in right_frame.winfo_children():
        wid.destroy()

    filetype = [("images", "*.jpg *.jpeg *.png")]
    path = filedialog.askopenfilename(title="Choose a image", filetypes=filetype)

    if(len(path) > 0):
        img_read = cv2.imread(path)

        img_size =  left_frame.winfo_height() - 40
        showImage(img_read, img_size)

def selectvideos():
    global left_frame, img_label, img_read
    for wid in right_frame.winfo_children():
        wid.destroy()

    filetype = [("videos", "*.mp4")]
    path = filedialog.askopenfilename(title="Choose a video", filetypes=filetype)
    source = path
    print(path)
    cam = cv2.VideoCapture(path)

    try:
        # creating a folder named data
        if not os.path.exists('data'):
            os.makedirs('data')
    # if not created then raise error
    except OSError:
        print ('Error: Creating directory of data')
    # frame 
    currentframe = 0

    messagebox.showinfo("Show Information","Under Process")
    for i in range(0, 200):
        # reading from frame
        ret,frame = cam.read()
        print(ret)
        if ret: 
            # if video is still left continue creating images
            name = './data/frame' + str(currentframe) + '.jpg'
            print ('Creating...' + name)

            cv2.imwrite(name, frame)

            currentframe += 1
            print("hi")
        else:
            print("hello")
        
            break
    # img_read = cv2.imread("outputs/object-detection.jpg")
    # img_size = 200
    # showImage(img_read, img_size)
    messagebox.showinfo("Show Information","Completed")
    cam.release() 
    cv2.destroyAllWindows() 

    if(len(path) > 0):
        img_read = cv2.imread(path)


## Detection Page ##
def getPage2():
    global active_page, left_frame, right_frame, img_label, heading
    img_label = None
    active_page = 2
    pages[2].lift()

    basicPageSetup(2)
    heading.configure(text="Detect Criminal")
    right_frame.configure(text="Detected Criminals")

    btn_grid = tk.Frame(left_frame, bg="#660033")
    btn_grid.pack()

    tk.Button(btn_grid, text="Select Image", command=selectImage, font="Arial 15 bold", padx=20, bg="#2196f3",
            fg="white", pady=10, bd=0, highlightthickness=0, activebackground="#091428",
            activeforeground="white").grid(row=0, column=0, padx=25, pady=25)
    tk.Button(btn_grid, text="Recognize", command=startRecognition, font="Arial 15 bold", padx=20, bg="#2196f3",
           fg="white", pady=10, bd=0, highlightthickness=0, activebackground="#091428",
           activeforeground="white").grid(row=0, column=1, padx=25, pady=25)

def findPerson():
    global active_page, left_frame, right_frame, img_label, heading
    img_label = None
    active_page = 2
    pages[2].lift()

    basicPageSetup(2)
    heading.configure(text="Find Missing People")
    right_frame.configure(text="Missing Reports")

    btn_grid = tk.Frame(left_frame, bg="#660033")
    btn_grid.pack()

    tk.Button(btn_grid, text="Select Image", command=selectImage, font="Arial 15 bold", padx=20, bg="#2196f3",
            fg="white", pady=10, bd=0, highlightthickness=0, activebackground="#091428",
            activeforeground="white").grid(row=0, column=0, padx=25, pady=25)
    tk.Button(btn_grid, text="Recognize", command=startRecognitionMissingPeople, font="Arial 15 bold", padx=20, bg="#2196f3",
           fg="white", pady=10, bd=0, highlightthickness=0, activebackground="#091428",
           activeforeground="white").grid(row=0, column=1, padx=25, pady=25)
    
def on_cancel(self):
        self.destroy()
 
def getPage71():
    global active_page, left_frame, right_frame, heading, img_label, df
    img_label = None
    opt_menu=None
    menu_var = tk.StringVar(root)
    active_page = 3
    pages[3].lift()
    basicPageSetup(3)

def upLoad():
    global img_list, current_slide, slide_caption, slide_control_panel
    img_read=cv2.imread("image1.png")
    lab=Label(left_frame,text='image')
    img_size=200
    showImage(img_read,img_size)
    lab.pack()

def videoLoop(path, known_face_names, known_face_encodings):
    global thread_event, left_frame, webcam, img_label
    webcam = cv2.VideoCapture(path)
    old_recognized = []
    crims_found_labels = []
    img_label = None
    messagebox.showinfo("Show Information","Process Finished")
    
    try:
        while not thread_event.is_set():
                # Loop until the camera is working
                while (True):
                    # Put the image from the webcam into 'frame'
                    (return_val, frame) = webcam.read()
                    print("return_val ",return_val)
                    if (return_val == True):
                        break
                    else:
                        print("Failed to open webcam. Trying again...")

                # Flip the image (optional)
                frame = cv2.flip(frame, 1, 0)
                # Convert frame to grayscale
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Detect Faces
                face_coords = detect_faces(gray_frame)
                (frame, names) = recognize_face(frame, known_face_names, known_face_encodings)

                # Recognize Faces
                recog_names = [item[0] for item in names]
                if(recog_names != old_recognized):
                    for wid in right_frame.winfo_children():
                        wid.destroy()
                    del(crims_found_labels[:])

                    for i in range(len(names)):
                        crims_found_labels.append(tk.Label(right_frame, text=names[i], bg="orange",
                                                font="Arial 15 bold", pady=20))
                        crims_found_labels[i].pack(fill="x", padx=20, pady=10)
                        crims_found_labels[i].bind("<Button-1>", lambda e, name=names[i]:showCriminalProfile(name))
                        
                    old_recognized = recog_names

                # Display Video stream
                img_size = min(left_frame.winfo_width(), left_frame.winfo_height()) - 20

                showImage(frame, img_size)

    except RuntimeError:
        print("[INFO]Caught Runtime Error")
    except tk.TclError:
        print("[INFO]Caught Tcl Error")

def showImage1(frame, img_size):
    global img_label, left_frame

    img = cv2.resize(frame, (img_size, img_size))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(img)
    if (img_label == None):
        img_label = tk.Label(right_frame, image=img, bg="#660033")
        img_label.image = img
        img_label.pack(padx=20)
    else:
        img_label.configure(image=img)
        img_label.image = img


def a1():
    import pp
    
def violence():
    global active_page, left_frame, right_frame, img_label, heading
    img_label = None
    active_page = 2
    pages[2].lift()

    basicPageSetup(2)
    heading.configure(text="Detect Criminal")
    right_frame.configure(text="Detected Criminals")

    btn_grid = tk.Frame(left_frame, bg="#660033")
    btn_grid.pack()
    
     
    img_read = cv2.imread("outputs/object-detection.jpg")
    img_size = 200
    showImage1(img_read, img_size)

    tk.Button(btn_grid, text="Select Video", command=selectvideos, font="Arial 15 bold", padx=20, bg="#2196f3",
            fg="white", pady=10, bd=0, highlightthickness=0, activebackground="#091428",
            activeforeground="white").grid(row=0, column=0, padx=25, pady=25)
    # tk.Button(btn_grid, text="Recognize", command=startRecognition, font="Arial 15 bold", padx=20, bg="#2196f3",
    #       fg="white", pady=10, bd=0, highlightthickness=0, activebackground="#091428",
    #       activeforeground="white").grid(row=1, column=0, padx=25, pady=25)
    tk.Button(btn_grid, text="Recognize", command=a1, font="Arial 15 bold", padx=20, bg="#2196f3",
           fg="white", pady=10, bd=0, highlightthickness=0, activebackground="#091428",
           activeforeground="white").grid(row=0, column=1, padx=25, pady=25)


def selectvideo():
    global left_frame, img_label, img_read
    for wid in right_frame.winfo_children():
        wid.destroy()

    filetype = [("video", "*.mp4 *.mkv")]
    path = filedialog.askopenfilename(title="Choose a video", filetypes=filetype)
    p=''
    p=path
    
    if(len(path) > 0):
        # vid_read = cv2.imread(path)
        print("vid_read ", path)
        getPage4(p)
        # img_read = cv2.imread(path)

def getPage4(path):
    p=path
    # print(p)
    global active_page, video_loop, left_frame, right_frame, thread_event, heading
    active_page = 4
    pages[4].lift()

    basicPageSetup(4)
    heading.configure(text="Video Surveillance")
    right_frame.configure(text="Detected Criminals")
    left_frame.configure(pady=40)

    btn_grid = tk.Frame(right_frame, bg="#3E3B3C")
    btn_grid.pack()
    messagebox.showinfo("Show Information","Under Process")
    (names, model) = train_model()
    print('Training Successful. Detecting Faces')
    
    thread_event = threading.Event()
    thread = threading.Thread(target=videoLoop, args=(p, names, model))
    thread.start()

## video surveillance Page ##
def getPage3():
    global active_page, video_loop, left_frame, right_frame, thread_event, heading
    active_page = 3
    pages[3].lift()

    basicPageSetup(3)
    heading.configure(text="Video Surveillance")
    # right_frame.configure(text="Detected Criminals")
    # left_frame.configure(pady=40)

    # (known_face_names, known_face_encodings) = train_model()
    # print('Training Successful. Detecting Faces')

    # thread_event = threading.Event()
    # thread = threading.Thread(target=videoLoop, args=(known_face_names, known_face_encodings))
    # thread.start()
    btn_grid = tk.Frame(left_frame,bg="#660033")
    btn_grid.pack()

    tk.Button(btn_grid, text="Select Video", command=selectvideo, font="Arial 15 bold", padx=20, bg="#2196f3",
            fg="white", pady=10, bd=0, highlightthickness=0, activebackground="#091428",
            activeforeground="white").grid(row=0, column=0, padx=25, pady=25)
    tk.Button(btn_grid, text="Start Webcam", command=startWebcamRecognition, font="Arial 15 bold", padx=20, bg="#2196f3",
           fg="white", pady=10, bd=0, highlightthickness=0, activebackground="#091428",
           activeforeground="white").grid(row=0, column=1, padx=25, pady=25)

def startWebcamRecognition():
    global left_frame, img_label, img_read, active_page, thread_event
    for wid in right_frame.winfo_children():
        wid.destroy()
    
    active_page = 4
    pages[4].lift()

    basicPageSetup(4)
    heading.configure(text="Video Surveillance")
    right_frame.configure(text="Detected Criminals")
    left_frame.configure(pady=40)

    btn_grid = tk.Frame(right_frame, bg="#3E3B3C")
    btn_grid.pack()
    sfr = SimpleFacerec()
    messagebox.showinfo("Show Information","Under Process")
    for (subdirs, dirs, files) in os.walk('face_samples'):
        for subdir in dirs:
            subjectpath = os.path.join('face_samples', subdir)
            sfr.load_encoding_images(subjectpath + '\\', subdir)
            
            
    print('Training Successful. Detecting Faces')
    
    thread_event = threading.Event()
    thread = threading.Thread(target=video, args=(1,sfr))
    thread.start()     
  
def video(p,sfr):
    global thread_event, left_frame, webcam, img_label
    # filetype = [("video", "*.mp4 *.mkv")]
    # path = filedialog.askopenfilename(title="Choose a video", filetypes=filetype)
    # root = Tk()
    # master.geometry('1500x900+200+100')
    # v = StringVar(root, "1")
    # # Dictionary to create multiple buttons
    # values = {"RadioButton 1" : "1",
    #       "RadioButton 2" : "2",
    #       "RadioButton 3" : "3"}
 
    # # Loop is used to create multiple Radiobuttons
    # # rather than creating each button separately
    # for (text, value) in values.items():
    #     Radiobutton(root, text = text, variable = v,
    #             value = value, indicator = 0,
    #             background = "light blue", command=lambda: setPath(value)).pack(fill = X, ipady = 5)
    
    # def setPath(v):
    #     p = v
    #     root.destroy
       
    
    # print("Webcam ",p)
    
    webcam = cv2.VideoCapture(1)
    old_recognized = []
    crims_found_labels = []
    img_label = None
    messagebox.showinfo("Show Information","Process Finished")
    try:
        while not thread_event.is_set():
            # Loop until the camera is working
            while (True):
                # Put the image from the webcam into 'frame'
                (return_val, frame) = webcam.read()
                face_locations, face_names = sfr.detect_known_faces(frame)
                
                for face_loc, name in zip(face_locations, face_names):
                    y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
                    cv2.putText(frame, name,(x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)
                        
                img_size = min(left_frame.winfo_width(), left_frame.winfo_height()) - 20

                showImage(frame, img_size)    
                print("return_val ",return_val)
                # if (return_val == True):
                #     break
                # else:
                #     print("Failed to open webcam. Trying again...")
            
            # # Flip the image (optional)
            # frame = cv2.flip(frame, 1, 0)
            # # Convert frame to grayscale
            # gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # # Detect Faces
            # face_coords = detect_faces(gray_frame)
            # (frame, names) = recognize_face(frame, known_face_names, known_face_encodings)

            # # Recognize Faces
                recog_names = [item[0] for item in face_names]
                if(recog_names != old_recognized):
                    for wid in right_frame.winfo_children():
                        wid.destroy()
                    del(crims_found_labels[:])

                    for i in range(len(face_names)):
                        if(face_names[i] != 'Unknown') :
                            crims_found_labels.append(tk.Label(right_frame, text=face_names[i], bg="orange",
                                            font="Arial 15 bold", pady=20))
                            crims_found_labels[i].pack(fill="x", padx=20, pady=10)
                            crims_found_labels[i].bind("<Button-1>", lambda e, name=face_names[i]:showCriminalProfile(name))

                    old_recognized = recog_names

            # # Display Video stream
            # img_size = min(left_frame.winfo_width(), left_frame.winfo_height()) - 20

            # showImage(frame, img_size)
            
    except RuntimeError:
        print("[INFO]Caught Runtime Error")
    except tk.TclError:
        print("[INFO]Caught Tcl Error")



######################################## Home Page ####################################
tk.Label(pages[0], text="Crime Preventor", fg="white", bg="#660033",
      font="Arial 35 bold", pady=30).pack()

logo = tk.PhotoImage(file = "logo.png")
tk.Label(pages[0], image=logo, bg="#660033").pack()

btn_frame = tk.Frame(pages[0], bg="#660033", pady=30)
btn_frame.pack()

tk.Button(btn_frame, text="Register Criminal", command=getPage1)
tk.Button(btn_frame, text="Detect Criminal", command=getPage2)
tk.Button(btn_frame, text="Video Surveillance", command=getPage3)
tk.Button(btn_frame, text="Find Missing People", command=findPerson)
tk.Button(btn_frame, text="Violence Detection", command=violence)



for btn in btn_frame.winfo_children():
    btn.configure(font="Arial 20", width=15, bg="#000000", fg="white", 
        pady=-2, bd=0, highlightthickness=0, activebackground="#000000", activeforeground="red")
    btn.pack(pady=10)


pages[0].lift()
root.mainloop()
