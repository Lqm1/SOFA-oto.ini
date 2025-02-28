import pyopenjtalk
import warnings
import pathlib
import pandas as pd
import re

from SOFA.modules.g2p.base_g2p import DataFrameDataset


class PyOpenJTalkG2P:
    def __call__(self, text: str):
        ph_seq, word_seq, ph_idx_to_word_idx = self._g2p(text)

        # The first and last phonemes should be `SP`,
        # and there should not be more than two consecutive `SP`s at any position.
        assert ph_seq[0] == "SP" and ph_seq[-1] == "SP"
        assert all(
            ph_seq[i] != "SP" or ph_seq[i + 1] != "SP" for i in range(len(ph_seq) - 1)
        )
        return ph_seq, word_seq, ph_idx_to_word_idx

    def _g2p(self, input_text: str):
        word_seq_raw = input_text.strip().split(" ")
        word_seq = []
        word_seq_idx = 0
        ph_seq = ["SP"]
        ph_idx_to_word_idx = [-1]
        for word in word_seq_raw:
            phones = pyopenjtalk.g2p(word, join=False)
            if not phones:
                warnings.warn(f"Word {word} is not in the dictionary. Ignored.")
                continue
            word_seq.append(word)
            for i, ph in enumerate(phones):
                if (i == 0 or i == len(phones) - 1) and ph == "SP":
                    warnings.warn(
                        f"The first or last phoneme of word {word} is SP, which is not allowed. "
                        "Please check your dictionary."
                    )
                    continue
                ph_seq.append(ph)
                ph_idx_to_word_idx.append(word_seq_idx)
            if ph_seq[-1] != "SP":
                ph_seq.append("SP")
                ph_idx_to_word_idx.append(-1)
            word_seq_idx += 1

        return ph_seq, word_seq, ph_idx_to_word_idx

    @staticmethod
    def detach_y(text: str):
        text = re.sub(r"([a-zA-Z])y", r"\1 y", text)
        text = re.sub(r"y([a-zA-Z])", r"y \1", text)
        return text

    def get_dataset(self, wav_paths: list[pathlib.Path]):
        dataset = []
        for wav_path in wav_paths:
            try:
                if wav_path.with_suffix(".txt").exists():
                    with open(wav_path.with_suffix(".txt"), "r", encoding="utf-8") as f:
                        lab_text = f.read().strip()
                    ph_seq, word_seq, ph_idx_to_word_idx = self(lab_text)
                    dataset.append((wav_path, ph_seq, word_seq, ph_idx_to_word_idx))
            except Exception as e:
                e.args = (f" Error when processing {wav_path}: {e} ",)
                raise e
        dataset = pd.DataFrame(
            dataset, columns=["wav_path", "ph_seq", "word_seq", "ph_idx_to_word_idx"]
        )
        return DataFrameDataset(dataset)
