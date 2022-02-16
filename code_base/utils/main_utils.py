def milliseconds_2_points(input, sr=16_000):
    if sr % 1000 == 0:
        khz = int(sr / 1000)
        return int(input * khz)
    else:
        return int(input * 1000 / sr)


def read_file(filename):
    with open(filename, encoding="utf-8") as f:
        text_content = f.read()

    return text_content
