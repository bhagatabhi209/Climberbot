import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import os
import uuid

# --- Crack Classification Helper ---
def generate_wall_health_summary(health_edges, health_blur, health_heatmap, orientation, crack_height, crack_width):
    avg_health = (health_edges + health_blur + health_heatmap) / 3

    size_score = crack_height * crack_width
    if size_score < 100:
        crack_type = "Hairline Crack"
        damage_level = "Low"
        depth = "Superficial"
        suggestion = "No urgent action needed. Monitor for expansion."
    elif size_score < 1000:
        crack_type = "Medium Crack"
        damage_level = "Moderate"
        depth = "Surface Penetration"
        suggestion = "Use wall filler or plaster. Inspect nearby areas."
    else:
        crack_type = "Structural Crack"
        damage_level = "High"
        depth = "Possible Structural"
        suggestion = "Consult a civil engineer. Structural support may be required."

    condition = (
        f"The wall has a {crack_type.lower()} with a {orientation.lower()} orientation. "
        f"The damage level is {damage_level} and the crack has a depth classified as '{depth}'. "
        f"Based on image analysis, the wall health is approximately {avg_health:.2f}%. "
        f"Suggested action: {suggestion}"
    )

    return {
        "crack_type": crack_type,
        "damage_level": damage_level,
        "depth": depth,
        "suggestion": suggestion,
        "condition_summary": condition
    }

# --- Image Analysis Function ---
def analyze_wall_image(image_path):
    img_gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img_gray is None:
        messagebox.showerror("Error", "Unable to load image.")
        return

    img_gray = cv2.resize(img_gray, (400, 300))

    blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
    cv2.imwrite("gaussian_blur.png", blur)

    edges = cv2.Canny(blur, 50, 150)
    cv2.imwrite("canny_edges.png", edges)

    combined = cv2.bitwise_or(blur, edges)
    cv2.imwrite("combined.png", combined)

    heatmap_img = cv2.applyColorMap(img_gray, cv2.COLORMAP_JET)
    cv2.imwrite("heatmap.png", heatmap_img)

    crack_pixels = np.count_nonzero(edges)
    total_pixels = edges.size
    crack_percentage = (crack_pixels / total_pixels) * 100

    health_score_edges = max(0, 100 - crack_percentage)
    health_score_blur = max(0, 100 - (np.std(blur) / 255 * 100))
    health_score_heatmap = max(0, 100 - (np.std(img_gray) / 255 * 100))

    crack_height = 20  # placeholder
    crack_width = 5    # placeholder
    orientation = "Vertical"  # placeholder

    summary = generate_wall_health_summary(
        health_edges=health_score_edges,
        health_blur=health_score_blur,
        health_heatmap=health_score_heatmap,
        orientation=orientation,
        crack_height=crack_height,
        crack_width=crack_width
    )

    explanation = summary["condition_summary"]

    return {
        "blur": "gaussian_blur.png",
        "edges": "canny_edges.png",
        "combined": "combined.png",
        "heatmap": "heatmap.png",
        "health": (health_score_edges + health_score_blur + health_score_heatmap) / 3,
        "damage": crack_percentage / 10,
        "depth": summary['depth'],
        "crack_pct": crack_percentage,
        "explanation": explanation
    }

# --- GUI Functions ---
def open_image():
    filepath = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
    if not filepath:
        return

    result = analyze_wall_image(filepath)
    if not result:
        return

    display_images(filepath, result)
    show_summary(result)
    plot_graph(result['health'], result['damage'])
    export_button.config(state="normal")
    export_button.result = result
    export_button.orig_path = filepath

def display_images(original_path, result):
    for widget in img_frame.winfo_children():
        widget.destroy()

    def load_img(path):
        img = Image.open(path)
        img = img.resize((200, 150))
        return ImageTk.PhotoImage(img)

    images = [
        (load_img(original_path), "Original"),
        (load_img(result['blur']), "Gaussian Blur"),
        (load_img(result['edges']), "Canny Edges"),
        (load_img(result['combined']), "Combined"),
        (load_img(result['heatmap']), "Heatmap")
    ]

    for i, (img, title) in enumerate(images):
        panel = tk.Label(img_frame, image=img)
        panel.image = img
        panel.grid(row=0, column=i, padx=5)
        label = tk.Label(img_frame, text=title)
        label.grid(row=1, column=i)

def show_summary(result):
    summary_label.config(fg="black")
    if result['health'] > 80:
        status = "Safe"
        color = "green"
    elif result['health'] > 50:
        status = "Moderate"
        color = "orange"
    else:
        status = "Critical"
        color = "red"

    summary = f"Wall Health: {result['health']:.2f}% ({status})\n"
    summary += f"Damage Score: {result['damage']:.2f}/10\n"
    summary += f"Crack Depth: {result['depth'].upper()}\n\n"
    summary += f"AI Analysis:\n{result['explanation']}"

    summary_label.config(text=summary, fg=color)

def plot_graph(health, damage):
    fig, ax = plt.subplots(figsize=(3, 2))
    categories = ["Health Score", "Damage Score"]
    values = [health, damage * 10]

    if health > 80:
        health_color = 'green'
    elif health > 50:
        health_color = 'orange'
    else:
        health_color = 'red'

    ax.bar(categories, values, color=[health_color, 'red'])
    ax.set_ylim(0, 100)
    ax.set_ylabel('% / 10 scale')
    ax.set_title('Wall Analysis Metrics')
    graph_path = f"graph_{uuid.uuid4().hex}.png"
    plt.tight_layout()
    plt.savefig(graph_path)
    plt.close()

    graph_img = Image.open(graph_path)
    graph_img = graph_img.resize((300, 200))
    graph_img_tk = ImageTk.PhotoImage(graph_img)

    graph_panel.config(image=graph_img_tk)
    graph_panel.image = graph_img_tk
    export_button.graph_path = graph_path

def export_to_pdf():
    result = export_button.result
    original_path = export_button.orig_path
    graph_path = export_button.graph_path

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Wall Analysis Report", ln=True, align='C')
    pdf.ln(10)

    pdf.cell(200, 10, txt="Original & Processed Images", ln=True)
    for img_path in [original_path, result['blur'], result['edges'], result['combined'], result['heatmap']]:
        pdf.image(img_path, w=100)

    pdf.ln(5)
    pdf.cell(200, 10, txt="Graphical Summary", ln=True)
    pdf.image(graph_path, x=30, w=150)

    pdf.ln(5)
    pdf.multi_cell(0, 10, txt=result['explanation'])

    save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if save_path:
        pdf.output(save_path)
        messagebox.showinfo("PDF Exported", f"Saved to {save_path}")

# --- GUI Layout ---
root = tk.Tk()
root.title("Smart Wall Analyzer")
root.geometry("1100x750")

upload_btn = tk.Button(root, text="📂 Upload Wall Image", font=("Arial", 14), bg="#4CAF50", fg="white", command=open_image)
upload_btn.pack(pady=10)

img_frame = tk.Frame(root)
img_frame.pack()

summary_label = tk.Label(root, text="", justify="left", font=("Arial", 12), anchor='w')
summary_label.pack(pady=10)

graph_panel = tk.Label(root)
graph_panel.pack(pady=10)

export_button = tk.Button(root, text="📄 Export Result to PDF", font=("Arial", 12), command=export_to_pdf, state="disabled")
export_button.pack(pady=5)

print("Launching Smart Wall Analyzer GUI...")
root.mainloop()