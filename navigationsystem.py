import tkinter as tk
from tkinter import messagebox, ttk
import googlemaps
import folium
import heapq
import uuid
import webbrowser
from collections import defaultdict
import math
import os

# Backend functions (unchanged)
API_KEY = "AIzaSyCPz2ZjAe3yzRdro4Zq3TaUTCAf-Tw-PoQ"
gmaps = googlemaps.Client(key=API_KEY)

def geocode_address(address):
    result = gmaps.geocode(address)
    if result:
        loc = result[0]['geometry']['location']
        return (loc['lat'], loc['lng'])
    else:
        raise ValueError("Invalid address")

def haversine(coord1, coord2):
    R = 6371000
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def find_closest_node(coord, graph):
    all_nodes = list(graph.keys()) + [n for neighbors in graph.values() for n, _ in neighbors]
    return min(all_nodes, key=lambda node: haversine(coord, node))

def get_route_data(start, end):
    directions = gmaps.directions(start, end, mode='driving')
    steps = directions[0]['legs'][0]['steps']
    graph = defaultdict(list)
    coords = []
    for step in steps:
        start_loc = (step['start_location']['lat'], step['start_location']['lng'])
        end_loc = (step['end_location']['lat'], step['end_location']['lng'])
        distance = step['distance']['value']
        graph[start_loc].append((end_loc, distance))
        coords.append((start_loc, end_loc))
    total_distance = directions[0]['legs'][0]['distance']['value']
    duration = directions[0]['legs'][0]['duration']['text']
    return graph, coords, total_distance, duration

def dijkstra(graph, start, end):
    heap = [(0, start)]
    dist = {start: 0}
    prev = {}
    while heap:
        current_dist, current_node = heapq.heappop(heap)
        if current_node == end:
            break
        for neighbor, weight in graph[current_node]:
            alt = current_dist + weight
            if neighbor not in dist or alt < dist[neighbor]:
                dist[neighbor] = alt
                prev[neighbor] = current_node
                heapq.heappush(heap, (alt, neighbor))
    path, node = [], end
    while node in prev:
        path.insert(0, node)
        node = prev[node]
    if path:
        path.insert(0, start)
    return path, dist.get(end, float('inf'))

