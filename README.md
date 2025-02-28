# SOFA Oto.ini

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3111/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

**SOFA Oto.ini** は、UTAU音源からグラフェム抽出およびg2p変換（PyOpenJTalk利用）を行い、SOFAモジュールによるラベル推定を経て、oto.iniファイルの生成を自動化するツールです。

[English README](README_EN.md)

## 目次

- [概要](#概要)
- [機能](#機能)
- [ディレクトリ構造](#ディレクトリ構造)
- [前提条件](#前提条件)
- [インストール方法](#インストール方法)
- [使用方法](#使用方法)
- [注意事項](#注意事項)
- [貢献](#貢献)
- [ライセンス](#ライセンス)
- [連絡先](#連絡先)

## 概要

SOFA Oto.iniは、UTAU音源ファイル名からグラフェム（仮名）を抽出し、**PyOpenJTalk** によるg2p変換を実施します。その後、**SOFA** モジュールがラベル推定を行い、最終的にoto.iniファイル（例: `oto-SOFAEstimation.ini`）を生成します。なお、PyOpenJTalkはg2p変換のみに特化しており、ラベル推定はSOFAが担当します。

## 機能

- **グラフェム抽出:**  
  音声ファイル名から対象のグラフェムを抽出し、対応するテキストファイルを生成します。

- **g2p変換 (PyOpenJTalk):**  
  抽出されたテキストから、PyOpenJTalkを利用して音素列を生成します。  
  ※ PyOpenJTalkはg2p変換のみを実施します。

- **ラベル推定 (SOFA):**  
  PyOpenJTalkで得られた音素列およびその他の情報を基に、SOFAがラベル推定を行います。

- **oto.ini生成:**  
  推定されたラベル情報を活用して、oto.iniファイルを自動生成します。

## ディレクトリ構造

```
Directory structure:
└── SOFA-oto.ini/
    ├── README.md
    ├── README_EN.md
    ├── LICENSE
    ├── pyproject.toml
    ├── requirements.txt
    ├── uv.lock
    ├── .python-version
    └── src/
        ├── g2p.py
        ├── main.py
        ├── SOFA/
        └── ckpt/
            └── .gitkeep
```

## 前提条件

- **OS:** Windows  
- **Python:** 3.11（3.12未満。3.11での動作を推奨）  
- **依存パッケージ:**  
  必要なパッケージは [pyproject.toml](pyproject.toml) に記載されています。

## インストール方法

1. **リポジトリのクローン**  
   サブモジュールを含めてクローンすることを推奨します。以下のコマンド例をご利用ください：

   ```powershell
   git clone --recursive https://github.com/Lqm1/SOFA-oto.ini
   cd SOFA-oto.ini
   ```

2. **仮想環境の構築とアクティベート**

   ```powershell
   python -m venv .venv
   .venv/scripts/activate
   ```

3. **依存パッケージのインストール**

   ```powershell
   pip install -r requirements.txt
   ```

4. **チェックポイントの配置**  
   `src/ckpt` フォルダ内に、必要な学習済みチェックポイント（例: `step.100000.ckpt`）を配置してください。

## 使用方法

1. **仮想環境のアクティベート**

   ```powershell
   .venv/scripts/activate
   ```

2. **実行**

   `src/main.py` を実行し、対象のUTAU音源が格納されているディレクトリのパスを引数として指定します。例：

   ```powershell
   python src/main.py [音源ディレクトリのパス]
   ```

   実行時、以下のフェーズに分かれた処理が実行されます：

   - **Phase 1:**  
     音声ファイル名からグラフェムを抽出し、テキストファイルを生成します。

   - **Phase 2:**  
     生成されたテキストファイルを基に、PyOpenJTalkでg2p変換を実施し、SOFAモジュールがラベル推定を行います。

   - **Phase 3:**  
     推定されたラベル情報を元に、oto.iniファイル（例: `oto-SOFAEstimation.ini`）を生成します。

   ※ 各フェーズでは、ユーザ入力（VCV oto.ini生成の有無、サフィックスの指定、重複エイリアスの番号付与など）が求められる場合があります。

## 注意事項

- **入力ファイル:**  
  指定ディレクトリには、対象の `.wav` ファイルが配置されている必要があります。ファイル名はグラフェム抽出のための重要な情報を含むため、適切な命名規則に従っているか確認してください。

- **依存パッケージ:**  
  本プロジェクトは多数の外部パッケージに依存しています。インストール時に問題が発生した場合は、Pythonのバージョンや各パッケージのバージョン設定をご確認ください。

- **チェックポイント:**  
  oto.iniの生成には学習済みチェックポイントが必要です。正しいファイルを `src/ckpt` 内に配置してください。

## 貢献

バグ報告、機能追加の提案、プルリクエストなど、どなたからの貢献も歓迎します。まずは [Issue](https://github.com/Lqm1/SOFA-oto.ini/issues) をご利用ください。

## ライセンス

本プロジェクトは [GPL-3.0 License](https://www.gnu.org/licenses/gpl-3.0) のもとで公開されています。

## 連絡先

ご質問やご提案は、[info@lami.zip](mailto:info@lami.zip) までお気軽にご連絡ください。
