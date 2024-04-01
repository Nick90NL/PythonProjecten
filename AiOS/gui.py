import tkinter as tk
from connect import chat_with_gpt

def send_message(event=None):
    user_input = input_entry.get()
    chat_history.insert(tk.END, "Jij: " + user_input + "\n")
    response = chat_with_gpt(user_input)
    chat_history.insert(tk.END, "AI: " + response + "\n")
    input_entry.delete(0, tk.END)

root = tk.Tk()
root.title("ChatGPT")

chat_history = tk.Text(root, width=50, height=20)
chat_history.pack()

input_entry = tk.Entry(root, width=50)
input_entry.pack()
input_entry.bind("<Return>", send_message)

send_button = tk.Button(root, text="Stuur", command=send_message)
send_button.pack()

root.mainloop()