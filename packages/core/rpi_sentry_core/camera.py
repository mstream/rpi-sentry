import hashlib
import os


def photo_file_path(trigger_event):
    rank_part = str(int(round(trigger_event["rank"] * 100, 2))).zfill(3)[0:3]
    timestamp_part = str(trigger_event["timestamp"]).zfill(20)[0:20]
    file_name = f"{rank_part}_{timestamp_part}.jpg"
    file_digest = hashlib.md5(file_name.encode()).hexdigest()
    dir_name = file_digest[0:2]
    path = os.path.join(dir_name, file_name)
    print(path)
    return os.path.join(dir_name, file_name)


def take_photo(fs, trigger_event):
    fs.create_file(photo_file_path(trigger_event))
