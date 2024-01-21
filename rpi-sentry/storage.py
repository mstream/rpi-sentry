import hashlib
import os
import pathlib

hash = hashlib.blake2s(digest_size=20)


def file_path(timestamp, rank):
    rank_part = str(int(round(rank * 100, 2))).zfill(3)[0:3]
    timestamp_part = str(timestamp)
    digest_input = f"{rank_part}{timestamp_part}"
    hash.update(digest_input.encode())
    file_digest = hash.hexdigest()
    dir_name = file_digest[0:2]
    file_base_name = f"{rank_part}_{file_digest[2:]}"
    return (dir_name, file_base_name)


def prepare_file_path(rank, root_dir_path, timestamp):
    dir_name, file_base_name = file_path(timestamp=timestamp, rank=rank)
    dir_path = os.path.join(root_dir_path, dir_name)
    pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
    return os.path.join(dir_path, f"{file_base_name}.h264")
