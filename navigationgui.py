# GUI setup
root = tk.Tk()
root.title("PathFinderAI - Delivery Route Planner")
root.geometry("600x800")
root.configure(bg='#1e1e1e')

style = ttk.Style()
style.theme_use('clam')
style.configure("TButton", foreground="white", background="#4CAF50", font=("Segoe UI", 10, "bold"))
style.configure("TLabel", background="#1e1e1e", foreground="white", font=("Segoe UI", 10))

icon_label = tk.Label(root, text="🚀 PathFinderAI", font=("Helvetica", 16, "bold"), bg="#1e1e1e", fg="white")
icon_label.pack(pady=10)

form_frame = tk.Frame(root, bg="#1e1e1e")
form_frame.pack(pady=10)

labels = ["Pickup Location:", "Delivery Destination:", "Client Name:", "Deliveryman Name:"]
entries = []

for label_text in labels:
    lbl = tk.Label(form_frame, text=label_text, font=("Segoe UI", 10), anchor="w", bg="#1e1e1e", fg="white")
    lbl.pack(fill='x', padx=20, pady=2)
    entry = tk.Entry(form_frame, width=50)
    entry.pack(padx=20, pady=5)
    entries.append(entry)

pickup_entry, delivery_entry, client_entry, driver_entry = entries

ttk.Button(root, text="Calculate Route", command=calculate_route).pack(pady=15)

result_text = tk.Text(root, height=10, width=70, state='disabled', bg='#2e2e2e', fg='white', relief='solid', borderwidth=1)
result_text.pack(pady=10)

log_title = tk.Label(root, text="📦 Delivery History", font=("Segoe UI", 12, "bold"), bg="#1e1e1e", fg="white")
log_title.pack(pady=(20, 5))

log_text = tk.Text(root, height=10, width=70, state='disabled', bg='#2e2e2e', fg='white', relief='solid', borderwidth=1)
log_text.pack(pady=5)
log_text.config(state='normal')
log_text.insert(tk.END, load_delivery_log())
log_text.config(state='disabled')

root.mainloop()
