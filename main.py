import asyncio
import ffmpeg
import math
import threading
from pipe import PipeServer

WIDTH=1280
HEIGHT=720
FPS=30
AR=44100 # sample rate
AC=1 # channels

def write_video(video_pipe: PipeServer):
    video_pipe.wait()
    seconds = 5

    for i in range(0, seconds * FPS):
        v = math.floor((i / (FPS * seconds)) * 255)
        frame = bytes((v,v,v,255) * WIDTH * HEIGHT)
        video_pipe.write(frame)

def write_audio(audio_pipe: PipeServer):
    audio_pipe.wait()
    seconds = 5

    for i in range(0, seconds):
        left = 10
        right = 10
        samples = bytes([left, right] * (AC * AR))
        audio_pipe.write(samples)

async def main():
    # Create pipes
    video_pipe = PipeServer(name="video")
    audio_pipe = PipeServer(name="audio")

    # Create inputs
    video_input = ffmpeg.input(video_pipe.path, f="rawvideo", pix_fmt="rgba", s=f"{WIDTH}x{HEIGHT}", r=FPS)
    audio_input = ffmpeg.input(audio_pipe.path, f="s16le", ar=AR, channels=AC)

    # Define ffmpeg args
    stream = ffmpeg.output(
        video_input,
        audio_input,
        "out/merged.mp4",
        **{"c:v": "libx264", "c:a": "aac"},
        vb="2500k",
        pix_fmt="yuv420p"
    )

    # Run ffmpeg async
    print(f'Running ffmpeg with: {stream.compile()}')
    p = ffmpeg.run_async(stream, quiet=False)

    # Write data in parallel
    v = threading.Thread(target=write_video, args=(video_pipe,))
    a = threading.Thread(target=write_audio, args=(audio_pipe,))

    v.start()
    a.start()

    v.join()
    a.join()

    # Release resources
    video_pipe.close()
    audio_pipe.close()

    # Wait for ffmpeg to finish
    out, err = p.communicate()
    code = p.poll()
    if code is not None and code != 0:
        raise Exception('ffmpeg', out, err)
    
    exit()



asyncio.run(main())