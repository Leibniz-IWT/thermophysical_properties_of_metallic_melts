import json
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog
import csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def load_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def save_to_csv(data, alloy_key):
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return
    
    alloy_data = data[alloy_key]
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Key", "Value"])
        for key, value in alloy_data.items():
            if isinstance(value, list):
                writer.writerow([key, ', '.join(map(str, value))])
            elif isinstance(value, dict):
                for subkey, subvalue in value.items():
                    writer.writerow([f"{key} - {subkey}", subvalue])
            else:
                writer.writerow([key, value])

def plot_surface_tension(data, alloy_key, plot_frame):
    for widget in plot_frame.winfo_children():
        widget.destroy()
    
    alloy_data = data[alloy_key]
    temperatures = alloy_data["T_superheat"]
    sigma = alloy_data["sigma"]
    sigma_stddev = alloy_data["sigma_stddev"]
    
    fig, ax = plt.subplots()
    ax.errorbar(temperatures, sigma, yerr=sigma_stddev, fmt='o', capsize=5, label="Measured Data")
    
    # Linear model fit line
    sigma_L = alloy_data["model"]["sigma_L"]
    dsigma_dT = alloy_data["model"]["dsigma_dT"]
    T_range = np.linspace(min(temperatures), max(temperatures), 100)
    sigma_fit = sigma_L + dsigma_dT * T_range
    ax.plot(T_range, sigma_fit, 'r--', label="Model Fit")
    
    ax.set_xlabel("Superheat Temperature (°C)")
    ax.set_ylabel("Surface Tension (N/m)")
    ax.set_title(f"Surface tension of {alloy_data['alloy']}")
    ax.legend()
    ax.grid(True)
    
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()
    
    info_text = f"Liquidus Temperature: {alloy_data['liquidus']}°C\n" \
                f"Category: {alloy_data['category']}\n" \
                f"Model: {alloy_data['model']['type']}\n" \
                f"sigma_L: {sigma_L}\n" \
                f"dsigma_dT: {dsigma_dT}\n" \
                f"Experiment ID: {alloy_data['experimentID']}\n" \
                f"Funding: {alloy_data['funding']}\n" \
                f"Reference: {alloy_data['reference']}"
    
    tk.Label(plot_frame, text=info_text, justify=tk.LEFT, wraplength=500).pack(pady=5)
    
    save_button = tk.Button(plot_frame, text="Download CSV", command=lambda: save_to_csv(data, alloy_key))
    save_button.pack(pady=5)

def update_category_list(data, category_combo):
    categories = sorted(set(entry['category'] for entry in data.values()))
    category_combo["values"] = categories

def update_alloy_list(event, data_var, category_combo, alloy_combo):
    data = data_var["data"]
    selected_category = category_combo.get()
    if selected_category:
        alloys = [data[key]['alloy'] for key in data if data[key]['category'] == selected_category]
        alloy_combo["values"] = alloys
        alloy_combo.set("")

def on_select(event, data_var, alloy_combo, plot_frame):
    data = data_var["data"]
    selected_alloy = alloy_combo.get()
    alloy_key = next((key for key in data if data[key]['alloy'] == selected_alloy), None)
    if alloy_key:
        plot_surface_tension(data, alloy_key, plot_frame)

def load_new_database(root, data_var, category_combo, alloy_combo):
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        data = load_data(file_path)
        data_var["data"] = data
        update_category_list(data, category_combo)
        alloy_combo["values"] = []
        category_combo.set("")
        alloy_combo.set("")

def main():
    root = tk.Tk()
    root.title("Select Alloy")
    
    data_var = {"data": {}}
    
    control_frame = tk.Frame(root)
    control_frame.pack(pady=5)
    
    load_button = tk.Button(control_frame, text="Load Database", command=lambda: load_new_database(root, data_var, category_combo, alloy_combo))
    load_button.pack(side=tk.LEFT, padx=5)
    
    category_combo = ttk.Combobox(control_frame, state="readonly")
    category_combo.pack(side=tk.LEFT, padx=5)
    
    alloy_combo = ttk.Combobox(control_frame, state="readonly")
    alloy_combo.pack(side=tk.LEFT, padx=5)
    
    plot_frame = tk.Frame(root)
    plot_frame.pack(pady=10)
    
    category_combo.bind("<<ComboboxSelected>>", lambda event: update_alloy_list(event, data_var, category_combo, alloy_combo))
    alloy_combo.bind("<<ComboboxSelected>>", lambda event: on_select(event, data_var, alloy_combo, plot_frame))
    
    root.mainloop()

if __name__ == "__main__":
    main()
