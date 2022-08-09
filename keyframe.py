import argparse
import os
import shutil
import subprocess
import toml


"""keyframe picker
"""


def dos_path(path):
    buf = path.replace('/mnt/','').replace('/','\\\\')
    return buf[0] + ':' + buf[1:]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('target_file', nargs='*', help='target file path')

    args = parser.parse_args()

    config = 'config.toml'
    conf = toml.load(open(config))

    videos = args.target_file

    for video in videos:
        if video.find(' ') >= 0:
            vprev = video
            video = video.replace(' ','_')
            shutil.move(vprev, video)
        video_dos = dos_path(video)

        csvfile = f'{video}.csv'
        keyframefile = f'{video}_keyframes.txt'
        rangefile = f'{video}_ranges.txt'


        ffprobe = conf['win']['ffprobe']
        avidemux = conf['win']['avidemux']


        if not os.path.isfile(csvfile):
            print('creating keyframe file...')
            subprocess.run(
                f'{ffprobe} -show_frames -select_streams v:0 -show_entries frame=key_frame,pkt_pts_time,coded_picture_number -of csv=p=0 {video_dos} |grep "^1" > {csvfile}',
                shell=True,
                text=True
                    )
