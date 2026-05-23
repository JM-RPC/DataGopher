import tkinter as tk
from tkinter import ttk

# Create main window
window = tk.Tk()
window.geometry("400x350")
window.title("Multiple Selection with Listbox")

# Define dropdown values
values = ["Python", "Java", "C++", "JavaScript", "Go"]

# Create widgets
label = ttk.Label(window, text="Select Programming Languages:")
combobox = ttk.Combobox(window, state="readonly", width=30)
listbox = tk.Listbox(window, selectmode="multiple", exportselection=0, height=6)

# Populate listbox
for value in values:
    listbox.insert(tk.END, value)

# Function to update combobox display
def update_combobox(event=None):
    selected_indices = listbox.curselection()
    selected_values = [listbox.get(idx) for idx in selected_indices]
    combobox.set(", ".join(selected_values))

# Bind selection event
listbox.bind("<<ListboxSelect>>", update_combobox)

# Layout widgets
label.pack(pady=10, anchor="w", padx=20)
combobox.pack(pady=5, padx=20, fill="x")
tk.Label(window, text="Available Options:").pack(pady=(20,5), anchor="w", padx=20)
listbox.pack(pady=5, padx=20, fill="both", expand=True)

window.mainloop()