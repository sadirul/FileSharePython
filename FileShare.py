from socket import gethostname, gethostbyname, socket, AF_INET, SOCK_STREAM
from tkinter.filedialog import askopenfilename, askdirectory
from webbrowser import open as open_fb_profile
from tkinter import ttk, NORMAL, DISABLED
from re import search as searchRegx
from PIL import Image, ImageTk
from os import environ, path
from threading import Thread
from random import randint
from tqdm import tqdm
import tkinter as tk

from localStoragePy import localStoragePy
localStorage = localStoragePy('mydb', 'ipaddress')
# localStorage.clear()


regex = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'''

dirname = "C:" + path.join(environ['HOMEPATH'], "Desktop").replace("\\", '/')
SERVER_NAME = gethostname()
SERVER_HOST = gethostbyname(SERVER_NAME)

myport = str(randint(1111, 9999))


def alert(text, color = 'green'):
	error.set(text)
	error_lbl['foreground'] = color
# OPEN DEVELOPER FACEBOOK PROFILE
def open_profile(event):
	open_fb_profile("https://www.facebook.com/sadirul4")

isReceive = False
def chnage_radio_btn():
	alert('File Sharing')
	global isReceive
	value = type_method.get()
	if value == 1:
		isReceive = False
		send_button.configure(state = NORMAL)
		port_entry.configure(state = NORMAL)
		user_entry.configure(state = NORMAL)
		select_button.configure(state = NORMAL)
		save_button.configure(state = DISABLED)
	else:
		isReceive = True
		send_button.configure(state = DISABLED)
		port_entry.configure(state = DISABLED)
		user_entry.configure(state = DISABLED)
		select_button.configure(state = DISABLED)
		save_button.configure(state = NORMAL)
		# receive_file()
		Thread(target = receive_file).start()

def all_normal():
	send_button.configure(state = NORMAL)
	send_button.configure(cursor = 'hand2')
	receive_radio.configure(state = NORMAL)
	send_radio.configure(state = NORMAL)

def send_file(filename, host, port):
	SEPARATOR = "<---->"
	BUFFER_SIZE = 4096
	filesize = path.getsize(filename)
	send_button.configure(state = DISABLED)
	receive_radio.configure(state = DISABLED)
	send_radio.configure(state = DISABLED)
	send_button.configure(cursor = 'no')
	alert('Checking sender info...')
	
	try:
		s = socket(AF_INET, SOCK_STREAM)
		s.connect((host.strip(), int(port.strip())))
		s.send(f"{filename}{SEPARATOR}{filesize}".encode())
		progress = tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
		alert('File sending...')
		with open(filename, "rb") as f:
			count = 0
			while True:
				bytes_read = f.read(BUFFER_SIZE)
				if not bytes_read:
					break
				s.sendall(bytes_read)
				# print(len(bytes_read))
				count += len(bytes_read)
				prgrs = count*100/filesize
				progress_check(prgrs)
				progress.update(len(bytes_read))
				size_title.set(f"Sending : {str(progress).split('|')[2].strip()}")
			progress_check(0)
			alert('File sent successfully')
			size_title.set('')
		s.close()
	except TimeoutError:
		alert("User is not online!", 'red')
	except OSError:
		alert("Unable to send file!", 'red')
	finally:
		all_normal()
		quit()


def select_dirname():
	global dirname
	sel_dirname = askdirectory()
	if sel_dirname:
		dirname = sel_dirname
		save_input.set(dirname)

files_send = None
def select_files():
	global files_send
	files_send = askopenfilename()
	if files_send:
		selet_file_path.set(f"{files_send}")

def send_files_now():
	global regex, files_send
	ipaddress = ip_input.get()
	if not ipaddress:
		alert('Please enter IP address!', 'red')
		quit()
	if not searchRegx(regex, ipaddress):
		alert('Enter valid IP address!', 'red')
		quit()

	port = port_input.get()
	if not port:
		alert('Please enter PORT!', 'red')
		quit()
		print(files_send)
	if not files_send:
		alert('Please select files!', 'red')
		quit()
	try:
		send_file(files_send, ipaddress, port)
	except ConnectionResetError:
		alert("Connection error!", 'red')
		send_button.configure(state = NORMAL)
		quit()

sket_rcv = socket(AF_INET, SOCK_STREAM)
sket_rcv.bind((SERVER_HOST.strip(), int(myport.strip())))
sket_rcv.listen(5)
def receive_file():
	global isReceive, dirname, sket_rcv
	BUFFER_SIZE = 4096
	SEPARATOR = "<---->"
	while True:
		if isReceive:
			try:
				client_socket, address = sket_rcv.accept()
				received = client_socket.recv(BUFFER_SIZE).decode()
				filename, filesize = received.split(SEPARATOR)
				filename = path.basename(filename)
				filesize = int(filesize)
				# print(f"{dirname}/{filename}")
				progress = tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
				with open(f"{dirname}/{filename}", "wb") as f:
					alert('File receiving...')
					count = 0
					while True:
						bytes_read = client_socket.recv(BUFFER_SIZE)
						if not bytes_read:
							break
						f.write(bytes_read)
						progress.update(len(bytes_read))
						# size = round(int(os.stat(f"{dirname}/{filename}").st_size)*100/filesize)
						count += len(bytes_read)
						elapsed = progress.format_dict
						# print(filesize, count)
						size = count*100/filesize
						progress_check(size)
						size_title.set(f"Receiving : {str(progress).split('|')[2].strip()}")
					progress_check(0)
					alert('File received successfully')
					size_title.set('')
				client_socket.close()
			except UnicodeDecodeError:
				continue
			except ValueError:
				continue
		else:
			break
	sket_rcv.close()



def progress_check(percent):
	progress['value'] = percent
	style.configure('text.Horizontal.TProgressbar', text = str(int(percent)) + " %")
	root.update()

def start():
	ipaddress = ip_input.get()
	localStorage.setItem("host", ipaddress)
	Thread(target = send_files_now).start()


# START DESIGN
root = tk.Tk()
root.title("File Sharing")
root.wm_iconbitmap("hicon.ico")
root.geometry("348x510+200+40")
root.resizable(width = False, height = False)
# root.bind("<Key>", key)

# BACKGROUND IMAGE
img = Image.open("hicon.ico")
img = img.resize((85, 85))
photoImg =  ImageTk.PhotoImage(img)
profile_pic = ttk.Label(root, image = photoImg, width=50)
profile_pic.place(x = 130, y = 10)



# ERROR AND SUCCESS LABEL
error = tk.StringVar()
error_lbl = ttk.Label(root, textvariable = error, font = ("Courier", 14), width = 32)
error_lbl.place(x = 10, y = 105)
alert("File Sharing")
# error_lbl['foreground'] = "red"




type_method = tk.IntVar()
send_radio = ttk.Radiobutton(root, text = 'Send', value = 1, variable = type_method, command = chnage_radio_btn)
send_radio.place(x = 10, y = 140)
receive_radio = ttk.Radiobutton(root, text = 'Receive', value = 2, variable = type_method, command = chnage_radio_btn)
receive_radio.place(x = 80, y = 140)



# ERROR AND SUCCESS LABEL
ip = tk.StringVar()
ip_lbl = ttk.Label(root, textvariable = ip, font = ("Courier", 12), width = 32)
ip_lbl.place(x = 10, y = 165)
ip.set("Enter Remote IP:")


# USERNAME ENTERY BOX
ip_input = tk.StringVar()
user_entry = ttk.Entry(root, textvariable = ip_input, font = ("Arial", 10), width = 25, state = 'disabled')
user_entry.place(x = 10, y = 195, height = 30)
# user_entry.bind("<FocusIn>", user_focusin)
# user_entry.bind("<FocusOut>", user_focusout)
ip_input.set(localStorage.getItem('host') if localStorage.getItem('host') else '')


# ERROR AND SUCCESS LABEL
port_label = tk.StringVar()
port_label_lbl = ttk.Label(root, textvariable = port_label, font = ("Courier", 12), width = 32)
port_label_lbl.place(x = 200, y = 165)
port_label.set("PORT:")


# USERNAME ENTERY BOX
port_input = tk.StringVar()
port_entry = ttk.Entry(root, textvariable = port_input, font = ("Arial", 10), width = 19, state = 'disabled')
port_entry.place(x = 200, y = 195, height = 30)
port_entry.insert(tk.END, "5001")



# ERROR AND SUCCESS LABEL
save = tk.StringVar()
save_lbl = ttk.Label(root, textvariable = save, font = ("Courier", 12), width = 32)
save_lbl.place(x = 10, y = 225)
save.set("Save file path:")


# USERNAME ENTERY BOX
save_input = tk.StringVar()
save_button = ttk.Button(root, textvariable = save_input, command = select_dirname, cursor = "", state = 'disabled')
save_button.place(x = 10, y = 250, width = 330, height = 30)
save_input.set(dirname)


# ERROR AND SUCCESS LABEL
select = tk.StringVar()
select_lbl = ttk.Label(root, textvariable = select, font = ("Courier", 12), width = 32)
select_lbl.place(x = 10, y = 285)
select.set("Select file to send:")


# USERNAME ENTERY BOX
selet_file_path = tk.StringVar()
select_button = ttk.Button(root, textvariable = selet_file_path, command = select_files, cursor = "", state = 'disabled')
select_button.place(x = 10, y = 310, width = 330, height = 30)
selet_file_path.set("Select file")





style = ttk.Style(root)
style.layout('text.Horizontal.TProgressbar', 
             [('Horizontal.Progressbar.trough',
               {'children': [('Horizontal.Progressbar.pbar',
                              {'side': 'left', 'sticky': 'ns'})],
                'sticky': 'nswe'}), 
              ('Horizontal.Progressbar.label', {'sticky': ''})])
style.configure('text.Horizontal.TProgressbar', text='0 %')


# PROGRESSBAR
progress = ttk.Progressbar(root, length = 586, orient = tk.HORIZONTAL, mode = 'determinate', style='text.Horizontal.TProgressbar')
progress.place(x = 12, y = 345, height = 20, width = 328)

# # GREEN BUTTON
# ttk.Style().configure("TButton", padding = 6, relief="flat",
#    background = "green",  foreground = "green")

# # RED BUTTON
# ttk.Style().configure("W.TButton", padding = 6, relief="flat",
#    background = "red",  foreground = "red")

send_button = ttk.Button(root, text = "Send", command = start, cursor = "hand2", state = 'disabled')
send_button.place(x = 10, y = 370, width = 330, height = 30)


size_title = tk.StringVar()
size_label = tk.Label(root, textvariable =size_title, font = ("Courier", 8))
size_label.place(x = 10, y = 398)
# size_title.set(f"Sending : 15M/2M")


# VIDEO TITLE
video_title = tk.StringVar()
title_label = tk.Label(root, textvariable =video_title, font = ("Courier", 12), fg = "white", bg = "#282923", width = 35, height = 3)
title_label.place(x = 0, y = 420)
video_title.set(f"Host & Port \n{SERVER_HOST}:{myport}")


developer_name = tk.StringVar()
developed = tk.Label(root, textvariable = developer_name, font = ("Courier", 14), cursor = "hand2", bg = "blue", fg = "white", width = 32)
developed.bind("<Button-1>", open_profile)
developed.place(x = 0, y = 480, height = 30)
developer_name.set("Developed by : Sadirul Islam")

root.mainloop()


