import argparse
import os
from glob import glob
from os.path import basename, exists
from os.path import join as pjoin
from os.path import splitext

import librosa
import pandas as pd
import soundfile as sf
from tqdm import tqdm

from code_base.utils import (
    get_audio_df_markup,
    get_markup_path,
    read_file,
    trim_audio,
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "audio_glob", type=str, help="Glob statement for getting all audio samples"
    )
    parser.add_argument(
        "markup_root", type=str, help="Root of the folder with markup",
    )
    parser.add_argument(
        "path_to_processed_data",
        type=str,
        help="Folder where processed data will be stored",
    )
    args = parser.parse_args()

    all_audio_sample_pathes = glob(args.audio_glob)
    new_audio_root = pjoin(args.path_to_processed_data, "audio")
    os.makedirs(args.path_to_processed_data)
    os.makedirs(new_audio_root)

    markup_df = []
    for au_path in tqdm(all_audio_sample_pathes):
        file_conent = read_file(get_markup_path(au_path, args.markup_root))
        corrupted_file = False
        try:
            file_markup_df = get_audio_df_markup(
                file_conent, splitext(basename(au_path))[0]
            )
            if len(file_markup_df) == 0:
                corrupted_file = True
        except:
            corrupted_file = True

        if corrupted_file:
            print(f"Skipping file {au_path}")
            continue

        au, sr = librosa.load(au_path, sr=None)
        au = trim_audio(file_markup_df, au, sr)
        new_au_path = pjoin(new_audio_root, basename(au_path))
        if exists(new_au_path):
            raise RuntimeError(f"{new_au_path} already exists")
        else:
            sf.write(new_au_path, au, sr)
        markup_df.append(file_markup_df)

    markup_df = pd.concat(markup_df).reset_index(drop=True)
    markup_df.to_csv(pjoin(args.path_to_processed_data, "markup.csv"), index=False)
