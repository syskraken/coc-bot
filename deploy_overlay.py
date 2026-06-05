"""
deploy_overlay.py  —  COC Visual Deployment Planner
────────────────────────────────────────────────────
Can be launched standalone OR by app.py (which passes
env vars to control the output file and window title).

ENV VARS (set by app.py):
  OVERLAY_OUTPUT  — path to write the JSON file (default: deploy_points.json)
  OVERLAY_TITLE   — hint shown in the window title bar

Standalone usage:
  python deploy_overlay.py

Controls:
  Left-click      → place a numbered dot
  Right-click     → remove the last dot
  Refresh         → grab a fresh screenshot
  Clear All       → remove all dots
  Save & Close    → write the JSON file and close
"""

import tkinter as tk
from tkinter import messagebox
import subprocess, time, io, json, os
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFont

# ── Config ────────────────────────────────────────────────────
ADB          = "adb"
DEVICE       = "127.0.0.1:5555"
DEVICE_W     = 1600
DEVICE_H     = 900
SCREENSHOT_W = 1600
SCREENSHOT_H = 900
DISPLAY_W    = 1600
DISPLAY_H    = 900

# Read env vars from app.py (or use defaults for standalone)
POINTS_FILE   = os.environ.get("OVERLAY_OUTPUT", "deploy_points.json")
TITLE_HINT    = os.environ.get("OVERLAY_TITLE",  "COC Deployment Planner")

# ── Coordinate helpers ────────────────────────────────────────

def display_to_device(dx, dy):
    devx = int(dx / SCREENSHOT_W * DEVICE_W)
    devy = int(dy / SCREENSHOT_H * DEVICE_H)
    return devx, devy

def device_to_display(devx, devy):
    dx = int(devx / DEVICE_W * SCREENSHOT_W)
    dy = int(devy / DEVICE_H * SCREENSHOT_H)
    return dx, dy

# ── ADB screenshot ────────────────────────────────────────────

def grab_screenshot():
    try:
        result = subprocess.run(
            [ADB, "-s", DEVICE, "exec-out", "screencap", "-p"],
            capture_output=True, timeout=12
        )
        if not result.stdout or len(result.stdout) < 1000:
            return None
        img = Image.open(io.BytesIO(result.stdout))
        img = img.resize((SCREENSHOT_W, SCREENSHOT_H), Image.LANCZOS)
        return img
    except Exception as e:
        print(f"[overlay] Screenshot error: {e}")
        return None

# ── Dot drawing ───────────────────────────────────────────────

DOT_RADIUS = 10
DOT_COLORS = ["#FF4444", "#FF8C00", "#FFD700", "#44FF88",
              "#00BFFF", "#BF7FFF", "#FF69B4", "#FFFFFF"]

