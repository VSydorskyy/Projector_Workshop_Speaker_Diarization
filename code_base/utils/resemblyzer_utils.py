from pathlib import Path
from typing import Optional, Union

import librosa
import numpy as np
from resemblyzer import normalize_volume
from resemblyzer.hparams import audio_norm_target_dBFS, sampling_rate


def no_trim_preprocess_wav(
    fpath_or_wav: Union[str, Path, np.ndarray], source_sr: Optional[int] = None
):
    """
    Applies preprocessing operations to a waveform either on disk or in memory such that
    The waveform will be resampled to match the data hyperparameters.

    :param fpath_or_wav: either a filepath to an audio file (many extensions are supported, not
    just .wav), either the waveform as a numpy array of floats.
    :param source_sr: if passing an audio waveform, the sampling rate of the waveform before
    preprocessing. After preprocessing, the waveform's sampling rate will match the data
    hyperparameters. If passing a filepath, the sampling rate will be automatically detected and
    this argument will be ignored.
    """
    # Load the wav from disk if needed
    if isinstance(fpath_or_wav, str) or isinstance(fpath_or_wav, Path):
        wav, source_sr = librosa.load(fpath_or_wav, sr=None)
    else:
        wav = fpath_or_wav

    # Resample the wav
    if source_sr is not None:
        wav = librosa.resample(wav, source_sr, sampling_rate)

    # Apply the preprocessing: normalize volume and shorten long silences
    wav = normalize_volume(wav, audio_norm_target_dBFS, increase_only=True)

    return wav
