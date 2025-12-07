import os
import re
import threading
import shutil
from shutil import which
from tkinter import Tk, Button, Label, Entry, CENTER, LEFT, TOP, BOTTOM, X, filedialog, StringVar
from tkinter import ttk

try:
    from pytubefix import YouTube
except Exception:
    from pytube import YouTube

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except Exception:
    PYDUB_AVAILABLE = False

def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    name = name.strip()
    return name or "youtube_download"

def ensure_ffmpeg_available():
    return which("ffmpeg") is not None

def download_audio(url, out_dir, output_format, progress_label, download_button, pause_btn, cancel_btn, pbar):
    download_button.config(state='disabled')
    pause_btn.config(state='normal')
    cancel_btn.config(state='normal')

    try:
        progress_label.config(text="Connecting...")
        yt = YouTube(url)
        title = sanitize_filename(yt.title)
        stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
        if not stream:
            progress_label.config(text="No audio stream found")
            return

        orig_ext = stream.subtype or "m4a"
        tmp_basename = f"{title}_orig.{orig_ext}"
        tmp_path = os.path.join(out_dir, tmp_basename)
        final_basename = f"{title}.{output_format}"
        final_path = os.path.join(out_dir, final_basename)

        progress_label.config(text=f"Downloading original ({orig_ext})...")
        
        stream.download(output_path=out_dir, filename=os.path.basename(tmp_path))
        progress_label.config(text="Download complete")

        
        if output_format.lower() == orig_ext.lower():
            if os.path.exists(final_path):
                os.remove(final_path)
            shutil.move(tmp_path, final_path)
            progress_label.config(text=f"Saved: {final_path}")
        else:
            
            if output_format.lower() == "mp4":
                shutil.move(tmp_path, final_path)
                progress_label.config(text=f"Saved: {final_path}")
            else:
               
                if not PYDUB_AVAILABLE:
                    progress_label.config(text="Install pydub (pip) to enable conversion.")
                    return
                if not ensure_ffmpeg_available():
                    progress_label.config(text="ffmpeg not found. Install ffmpeg and add to PATH.")
                    return

                progress_label.config(text=f"Converting to {output_format}...")
                audio = AudioSegment.from_file(tmp_path)
                audio.export(final_path, format=output_format)
                progress_label.config(text=f"Saved: {final_path}")
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    except Exception as e:
        progress_label.config(text=f"Error: {e}")
    finally:
        download_button.config(state='normal')
        pause_btn.config(state='disabled')
        cancel_btn.config(state='disabled')
        try:
            pbar.stop()
            pbar['value'] = 0
        except Exception:
            pass

# UI actions
def start_audio_download():
    url = url_entry.get().strip()
    if not url:
        progress_label.config(text="Please enter a YouTube URL")
        return
    out_dir = filedialog.askdirectory()
    if not out_dir:
        return
    fmt = format_var.get()
    pbar.start()
    threading.Thread(
        target=download_audio,
        args=(url, out_dir, fmt, progress_label, download_audio_btn, pause_btn, cancel_btn, pbar),
        daemon=True
    ).start()

def toggle_darkmode():
    global dark_on
    dark_on = not dark_on
    if dark_on:
        app.config(bg="#2B2B2B")
        progress_label.config(bg="#2B2B2B", fg="white")
        url_entry.config(bg="#333333", fg="white")
    else:
        app.config(bg="#CECCBE")
        progress_label.config(bg="#CECCBE", fg="black")
        url_entry.config(bg="white", fg="green")

def toggle_pause():
    progress_label.config(text="Pause/resume not implemented")

def cancel_download():
    progress_label.config(text="Cancel not implemented")

# GUI 
app = Tk()
app.title("YouTube Audio Downloader")
app.iconbitmap("Images/icon.ico")
app.geometry("520x320")

dark_on = False

Label(app, text="YouTube Audio Downloader", font=("Arial", 14)).pack(side=TOP, pady=8)

url_entry = Entry(app, justify=CENTER, bd=4, width=60)
url_entry.pack(side=TOP, padx=12)
url_entry.insert(0, "https://www.youtube.com/watch?v=")
url_entry.focus()

format_var = StringVar(value="mp3")
format_frame = ttk.Frame(app)
format_frame.pack(side=TOP, pady=8)
Label(format_frame, text="Select format:").pack(side=LEFT, padx=(0,6))
format_combo = ttk.Combobox(format_frame, textvariable=format_var, values=["mp4", "mp3", "wav"], state="readonly", width=8)
format_combo.pack(side=LEFT)

pbar = ttk.Progressbar(app, orient="horizontal", mode="indeterminate", length=360)
pbar.pack(side=TOP, pady=(10,2))
progress_label = Label(app, text="Ready", bg="#CECCBE")
progress_label.pack(side=TOP, pady=6)

btn_frame = ttk.Frame(app)
btn_frame.pack(side=TOP, pady=6)
download_audio_btn = Button(btn_frame, text="Download Audio", width=18, command=start_audio_download)
download_audio_btn.pack(side=LEFT, padx=6)

pause_btn = Button(app, text="Pause", width=12, command=toggle_pause, state='disabled')
pause_btn.pack(side=TOP, pady=4)
cancel_btn = Button(app, text="Cancel", width=12, command=cancel_download, state='disabled')
cancel_btn.pack(side=TOP, pady=4)

dark_btn = Button(app, text="Toggle Dark Mode", command=toggle_darkmode)
dark_btn.pack(side=BOTTOM, pady=8)

app.mainloop()


