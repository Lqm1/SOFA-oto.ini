import sys

sys.path.append("src/SOFA")
sys.path.append("src/SOFA/modules")
import glob
import pathlib
import tqdm
import re
import tomllib
import click
from g2p import PyOpenJTalkG2P
import warnings
import pyopenjtalk
import SOFA.modules.g2p
import SOFA.modules.AP_detector
from SOFA.modules.utils.post_processing import post_processing
from SOFA.modules.utils.export_tool import Exporter
import torch
from SOFA.train import LitForcedAlignmentTask
import lightning as pl
import utaupy


def split_kana_combinations(s):
    pattern = r"([ぁ-んァ-ンヴー][ぁぃぅぇぉゃゅょっァィゥェォャュョッー]*)"
    return re.findall(pattern, s)


with open("pyproject.toml", "rb") as f:
    pyproject = tomllib.load(f)


@click.command()
@click.version_option(version=pyproject["project"]["version"])
@click.argument("voicebank_dir_str", type=click.Path(exists=True, file_okay=False))
def main(voicebank_dir_str: str):
    print(
        f"SOFA oto.ini {pyproject['project']['version']} - Use SOFA to estimate oto.ini."
    )
    print()

    voicebank_dir = pathlib.Path(voicebank_dir_str)
    voicebank_wav_files = glob.glob(str(voicebank_dir / "*.wav"))
    if len(voicebank_wav_files) == 0:
        print("No wav files found in the specified folder.")
        input("Press Enter to exit.")
        return
    generate_vcv_oto_ini_flag = input("Generate VCV oto.ini? (y/n): ") == "y"
    generate_cvvc_oto_ini_flag = input("Generate CVVC oto.ini? (y/n): ") == "y"
    suffix = input("Enter the suffix to add to the after all entries in the oto.ini: ")
    duplicate_alias_numbering = input("Number the duplicate aliases? (y/n): ") == "y"
    if duplicate_alias_numbering:
        duplicate_alias_numbering_limit = int(
            input(
                "Enter the number of duplicate aliases to allow before numbering (Default 100): "
            )
            or "100"
        )
    else:
        duplicate_alias_numbering_limit = 0

    print()
    print("Phase 1: Generating text files...")
    print()

    with tqdm.tqdm(total=len(voicebank_wav_files)) as pbar:
        for wav_file in voicebank_wav_files:
            file_name = pathlib.Path(wav_file).stem
            words = file_name[1:]
            graphemes = split_kana_combinations(words)
            with open(voicebank_dir / f"{file_name}.txt", "w", encoding="utf-8") as f:
                f.write(" ".join(graphemes))
            pbar.update(1)

    print()
    print("Phase 1: Done.")
    print()
    print("Phase 2: Generating label files...")
    print()

    AP_detector_class = SOFA.modules.AP_detector.LoudnessSpectralcentroidAPDetector
    get_AP = AP_detector_class()

    g2p_class = PyOpenJTalkG2P
    grapheme_to_phoneme = g2p_class()

    torch.set_grad_enabled(False)

    model = LitForcedAlignmentTask.load_from_checkpoint("src/ckpt/step.100000.ckpt")
    model.set_inference_mode("force")

    trainer = pl.Trainer(logger=False)

    dataset = grapheme_to_phoneme.get_dataset(
        [pathlib.Path(wav_file) for wav_file in voicebank_wav_files]
    )

    predictions = trainer.predict(model, dataloaders=dataset, return_predictions=True)

    predictions = get_AP.process(predictions)
    predictions, log = post_processing(predictions)

    exporter = Exporter(predictions, log)
    exporter.export(["htk"])

    print()
    print("Phase 2: Done.")
    print()
    print("Phase 3: Generating oto.ini file...")
    print()

    if generate_vcv_oto_ini_flag:
        otoini = utaupy.otoini.OtoIni()
        with tqdm.tqdm(total=len(voicebank_wav_files)) as pbar:
            for wav_file in voicebank_wav_files:
                wav_path = pathlib.Path(wav_file)
                words = wav_path.stem[1:]
                graphemes = split_kana_combinations(words)
                label = utaupy.label.load(
                    str(
                        wav_path.parent
                        / "htk"
                        / "phones"
                        / wav_path.with_suffix(".lab").name
                    ),
                    encoding="utf-8",
                )
                phonemes: list[utaupy.label.Phoneme] = [
                    phoneme for phoneme in label if phoneme.symbol not in ["SP", "AP"]
                ]
                phoneme_like_grapheme_list: list[list[utaupy.label.Phoneme]] = []
                # consonant_flag = False
                # for phoneme in phonemes:
                #     if phoneme.symbol in ["a", "i", "u", "e", "o", "N"]:
                #         if consonant_flag:
                #             phoneme_like_grapheme_list[-1].append(phoneme)
                #         else:
                #             phoneme_like_grapheme_list.append([phoneme])
                #         consonant_flag = False
                #     else:
                #         phoneme_like_grapheme_list.append([phoneme])
                #         consonant_flag = True
                index = 0
                for grapheme in graphemes:
                    ph_raw = PyOpenJTalkG2P.detach_y(pyopenjtalk.g2p(grapheme))
                    if not ph_raw:
                        warnings.warn(
                            f"Grapheme {grapheme} is not in the dictionary. Ignored."
                        )
                        continue
                    phones = ph_raw.split(" ")
                    phoneme_like_grapheme_list.append(
                        phonemes[index : index + len(phones)]
                    )
                    index += len(phones)
                time_order_ratio = 10 ** (-4)
                aliases = []
                for i, (grapheme, phoneme_like_grapheme) in enumerate(
                    zip(graphemes, phoneme_like_grapheme_list)
                ):
                    if len(phoneme_like_grapheme) == 0:
                        pass
                    elif len(phoneme_like_grapheme) == 1:
                        alias = (
                            f"- {grapheme}"
                            if i == 0
                            else f"{phoneme_like_grapheme_list[i - 1][-1].symbol.lower()} {grapheme}"
                        )
                        if alias in aliases:
                            if duplicate_alias_numbering:
                                if (
                                    not aliases.count(alias) + 1
                                    > duplicate_alias_numbering_limit
                                ):
                                    alias += str(aliases.count(alias) + 1)
                        aliases.append(alias)
                        if suffix:
                            alias += suffix
                        oto = utaupy.otoini.Oto()
                        oto.filename = wav_path.stem + ".wav"
                        oto.alias = alias
                        oto.offset = (
                            phoneme_like_grapheme[0].start * time_order_ratio
                            if i == 0
                            else (
                                phoneme_like_grapheme[0].start
                                - (
                                    phoneme_like_grapheme_list[i - 1][-1].end
                                    - phoneme_like_grapheme_list[i - 1][-1].start
                                )
                                * 0.2
                            )
                            * time_order_ratio
                        )
                        oto.overlap = (
                            0.0
                            if i == 0
                            else (
                                phoneme_like_grapheme[0].start * time_order_ratio
                                - oto.offset
                            )
                            / 3
                        )
                        oto.preutterance = (
                            0.0
                            if i == 0
                            else phoneme_like_grapheme[0].start * time_order_ratio
                            - oto.offset
                        )
                        oto.consonant = (
                            phoneme_like_grapheme[0].start * time_order_ratio
                            - oto.offset
                        ) + (
                            (
                                (
                                    (
                                        phoneme_like_grapheme[0].end * time_order_ratio
                                        - oto.offset
                                    )
                                    * 0.8
                                )
                                - (
                                    phoneme_like_grapheme[0].start * time_order_ratio
                                    - oto.offset
                                )
                            )
                            * 0.2
                        )
                        oto.cutoff = (
                            -(
                                phoneme_like_grapheme[0].end * time_order_ratio
                                - oto.offset
                            )
                            * 0.8
                        )
                    elif len(phoneme_like_grapheme) == 2:
                        alias = (
                            f"- {grapheme}"
                            if i == 0
                            else f"{phoneme_like_grapheme_list[i - 1][-1].symbol.lower()} {grapheme}"
                        )
                        if alias in aliases:
                            if duplicate_alias_numbering:
                                if (
                                    not aliases.count(alias) + 1
                                    > duplicate_alias_numbering_limit
                                ):
                                    alias += str(aliases.count(alias) + 1)
                        aliases.append(alias)
                        if suffix:
                            alias += suffix
                        oto = utaupy.otoini.Oto()
                        oto.filename = wav_path.stem + ".wav"
                        oto.alias = alias
                        oto.offset = (
                            phoneme_like_grapheme[0].start * time_order_ratio
                            if i == 0
                            else (
                                phoneme_like_grapheme[0].start
                                - (
                                    phoneme_like_grapheme_list[i - 1][-1].end
                                    - phoneme_like_grapheme_list[i - 1][-1].start
                                )
                                * 0.2
                            )
                            * time_order_ratio
                        )
                        oto.overlap = (
                            0.0
                            if i == 0
                            else (
                                phoneme_like_grapheme[1].start * time_order_ratio
                                - oto.offset
                            )
                            / 3
                        )
                        oto.preutterance = (
                            phoneme_like_grapheme[1].start * time_order_ratio
                            - oto.offset
                        )
                        oto.consonant = (
                            phoneme_like_grapheme[1].start * time_order_ratio
                            - oto.offset
                        ) + (
                            (
                                (
                                    (
                                        phoneme_like_grapheme[1].end * time_order_ratio
                                        - oto.offset
                                    )
                                    * 0.8
                                )
                                - (
                                    phoneme_like_grapheme[1].start * time_order_ratio
                                    - oto.offset
                                )
                            )
                            * 0.2
                        )
                        oto.cutoff = (
                            -(
                                phoneme_like_grapheme[1].end * time_order_ratio
                                - oto.offset
                            )
                            * 0.8
                        )
                    else:
                        alias = (
                            f"- {grapheme}"
                            if i == 0
                            else f"{phoneme_like_grapheme_list[i - 1][-1].symbol.lower()} {grapheme}"
                        )
                        if alias in aliases:
                            if duplicate_alias_numbering:
                                if (
                                    not aliases.count(alias) + 1
                                    > duplicate_alias_numbering_limit
                                ):
                                    alias += str(aliases.count(alias) + 1)
                        aliases.append(alias)
                        if suffix:
                            alias += suffix
                        oto = utaupy.otoini.Oto()
                        oto.filename = wav_path.stem + ".wav"
                        oto.alias = alias
                        oto.offset = (
                            phoneme_like_grapheme[0].start * time_order_ratio
                            if i == 0
                            else (
                                phoneme_like_grapheme[0].start
                                - (
                                    phoneme_like_grapheme_list[i - 1][-1].end
                                    - phoneme_like_grapheme_list[i - 1][-1].start
                                )
                                * 0.2
                            )
                            * time_order_ratio
                        )
                        oto.overlap = (
                            0.0
                            if i == 0
                            else (
                                phoneme_like_grapheme[1].start * time_order_ratio
                                - oto.offset
                            )
                            / 3
                        )
                        oto.preutterance = (
                            phoneme_like_grapheme[1].start * time_order_ratio
                            - oto.offset
                        )
                        oto.consonant = (
                            phoneme_like_grapheme[1].start * time_order_ratio
                            - oto.offset
                        ) + (
                            (
                                (
                                    (
                                        phoneme_like_grapheme[-1].end * time_order_ratio
                                        - oto.offset
                                    )
                                    * 0.8
                                )
                                - (
                                    phoneme_like_grapheme[1].start * time_order_ratio
                                    - oto.offset
                                )
                            )
                            * 0.2
                        )
                        oto.cutoff = (
                            -(
                                phoneme_like_grapheme[-1].end * time_order_ratio
                                - oto.offset
                            )
                            * 0.8
                        )
                    otoini.append(oto)
                pbar.update(1)
        otoini.write(str(voicebank_dir / "oto-SOFAEstimation.ini"))

    # TODO: Generate CVVC oto.ini from .lab
    if generate_cvvc_oto_ini_flag:
        print("CVVC oto.ini generation is not supported yet.")
        input("Press Enter to exit.")

    print()
    print("Phase 3: Done.")
    print()
    input("Press Enter to exit.")


if __name__ == "__main__":
    main()
