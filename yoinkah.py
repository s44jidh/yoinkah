import customtkinter as ctk
from tkinter import filedialog
import subprocess
import threading
import os
import sys
import re


if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

YTDLP_BIN = os.path.normpath(os.path.join(APP_DIR, "bin", "yt-dlp.exe"))
FFMPEG_DIR = os.path.normpath(os.path.join(APP_DIR, "bin"))

DEFAULT_PATH = os.path.join(os.path.expanduser("~"), "Downloads", "Yoinkah")
if not os.path.exists(DEFAULT_PATH):
    try: os.makedirs(DEFAULT_PATH, exist_ok=True)
    except: DEFAULT_PATH = APP_DIR

class YoinkahApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        
        self.title("YOINKAH!")
        self.geometry("500x650")
        self.appearance_mode = "dark"
        ctk.set_appearance_mode(self.appearance_mode)
        
        
        self.save_dir = ctk.StringVar(value=DEFAULT_PATH)
        self.format_var = ctk.StringVar(value="mp4")
        self.res_var = ctk.StringVar(value="1080p")

        
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(side="top", fill="x", padx=20, pady=10)

        self.theme_btn = ctk.CTkButton(self.nav_frame, text="🌙", width=35, height=35,
                                       fg_color="transparent", hover_color=("#ddd", "#333"),
                                       text_color=("black", "white"), font=("Arial", 20),
                                       command=self.toggle_theme, corner_radius=20)
        self.theme_btn.pack(side="right")

        
        self.logo = ctk.CTkLabel(self, text="YOINKAH!", font=("Arial Black", 32))
        self.logo.pack(pady=(10, 20))

        self.url_entry = ctk.CTkEntry(self, width=400, height=45, placeholder_text="Paste Link Here...", 
                                      fg_color=("#f0f0f0", "#0a0a0a"), border_color="#222", corner_radius=15)
        self.url_entry.pack(pady=10)

        self.f_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.f_frame.pack(pady=10)
        
        ctk.CTkRadioButton(self.f_frame, text="MP3", variable=self.format_var, value="mp3").grid(row=0, column=0, padx=30)
        ctk.CTkRadioButton(self.f_frame, text="MP4", variable=self.format_var, value="mp4").grid(row=0, column=1, padx=30)

        self.settings_frame = ctk.CTkFrame(self, fg_color=("#ebebeb", "#161616"), border_width=1, border_color="#222", corner_radius=20)
        self.settings_frame.pack(pady=20, padx=40, fill="x")

        
        ctk.CTkLabel(self.settings_frame, text="RES:", font=("Arial", 10, "bold"), text_color="#555").grid(row=0, column=0, padx=15, pady=(15, 5))
        self.res_menu = ctk.CTkOptionMenu(self.settings_frame, 
                                          values=["2160p", "1440p", "1080p", "720p", "480p"], 
                                          variable=self.res_var, 
                                          fg_color=("#333", "#0a0a0a"), 
                                          button_color=("#444", "#222"),
                                          text_color="white", 
                                          corner_radius=10)
        self.res_menu.grid(row=0, column=1, padx=10, pady=(15, 5), sticky="w")

        self.dir_btn = ctk.CTkButton(self.settings_frame, text="CHANGE DIR", command=self.pick_dir, 
                                     fg_color=("#333", "#222"), text_color="white", height=30, width=110, corner_radius=10)
        self.dir_btn.grid(row=1, column=0, pady=(15, 20), padx=(20, 5), sticky="w")

        self.dir_label = ctk.CTkLabel(self.settings_frame, text=self.save_dir.get(), 
                                      font=("Consolas", 9), text_color="#777", wraplength=220, justify="left")
        self.dir_label.grid(row=1, column=1, pady=(15, 20), padx=(5, 20), sticky="w")

        self.status = ctk.CTkLabel(self, text="READY", font=("Arial", 10, "bold"), text_color="#444")
        self.status.pack(pady=(10, 5))

        
        self.btn_container = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_container.pack(pady=20, padx=60, fill="x")

        self.progress_bar = ctk.CTkProgressBar(self.btn_container, height=50, corner_radius=25, 
                                               fg_color=("#ddd", "#2b2b2b"), progress_color=("#333", "#fcfcfc"),
                                               border_width=1, border_color="#333")
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x")

        self.yoink_btn = ctk.CTkButton(self.btn_container, text="YOINK IT", command=self.start_thread, 
                                       fg_color="transparent", text_color=("black", "white"), 
                                       hover=False, font=("Arial", 14, "bold"), height=50, corner_radius=25)
        self.yoink_btn.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)

        
        self.yoink_btn.bind("<Enter>", lambda e: self.on_hover(True))
        self.yoink_btn.bind("<Leave>", lambda e: self.on_hover(False))

        self.check_engines()

    def on_hover(self, hovering):
        if hovering:
            self.yoink_btn.configure(font=("Arial", 15, "bold"))
            self.progress_bar.configure(border_color=("black", "white"))
        else:
            self.yoink_btn.configure(font=("Arial", 14, "bold"))
            self.progress_bar.configure(border_color="#333")

    def toggle_theme(self):
        self.appearance_mode = "light" if self.appearance_mode == "dark" else "dark"
        self.theme_btn.configure(text="☀️" if self.appearance_mode == "light" else "🌙")
        ctk.set_appearance_mode(self.appearance_mode)

    def check_engines(self):
        if not os.path.exists(YTDLP_BIN):
            self.status.configure(text=f"ERROR: ENGINE NOT FOUND", text_color="red")
            self.yoink_btn.configure(state="disabled")

    def pick_dir(self):
        path = filedialog.askdirectory(initialdir=self.save_dir.get())
        if path: 
            path = os.path.normpath(path)
            self.save_dir.set(path)
            self.dir_label.configure(text=path)

    def start_thread(self):
        threading.Thread(target=self.download, daemon=True).start()

    def download(self):
        url = self.url_entry.get().strip()
        if not url: return

        self.yoink_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.status.configure(text="PROCESSING...", text_color=("#333", "white"))

        fmt = self.format_var.get()
        res = self.res_var.get()
        res_num = res.replace("p", "")
        
        out_template = os.path.join(self.save_dir.get(), f"%(title)s [{res}].%(ext)s")
        cmd = [YTDLP_BIN, "--ffmpeg-location", FFMPEG_DIR, "-o", out_template, "--newline", "--no-playlist", "--progress"]
        
        if fmt == "mp3":
            cmd += ["-x", "--audio-format", "mp3", "--audio-quality", "0"]
        else:
            cmd += ["-f", f"bestvideo[height<={res_num}]+bestaudio/best[height<={res_num}]", "--merge-output-format", "mp4"]
        
        cmd.append(url)

        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, 
                                       bufsize=1, universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            for line in process.stdout:
                match = re.search(r'(\d+\.\d+)%', line)
                if match:
                    percent_val = float(match.group(1))
                    self.progress_bar.set(percent_val / 100)
                    self.yoink_btn.configure(text=f"{int(percent_val)}%")
                    
                    if self.appearance_mode == "dark":
                        self.yoink_btn.configure(text_color="black" if percent_val > 50 else "white")
                    else:
                        self.yoink_btn.configure(text_color="white" if percent_val > 50 else "black")

            process.wait()
            if process.returncode == 0:
                self.status.configure(text="YOINKED!", text_color="green")
                self.yoink_btn.configure(text="YOINK IT", text_color=("black", "white"))
                self.progress_bar.set(0)
                self.url_entry.delete(0, 'end')
            else:
                self.status.configure(text="YOINK FAILED", text_color="red")
        except Exception:
            self.status.configure(text="SYSTEM ERROR", text_color="red")

        self.yoink_btn.configure(state="normal")

if __name__ == "__main__":
    app = YoinkahApp()
    app.mainloop()
