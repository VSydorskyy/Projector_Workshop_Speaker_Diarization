import re
from os.path import basename, exists
from os.path import join as pjoin
from os.path import splitext

import pandas as pd

from .main_utils import milliseconds_2_points, read_file


def get_markup_path(audio_name, markup_root, postfix=".cha"):
    path_base = splitext(basename(audio_name))[0]
    markup_path = pjoin(markup_root, path_base[:3], path_base) + postfix
    if exists(markup_path):
        return markup_path
    else:
        markup_path = pjoin(markup_root, "0missing", path_base) + postfix
        if exists(markup_path):
            return markup_path
        else:
            raise RuntimeError(f"{markup_path} was not found")


def get_speaker_start_end_frames(input):
    splitted_line = re.findall(r"(\w+)", input)
    try:
        start, end = splitted_line[-1].split("_")
    except:
        print(input)
    return splitted_line[0], start, end


def get_audio_df_markup(raw_text, sample_name):
    episode_start = re.search("@New Episode", raw_text).end()
    episode_end = re.search("@End", raw_text).start()

    episode_text = raw_text[episode_start:episode_end]
    splitted_text = episode_text.split("\x15")
    # Exclude last "\n"
    n_phrases = len(splitted_text) - 1
    spk_names = []
    starts = []
    ends = []
    for i in range(0, n_phrases, 2):
        spk_name = re.findall(r"\*(\w+)\:", splitted_text[i])[-1]
        t_start, t_end = splitted_text[i + 1].split("_")
        spk_names.append(spk_name)
        starts.append(int(t_start))
        ends.append(int(t_end))

    return pd.DataFrame(
        {
            "sample_name": [sample_name] * len(spk_names),
            "spk_name": spk_names,
            "replica_start": starts,
            "replica_end": ends,
        }
    )


def trim_audio_and_correct_df(markup_df, input_au, input_sr=16_000):
    milliseconds_start = markup_df.replica_start.min()

    au_start = milliseconds_2_points(milliseconds_start, sr=input_sr)
    au_end = milliseconds_2_points(markup_df.replica_end.max(), sr=input_sr)

    markup_df.replica_start -= milliseconds_start
    markup_df.replica_end -= milliseconds_start

    return input_au[au_start:au_end], markup_df