def draw_dots_on_image(pil_img, points_display):
    img  = pil_img.copy()
    draw = ImageDraw.Draw(img)
    for i, (dx, dy) in enumerate(points_display):
        color = DOT_COLORS[i % len(DOT_COLORS)]
        r = DOT_RADIUS
        draw.ellipse([dx-r-2, dy-r-2, dx+r+2, dy+r+2], fill="white", outline="white")
        draw.ellipse([dx-r,   dy-r,   dx+r,   dy+r  ], fill=color,   outline="black")
        label = str(i + 1)
        try:
            font = ImageFont.truetype("arial.ttf", 11)
        except Exception:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), label, font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        draw.text((dx - tw//2, dy - th//2), label, fill="black", font=font)
    return img

# ── Main overlay app ──────────────────────────────────────────

class DeployOverlay:
    def __init__(self, root):
        self.root = root
        self.root.title(f"⚔  {TITLE_HINT}")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")

        self.base_image  = None
        self.tk_image    = None
        self.points_disp = []   # (dx, dy) display space
        self.points_dev  = []   # (devx, devy) device space

        self._build_ui()
        self._try_load_existing_points()
        self.refresh_screenshot()

    # ── UI ────────────────────────────────────────────────────

    def _build_ui(self):
        bar = tk.Frame(self.root, bg="#16213e", pady=6, padx=8)
        bar.pack(fill="x")

        tk.Label(bar, text=f"⚔  {TITLE_HINT}",
                 font=("Consolas", 12, "bold"),
                 fg="#e94560", bg="#16213e").pack(side="left")

        btn = {"bg": "#0f3460", "fg": "#e0e0e0",
               "activebackground": "#e94560", "activeforeground": "white",
               "relief": "flat", "padx": 12, "pady": 4,
               "font": ("Consolas", 10, "bold"), "cursor": "hand2"}

        tk.Button(bar, text="⟳  Refresh",
                  command=self.refresh_screenshot, **btn).pack(side="right", padx=4)
        tk.Button(bar, text="✕  Clear All",
                  command=self.clear_points, **btn).pack(side="right", padx=4)
        tk.Button(bar, text="↩  Undo",
                  command=self.undo_point, **btn).pack(side="right", padx=4)
        tk.Button(bar, text="💾  Save & Close",
                  command=self.save_and_close,
                  bg="#e94560", fg="white", activebackground="#c73652",
                  relief="flat", padx=12, pady=4,
                  font=("Consolas", 10, "bold"), cursor="hand2").pack(side="right", padx=4)

        self.canvas = tk.Canvas(self.root,
                                width=DISPLAY_W, height=DISPLAY_H,
                                bg="#0d0d1a", cursor="crosshair",
                                highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)

        self.status_var = tk.StringVar(value="Connecting to LDPlayer…")
        tk.Label(self.root, textvariable=self.status_var,
                 font=("Consolas", 9), fg="#888",
                 bg="#1a1a2e", anchor="w", padx=8, pady=4).pack(fill="x")

        tk.Label(self.root,
                 text=("Left-click → place dot    Right-click / Undo → remove last    "
                       "Save & Close → write " + os.path.basename(POINTS_FILE)),
                 font=("Consolas", 8), fg="#555", bg="#1a1a2e").pack(pady=(0, 6))

    # ── Screenshot ────────────────────────────────────────────

    def refresh_screenshot(self):
        self.status_var.set("Grabbing screenshot from LDPlayer…")
        self.root.update()
        img = grab_screenshot()
        if img is None:
            self.status_var.set("⚠  Could not connect — is LDPlayer running?")
            img = Image.new("RGB", (SCREENSHOT_W, SCREENSHOT_H), (20, 20, 40))
        self.base_image = img
        self._redraw()
        self.status_var.set(
            f"Screenshot loaded  |  {len(self.points_dev)} point(s)  "
            f"|  saving to: {POINTS_FILE}"
        )

    def _redraw(self):
        if self.base_image is None:
            return
        composite = draw_dots_on_image(self.base_image, self.points_disp)
        self.tk_image = ImageTk.PhotoImage(composite)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

    # ── Click handlers ────────────────────────────────────────

    def on_left_click(self, event):
        dx, dy = event.x, event.y
        devx, devy = display_to_device(dx, dy)
        self.points_disp.append((dx, dy))
        self.points_dev.append((devx, devy))
        self._redraw()
        self.status_var.set(
            f"Point {len(self.points_dev)} → device ({devx},{devy})  |  "
            f"Total: {len(self.points_dev)}"
        )

    def on_right_click(self, event):
        self.undo_point()

    def undo_point(self):
        if self.points_dev:
            self.points_disp.pop()
            removed = self.points_dev.pop()
            self._redraw()
            self.status_var.set(
                f"Removed {removed}  |  Total: {len(self.points_dev)}"
            )

    def clear_points(self):
        self.points_disp.clear()
        self.points_dev.clear()
        self._redraw()
        self.status_var.set("All points cleared.")

    # ── Save / load ───────────────────────────────────────────

    def save_and_close(self):
        if not self.points_dev:
            messagebox.showwarning("No points",
                                   "Place at least one dot before saving.")
            return
        # Always save with "points" key so app.py can load either file
        data = {
            "device_resolution": [DEVICE_W, DEVICE_H],
            "points": [{"x": x, "y": y} for x, y in self.points_dev]
        }
        with open(POINTS_FILE, "w") as f:
            json.dump(data, f, indent=2)
        messagebox.showinfo(
            "Saved",
            f"✔  {len(self.points_dev)} point(s) saved to:\n{POINTS_FILE}\n\n"
            "You can close this window."
        )
        self.root.destroy()

    def _try_load_existing_points(self):
        if not os.path.exists(POINTS_FILE):
            return
        try:
            with open(POINTS_FILE) as f:
                data = json.load(f)
            # Support both "points" and "slots" keys
            raw_pts = data.get("points", data.get("slots", []))
            for pt in raw_pts:
                devx, devy = pt["x"], pt["y"]
                dx, dy = device_to_display(devx, devy)
                self.points_disp.append((dx, dy))
                self.points_dev.append((devx, devy))
        except Exception as e:
            print(f"[overlay] Could not load existing points: {e}")


# ── Entry point ───────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app  = DeployOverlay(root)
    root.mainloop()