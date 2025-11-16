from pytubefix import YouTube

urls =  input("url:")

vid = YouTube(urls)

video_download = vid.streams.get_highest_resolution()
audio_download = vid.streams.get_audio_only()

entry = YouTube(urls).title

print(f"\nVideo found: {entry}\n")

print(f"Downloading Video...")
video_download.download(filename=f"{entry}.mp4")
video_download.download(filename=f"{entry}.mp3")
video_download.download(filename=f"{entry}.wav")
print("audio Complete!")




