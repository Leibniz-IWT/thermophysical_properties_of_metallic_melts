import json
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
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

def plot_surface_tension(data, alloy_key, frame):
    for widget in frame.winfo_children():
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
    
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()
    
    info_text = f"Liquidus Temperature: {alloy_data['liquidus']}°C\n" \
                f"Model: {alloy_data['model']['type']}\n" \
                f"sigma_L: {sigma_L}\n" \
                f"dsigma_dT: {dsigma_dT}\n" \
                f"Experiment ID: {alloy_data['experimentID']}\n" \
                f"Funding: {alloy_data['funding']}\n" \
                f"Reference: {alloy_data['reference']}"
    
    tk.Label(frame, text=info_text, justify=tk.LEFT, wraplength=500).pack(pady=5)
    
    save_button = tk.Button(frame, text="Download CSV", command=lambda: save_to_csv(data, alloy_key))
    save_button.pack(pady=5)

def on_select(event, data, combo, frame):
    selected_alloy = combo.get()
    alloy_key = next((key for key in data if data[key]['alloy'] == selected_alloy), None)
    if alloy_key:
        plot_surface_tension(data, alloy_key, frame)

def main():
    file_path = "database.json"  # Update with actual file path if needed
    data = load_data(file_path)
    
    root = tk.Tk()
    root.title("Select Alloy")
    
    tk.Label(root, text="Select an alloy:").pack(pady=5)
    
    alloy_names = [data[key]['alloy'] for key in data]
    combo = ttk.Combobox(root, values=alloy_names, state="readonly")
    combo.pack(pady=5)
    
    frame = tk.Frame(root)
    frame.pack(pady=10)
    
    combo.bind("<<ComboboxSelected>>", lambda event: on_select(event, data, combo, frame))
    
    root.mainloop()

if __name__ == "__main__":
    main()
