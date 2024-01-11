import hashlib
import pydantic as p

hash = hashlib.blake2s(digest_size=20)


class CaptureFilePath(p.BaseModel):
    dir_name: str
    file_base_name: str


def file_path(trigger_event):
    rank_part = str(int(round(trigger_event.rank * 100, 2))).zfill(3)[0:3]
    timestamp_part = str(trigger_event.timestamp)
    digest_input = f"{rank_part}{timestamp_part}"
    hash.update(digest_input.encode())
    file_digest = hash.hexdigest()
    dir_name = file_digest[0:2]
    file_base_name = f"{rank_part}_{file_digest[2:]}"
    return CaptureFilePath(dir_name=dir_name, file_base_name=file_base_name)


def activate(cam):
    def cb(trigger_event):
        if trigger_event.rank >= 0.5:
            path = file_path(trigger_event)
            print(trigger_event)
            cam.shoot(trigger_event.rank, path)

    return cb
