import tkinter as tk
from tkinter import colorchooser
import socket
import threading

HOST = '5.tcp.eu.ngrok.io'  # Sunucu adresi
PORT = 13896                 # Sunucu port numarası

def receive_messages(client_socket, chat_text, client_name):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            received_message = data.decode()

            # Gönderenin adını ve mesajı ayır
            sender_name, message = received_message.split(": ", 1)

            if sender_name == client_name:
                # İstemci tarafından gönderilen mesaj
                chat_text.insert(tk.END, f"{message}\n")
            else:
                # Diğer istemcilerden gelen mesaj
                chat_text.insert(tk.END, f"{received_message}\n")

    except ConnectionResetError:
        chat_text.insert(tk.END, "Sunucu bağlantısı kesildi.\n")

def send_message(event=None):
    message = entry_message.get()
    if message.lower() == 'exit':
        root.destroy()
        return
    client_socket.sendall(f"{client_name}: {message}".encode())
    entry_message.delete(0, tk.END)

def change_frame_color():
    color = colorchooser.askcolor(title="choose color")
    if color:
        text_chat.config(bg=color[1])

def connect_to_server():
    global client_socket, client_name
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        client_name = entry_name.get()
        client_socket.sendall(client_name.encode())

        receive_thread = threading.Thread(target=receive_messages, args=(client_socket, text_chat, client_name))
        receive_thread.start()

        entry_name.config(state=tk.DISABLED)
        entry_message.config(state=tk.NORMAL)
        button_send.config(state=tk.NORMAL)

    except ConnectionRefusedError:
        text_chat.insert(tk.END, "Bağlantı reddedildi. Sunucu çalışıyor olabilir mi?\n")

# Tkinter penceresi oluşturma
root = tk.Tk()
root.title("chat app")

# Giriş alanları ve butonlar
label_name = tk.Label(root, text="name:")
label_name.pack(pady=5)
entry_name = tk.Entry(root, width=30)
entry_name.pack(pady=5)

button_connect = tk.Button(root, text="connect", command=connect_to_server)
button_connect.pack(pady=5)

text_chat = tk.Text(root, width=50, height=20)
text_chat.pack(pady=10)

entry_message = tk.Entry(root, width=50)
entry_message.pack(pady=5)

button_send = tk.Button(root, text="send", command=send_message)
button_send.pack(pady=5)

entry_message.bind("<Return>", send_message)

button_change_color = tk.Button(root, text="change background", command=change_frame_color)
button_change_color.pack(pady=5)

# Ana döngüyü başlatma
root.mainloop()