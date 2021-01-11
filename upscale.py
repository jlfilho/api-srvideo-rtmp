import argparse
import ffmpeg
import sys
import numpy as np
import subprocess 

from model import create_model, sr_genarator
from util import scale_lr_imgs, unscale_hr_imgs, payloader_pre, payloader_pos
from util import start_ffmpeg_reader, start_ffmpeg_writer   
from util import get_video_size, read_frame, return_seg, write_frame


# RTMP server address
rtmpin = r'rtmp://192.168.100.20/live/test'
rtmpout = r'rtmp://localhost:1935/ingest/test'

width, height = get_video_size(rtmpin)
print("Video Format: {}x{}".format(width, height))
fps = 30

commandout = [ 'ffmpeg', '-y','-re',
            '-i', rtmpin,
            '-pix_fmt', 'rgb24', '-r','30',  
            '-f', 'rawvideo', '-' ]

#reader = start_ffmpeg_reader(rtmpin)
reader = subprocess.Popen(commandout, stdout = subprocess.PIPE)#, bufsize=10**8


commandin = ['ffmpeg',
           '-y', '-re',
           '-f', 'rawvideo',
           '-vcodec', 'rawvideo',
           '-pix_fmt', 'rgb24',
           '-s:v', "{}x{}".format(width, height),
           '-r', str(fps),
           '-i', '-',
           '-tune', 'zerolatency',
           '-c:v', 'libx264',
           '-pix_fmt', 'yuv420p',
           '-preset', 'ultrafast',
           '-f', 'flv',
           rtmpout]

#writer = start_ffmpeg_writer(rtmpout,width,height)

# using subprocess and pipe to fetch frame data
writer = subprocess.Popen(commandin, stdin=subprocess.PIPE)


while True:
    in_frame = read_frame(reader, width, height)
    if in_frame is None:
        break
    print(in_frame)
    #write_frame(writer, in_frame)
    #frame_sr = sr_genarator(model,in_frame)
    writer.stdin.write(in_frame)
    
writer.stdin.close()  
writer.wait()  
reader.wait()