def show_map(path_coords):
    m = folium.Map(location=path_coords[0], zoom_start=13)
    folium.Marker(path_coords[0], tooltip="Pickup", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(path_coords[-1], tooltip="Delivery", icon=folium.Icon(color='red')).add_to(m)
    folium.PolyLine(path_coords, color="blue", weight=5).add_to(m)
    m.save("route_map.html")
    webbrowser.open("route_map.html")

def load_delivery_log():
    if os.path.exists("delivery_log.txt"):
        with open("delivery_log.txt", "r") as f:
            return f.read()
    return "No deliveries recorded yet."

def calculate_route():
    pickup = pickup_entry.get()
    delivery = delivery_entry.get()
    client = client_entry.get()
    driver = driver_entry.get()

    try:
        pickup_coords = geocode_address(pickup)
        delivery_coords = geocode_address(delivery)
        graph, segments, total_distance, duration = get_route_data(pickup, delivery)
        start_node = find_closest_node(pickup_coords, graph)
        end_node = find_closest_node(delivery_coords, graph)
        path, _ = dijkstra(graph, start_node, end_node)

        if path:
            delivery_id = str(uuid.uuid4())[:8]
            total_miles = total_distance * 0.000621371
            result = (
                f"Delivery ID: #{delivery_id}\n"
                f"Client: {client}\n"
                f"Driver: {driver}\n"
                f"Total Distance: {total_miles:.2f} mi\n"
                f"Estimated Travel Time: {duration}\n"
                f"Route map saved as route_map.html ✅\n"
            )
            result_text.config(state='normal')
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, result)
            result_text.config(state='disabled')

            with open("delivery_log.txt", "a") as f:
                f.write(f"{delivery_id}, {client}, {driver}, {pickup} -> {delivery}, {total_miles:.2f} mi, {duration}\n")

            show_map(path)
            log_text.config(state='normal')
            log_text.delete(1.0, tk.END)
            log_text.insert(tk.END, load_delivery_log())
            log_text.config(state='disabled')
        else:
            messagebox.showerror("No Route", "No valid route found.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Cute GUI with Purple Theme and Main Menu
root = tk.Tk()
root.title("TBD Navigation System")
root.geometry("1000x720")
root.configure(bg="#f9f5ff")  # Off-white background

# Custom Rounded Button Class
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, width=220, height=50, bg="#d8b9ff", fg="#4b0082"):
        super().__init__(parent, width=width, height=height, bg=parent['bg'], highlightthickness=0)
        self.command = command
        self.bg_color = bg
        self.fg_color = fg
        self.text = text
        self.width = width
        self.height = height
        
        # Draw rounded rectangle with gradient effect
        self.create_oval(10, 10, 50, 50, fill=bg, outline=bg)
        self.create_oval(width-50, 10, width-10, 50, fill=bg, outline=bg)
        self.create_oval(10, height-50, 50, height-10, fill=bg, outline=bg)
        self.create_oval(width-50, height-50, width-10, height-10, fill=bg, outline=bg)
        self.create_rectangle(30, 10, width-30, height-10, fill=bg, outline=bg)
        self.create_rectangle(30, 10, width-30, height-10, fill=bg, outline=bg)
        # Text with playful font
        self.create_text(width//2, height//2, text=text, fill=fg, font=("Comic Sans MS", 14, "bold"))
        
        # Bind click and hover
        self.bind("<Button-1>", lambda e: self.command())
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event):
        self.configure(cursor="hand2")
        # Lighten button on hover
        self.itemconfig(1, fill="#c7a6ff", outline="#c7a6ff")
        self.itemconfig(2, fill="#c7a6ff", outline="#c7a6ff")
        self.itemconfig(3, fill="#c7a6ff", outline="#c7a6ff")
        self.itemconfig(4, fill="#c7a6ff", outline="#c7a6ff")
        self.itemconfig(5, fill="#c7a6ff", outline="#c7a6ff")
        self.itemconfig(6, fill="#c7a6ff", outline="#c7a6ff")
    
    def on_leave(self, event):
        self.configure(cursor="")
        self.itemconfig(1, fill=self.bg_color, outline=self.bg_color)
        self.itemconfig(2, fill=self.bg_color, outline=self.bg_color)
        self.itemconfig(3, fill=self.bg_color, outline=self.bg_color)
        self.itemconfig(4, fill=self.bg_color, outline=self.bg_color)
        self.itemconfig(5, fill=self.bg_color, outline=self.bg_color)
        self.itemconfig(6, fill=self.bg_color, outline=self.bg_color)

# Global variables for view management
current_view = "delivery"
delivery_frame = None
company_frame = None
pickup_entry = None
delivery_entry = None
client_entry = None
driver_entry = None
result_text = None
log_text = None

# View Management Functions
def show_delivery():
    global current_view
    print("Showing delivery frame")
    company_frame.grid_forget()
    delivery_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)
    delivery_frame.lift()
    current_view = "delivery"

def show_company_info():
    global current_view
    print("Showing company info frame")
    delivery_frame.grid_forget()
    company_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)
    company_frame.lift()
    current_view = "company"

# Header
header = tk.Frame(root, bg="#d8b9ff", height=100)
header.pack(fill='x')
header_frame = tk.Frame(header, bg="#d8b9ff")
header_frame.pack(fill='x', padx=20)
header_label = tk.Label(header_frame, text="✨ TBD - Cute Delivery Routes ✨", font=("Comic Sans MS", 24, "bold"), bg="#d8b9ff", fg="#4b0082")
header_label.pack(side='left', pady=30)
company_btn = RoundedButton(header_frame, text="Company Info ℹ️", command=show_company_info, bg="#ffb7c5", fg="#4b0082", width=220, height=50)
company_btn.pack(side='right', pady=30)

# Main content area with grid
main_frame = tk.Frame(root, bg="#f9f5ff")
main_frame.pack(fill='both', expand=True)
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

# Delivery Frame
delivery_frame = tk.Frame(main_frame, bg="#f9f5ff")
# Left Side: Inputs (Cute Card)
left_frame = tk.Frame(delivery_frame, bg="#ffffff", bd=0, relief="flat")
left_frame.pack(side="left", fill="y", padx=(0, 15), pady=10, ipadx=25, ipady=25)
left_frame.configure(highlightbackground="#ffb7c5", highlightcolor="#ffb7c5", highlightthickness=3)

form_title = tk.Label(left_frame, text="📍 Delivery Details", font=("Comic Sans MS", 18, "bold"), bg="#ffffff", fg="#4b0082")
form_title.pack(pady=(20, 15))

