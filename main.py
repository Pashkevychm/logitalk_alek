from customtkinter import *
from socket import *
import threading


class RegisterWindow(CTk):
    def __init__(self):
        super().__init__()
        self.username = None
        self.title('Приєднатися до сервера')
        self.geometry('300x300')
        CTkLabel(self, text='Вхід в LogiTalk', font=('Arial', 20, 'bold')).pack(pady=40)
        self.name_entry = CTkEntry(self, placeholder_text='Введіть імʼя')
        self.name_entry.pack()
        self.host_entry = CTkEntry(self, placeholder_text='Введіть хост сервера localhost')
        self.host_entry.pack(pady=5)
        self.port_entry = CTkEntry(self, placeholder_text='Введіть порт сервера 12334 ')
        self.port_entry.pack()
        self.submit_button = CTkButton(self, text='Приєднатися', command=self.start_chat)
        self.submit_button.pack(pady=5)

    def start_chat(self):
        self.username = self.name_entry.get().strip()
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect((self.host_entry.get(), int(self.port_entry.get())))
            hello = f"[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            self.destroy()
            win = MainWindow(self.sock, self.username)
            win.mainloop()
        except Exception as e:
            print(f"Не вдалося підключитися до сервера: {e}")

class SideFrame(CTkFrame):
    def __init__(self, parent: 'MainWindow'):
        super().__init__(parent, width=200, height=parent.winfo_height())
        self.pack_propagate(False)
        self.configure(width=0)
        self.place(x=0, y=0)

        self.entry = CTkEntry(self, placeholder_text="Введіть нікнейм...")
        self.entry.pack(pady=30)
        self.btn = CTkButton(self, text="Встановити нікнейм", command=parent.change_nickname)
        self.btn.pack(pady=10)

        self.label_theme = CTkOptionMenu(self, values=['Темна', 'Світла'], command=parent.change_theme)
        self.label_theme.pack(side='bottom', pady=20)


class MainWindow(CTk):
    def __init__(self, sock, username):
        super().__init__()
        self.geometry('400x300')
        self.title("Назва")

        self.menu_show_speed = 20
        self.is_show_menu = False
        self.frame_width = 0

        self.create_ui()

        self.username = username
        self.sock = sock
        threading.Thread(target=self.recv_message, daemon=True).start()

    def create_ui(self):
        self.frame = SideFrame(self)

        self.btn = CTkButton(self, text='▶', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)

        self.chat_text = CTkTextbox(self, state='disable')
        self.chat_text.place(x=0, y=30)
        self.message_input = CTkEntry(self, placeholder_text='Введіть повідомлення:')
        self.message_input.place(x=0, y=250)
        self.send_button = CTkButton(self, text='▶', width=40, height=30, command=self.send_message)
        self.send_button.place(x=200, y=250)

        self.adaptive_ui()

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.close_menu()
        else:
            self.is_show_menu = True
            self.show_menu()

    def show_menu(self):
        if self.frame_width <= 200:
            self.frame_width += self.menu_show_speed
            self.frame.configure(width=self.frame_width, height=self.winfo_height())
            if self.frame_width >= 30:
                self.btn.configure(width=self.frame_width, text='◀')
        if self.is_show_menu:
            self.after(20, self.show_menu)

    def close_menu(self):
        if self.frame_width >= 0:
            self.frame_width -= self.menu_show_speed
            self.frame.configure(width=self.frame_width)
            if self.frame_width >= 30:
                self.btn.configure(width=self.frame_width, text='▶')
        if not self.is_show_menu:
            self.after(20, self.close_menu)

    def adaptive_ui(self):
        self.chat_text.configure(width=self.winfo_width() - self.frame.winfo_width(),
                                 height=self.winfo_height() - self.message_input.winfo_height() - 30)
        self.chat_text.place(x=self.frame.winfo_width() - 1)

        self.message_input.configure(
            width=self.winfo_width() - self.frame.winfo_width() - self.send_button.winfo_width())
        self.message_input.place(x=self.frame.winfo_width(), y=self.winfo_height() - self.send_button.winfo_height())

        self.send_button.place(x=self.winfo_width() - self.send_button.winfo_width(),
                               y=self.winfo_height() - self.send_button.winfo_height())

        self.after(20, self.adaptive_ui)

    def add_message(self, text):
        self.chat_text.configure(state='normal')
        self.chat_text.insert(END, text + '\n')
        self.chat_text.configure(state='disable')

    def connect(self):
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('localhost', 8080))
            hello = f"[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.add_message(line.strip())
            except:
                break
        self.sock.close()

    def send_message(self):
        message = self.message_input.get()
        data = f"{self.username}: {message}"
        packet = data + "\n"
        if message:
            self.add_message(data)
            try:
                self.sock.sendall(packet.encode())
            except Exception as e:
                self.add_message(f"Не вдалося надіслати повідомлення: {e}")

    def change_theme(self, value):
        if value == "Темна":
            set_appearance_mode("dark")
        else:
            set_appearance_mode("light")

    def change_nickname(self):
        nickname = self.frame.entry.get()
        if nickname:
            self.username = nickname


win = RegisterWindow()
win.mainloop()
