import argparse
import csv
import numpy as np
import os
import subprocess
import toml

import mk_avidemuxpy

"""trim videos
"""

def dos_path(path):
    buf = path.replace('/mnt/','').replace('/','\\\\')
    return buf[0] + ':' + buf[1:]

def pick_frame(video_path, frame_num):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception('Error')
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(frame_num))

    ret, frame = cap.read()

    return frame


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('start', type=int, help='start time second')
    parser.add_argument('end', type=int, help='end time second')
    parser.add_argument('target_file', nargs='*', help='target file path')

    args = parser.parse_args()

    config = 'config.toml'
    conf = toml.load(open(config))

    videos = args.target_file
    s = args.start
    e = args.end

    for video in videos:
        video_dos = dos_path(video)

        csvfile = f'{video}.csv'

        ffprobe = conf['win']['ffprobe']
        avidemux = conf['win']['avidemux']


        if not os.path.isfile(csvfile):
            print('creating keyframe file...')
            subprocess.run(
                f'{ffprobe} -show_frames -select_streams v:0 -show_entries frame=key_frame,pkt_pts_time,coded_picture_number -of csv=p=0 {video_dos} |grep "^1" > {csvfile}',
                shell=True,
                text=True
                )

        with open(csvfile) as f:
            cobj = csv.reader(f)
            key_frames = list(cobj)
            np_key_frames = np.array([[int(c[0]), float(c[1]), int(c[2])] for c in key_frames])

        sidx = np_key_frames[:,1].searchsorted(s) - 1
        eidx = np_key_frames[:,1].searchsorted(e)
        if sidx > eidx:
            raise Exception('invalid input')

        print(key_frames[sidx])
        print(key_frames[eidx])
        sframe = key_frames[sidx][1]
        eframe = key_frames[eidx][1]

        script_path = mk_avidemuxpy.mk_avidemuxpy(video, video_dos, [[sframe, eframe],])
        script_dos = dos_path(script_path)

        print('trimming...')

        proc = subprocess.run(f'"{avidemux}" --run "{script_dos}"',
            shell = True,
            text = True
        )