fields = ["Pickup Location 🏠", "Delivery Destination 📍", "Client Name 😊", "Delivery Person 🚚"]
entries = []

for field in fields:
    frame = tk.Frame(left_frame, bg="#ffffff")
    frame.pack(fill='x', padx=25, pady=8)
    lbl = tk.Label(frame, text=field, bg="#ffffff", font=("Comic Sans MS", 12, "bold"), fg="#4b0082")
    lbl.pack(anchor='w')
    entry = tk.Entry(frame, width=35, font=("Segoe UI", 12), relief='solid', bd=1, bg="#e6e6fa", fg="#4b0082")
    entry.pack(fill='x', pady=(2, 10))
    entries.append(entry)

pickup_entry, delivery_entry, client_entry, driver_entry = entries

submit_btn = RoundedButton(left_frame, text="Plan Route! 🌟", command=calculate_route, bg="#ffb7c5", fg="#4b0082")
submit_btn.pack(pady=25)

# Right Side: Outputs (Cute Card)
right_frame = tk.Frame(delivery_frame, bg="#ffffff", bd=0, relief="flat")
right_frame.pack(side="right", expand=True, fill="both", padx=(15, 0), pady=10, ipadx=25, ipady=25)
right_frame.configure(highlightbackground="#ffb7c5", highlightcolor="#ffb7c5", highlightthickness=3)

result_title = tk.Label(right_frame, text="🚚 Delivery Summary", font=("Comic Sans MS", 18, "bold"), bg="#ffffff", fg="#4b0082")
result_title.pack(pady=(20, 15))

result_text = tk.Text(right_frame, height=8, state='disabled', bg="#e6e6fa", fg="#4b0082", font=("Segoe UI", 12), relief='solid', bd=1)
result_text.pack(padx=25, pady=(0, 20), fill='x')

history_title = tk.Label(right_frame, text="📜 Delivery History", font=("Comic Sans MS", 18, "bold"), bg="#ffffff", fg="#4b0082")
history_title.pack(pady=(10, 15))

log_text = tk.Text(right_frame, height=10, state='disabled', bg="#e6e6fa", fg="#4b0082", font=("Segoe UI", 12), relief='solid', bd=1)
log_text.pack(padx=25, pady=(0, 20), fill='both', expand=True)

# Preload delivery log
log_text.config(state='normal')
log_text.insert(tk.END, load_delivery_log())
log_text.config(state='disabled')

# Company Info Frame
company_frame = tk.Frame(main_frame, bg="#f9f5ff")
company_content = tk.Frame(company_frame, bg="#ffffff", bd=0, relief="flat")
company_content.pack(padx=50, pady=50, fill='both', expand=True)
company_content.configure(highlightbackground="#ffb7c5", highlightcolor="#ffb7c5", highlightthickness=3)

tk.Label(company_content, text="🌸 About TBD Navigation", font=("Comic Sans MS", 24, "bold"), bg="#ffffff", fg="#4b0082").pack(pady=(20, 20))
info_text = tk.Text(company_content, height=12, bg="#e6e6fa", fg="#4b0082", font=("Segoe UI", 12), relief='solid', bd=1)
info_text.pack(padx=30, pady=20, fill='x')
info_text.config(state='normal')
info_text.insert(tk.END, (
    "Mission: To make deliveries super easy and fun with smart, eco-friendly routes! 🚚✨\n\n"
    "Founded: 2025\n\n"
    "Team Members:\n- Taylor Colbert 🌟\n- Brcye Alexander 🗺️\n- Danielle Devose 📍"
))
info_text.config(state='disabled')
back_btn_company = RoundedButton(company_content, text="Back 🩷", command=lambda: [print("Back button clicked"), show_delivery()], bg="#d8b9ff", fg="#4b0082", width=180, height=50)
back_btn_company.pack(pady=20)

# Initial View
delivery_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)
delivery_frame.lift()
current_view = "delivery"
print("Initial view: delivery frame")

# Footer
footer = tk.Frame(root, bg="#d8b9ff", height=50)
footer.pack(fill='x', side='bottom')
footer_label = tk.Label(footer, text="© 2025 TBD Navigation System 🌸 Made with Love", font=("Comic Sans MS", 10), bg="#d8b9ff", fg="#4b0082")
footer_label.pack(pady=15)

root.mainloop()