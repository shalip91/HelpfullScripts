import os
import argparse
import sys
from pytube import YouTube
from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import concatenate_videoclips
from pydub import AudioSegment


DOWNLOAD_FOLDER = str(Path(r"C:\Users") / Path(os.environ['USERNAME']) / Path(r"Downloads"))


def parse_args(input=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--urls", type=str, nargs='+', required=True, help="list of video-urls to download")
    parser.add_argument("-o", "--out_path", type=str, default=DOWNLOAD_FOLDER, help="output folder")
    parser.add_argument("-a", "--audio_only", action='store_true', help="boolean flag for audio only")
    parser.add_argument("-s", "--start_time", type=float, default=None, help="start time as number of sec from the beginning")
    parser.add_argument("-e", "--end_time", type=float, default=None, help="end time as number of sec from the beginning")
    return parser.parse_args(input).__dict__ 

class MediaCroper:
    def __init__(self, path: str):
        self.path = path
        self.new_fname_path = self._new_fname_path()
            
    
    def crop(self, start_time: float, end_time: float):
        _, ext = os.path.splitext(self.path)
        if ext == '.mp4':
            self._crop_video(start_time, end_time)
        elif ext == '.mp3':
            self._crop_mp3(start_time, end_time)
        else:
            raise Exception("unknown file extention")
    
    def _new_fname_path(self):
        base, ext = os.path.splitext(self.path)
        return f'{base}_cropped' + ext

    def _crop_video(self, start_time, end_time):
        clip = VideoFileClip(self.path).subclip(start_time, end_time)
        final_clip = concatenate_videoclips([clip])
        final_clip.write_videofile(self.new_fname_path)
        

    def _crop_mp3(self, start_time, end_time):
        x = Path(self.path).exists()
        sound = AudioSegment.from_mp3(str(Path(self.path)))
        extract = sound[start*1000 : end_time*1000]
        extract.export(self.new_fname_path, format="mp3")

def extract_raw_audio(fname):
    base, ext = os.path.splitext(fname)
    out_name = base + '.mp3'
    clip = VideoFileClip(fname)
    clip.audio.write_audiofile(out_name)
    return out_name
    
    
def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    print(percentage_of_completion)
    
    
def download_video(url, dst_path) -> str:
    chunk_size = 1024
    yt_vid = YouTube(url)
    # yt_vid.register_on_complete_callback(on_progress)
    return str(Path(yt_vid.streams.filter(progressive=True)
                                    .order_by('resolution')
                                    .desc()
                                    .first()
                                    .download(output_path=dst_path)))
    
    
def download_youtube_media(urls: list[str], out_path: str = DOWNLOAD_FOLDER, audio_only: bool = False, start_time: float = None, end_time: float = None) -> str:
    for url in urls:
        while(True):
            try:
                print(f"Downloading: {url}")
                fname = download_video(url, out_path)
                break
            except Exception as e:
                print(e)
        
        if audio_only:
            fname = extract_raw_audio(fname)
        if start_time:
            MediaCroper(fname).crop(start_time, end_time)
            return fname

# debug = [
#     "--urls", "https://www.youtube.com/watch?v=xwNiQYtUhPk",
#     "--out_path", r"C:\Users\shali\OneDrive\Media\Videos\Ski Videos\Tricks" ,
#     # , "https://www.youtube.com/watch?v=8lbRCTfZlTw"
#     # , "https://www.youtube.com/watch?v=Y2lm3ihlF8I"
#     # , "https://www.youtube.com/watch?v=Z1jo_GUVa-g"
    
#     # "--audio_only",
#     "--start_time", "413.5",
#     "--end_time", "415.5"
#     # "--help"
# ] 
# debug = None

def main(args=None):
    arg_dict = parse_args(args)
    download_youtube_media(**arg_dict)
        
            
if __name__ == "__main__":
    main(debug)