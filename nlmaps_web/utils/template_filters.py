from pathlib import Path


def asset_exists(static_path):
    path_to_static = (Path(__file__) / '../../static').resolve()
    return (path_to_static / static_path).is_file()


FILTERS = [asset_exists]
