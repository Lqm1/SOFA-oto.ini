# SOFA Oto.ini

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3111/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

**SOFA Oto.ini** is a tool that automates the generation of `oto.ini` files by extracting graphemes from UTAU voicebanks, performing g2p conversion using PyOpenJTalk, and estimating labels with the SOFA module.

[日本語READMEはこちら](README.md)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Directory Structure](#directory-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Notes](#notes)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Overview

SOFA Oto.ini extracts graphemes (kana) from UTAU voicebank filenames and performs g2p conversion using **PyOpenJTalk**. Then, the **SOFA** module estimates labels, ultimately generating an `oto.ini` file (e.g., `oto-SOFAEstimation.ini`). Note that PyOpenJTalk is only responsible for g2p conversion, while SOFA handles label estimation.

## Features

- **Grapheme Extraction:**
  Extracts target graphemes from voice file names and generates corresponding text files.

- **g2p Conversion (PyOpenJTalk):**
  Generates phoneme sequences from the extracted text using PyOpenJTalk.
  ※ PyOpenJTalk is used only for g2p conversion.

- **Label Estimation (SOFA):**
  SOFA estimates labels based on the phoneme sequences obtained from PyOpenJTalk and other information.

- **oto.ini Generation:**
  Automatically generates an `oto.ini` file using the estimated label information.

## Directory Structure

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

## Prerequisites

- **OS:** Windows  
- **Python:** 3.11 (below 3.12; 3.11 is recommended)  
- **Dependencies:**  
  Required packages are listed in [pyproject.toml](pyproject.toml).

## Installation

1. **Clone the repository**
   It is recommended to clone with submodules. Use the following commands:

   ```powershell
   git clone --recursive https://github.com/Lqm1/SOFA-oto.ini
   cd SOFA-oto.ini
   ```

2. **Create and activate a virtual environment**

   ```powershell
   python -m venv .venv
   .venv/scripts/activate
   ```

3. **Install dependencies**

   ```powershell
   pip install -r requirements.txt
   ```

4. **Place checkpoints**
   Place the required pre-trained checkpoints (e.g., `step.100000.ckpt`) in the `src/ckpt` folder.

## Usage

1. **Activate the virtual environment**

   ```powershell
   .venv/scripts/activate
   ```

2. **Run the script**

   Execute `src/main.py`, specifying the path to the directory containing the target UTAU voicebank:

   ```powershell
   python src/main.py [path to voicebank directory]
   ```

   During execution, the following phases will be processed:

   - **Phase 1:**
     Extracts graphemes from voice file names and generates a text file.

   - **Phase 2:**
     Performs g2p conversion using PyOpenJTalk and estimates labels using the SOFA module.

   - **Phase 3:**
     Generates an `oto.ini` file (e.g., `oto-SOFAEstimation.ini`) based on the estimated label information.

   ※ Some phases may require user input, such as enabling VCV oto.ini generation, specifying suffixes, and numbering duplicate aliases.

## Notes

- **Input Files:**
  The specified directory must contain `.wav` files. Ensure that filenames follow appropriate naming conventions, as they are essential for grapheme extraction.

- **Dependencies:**
  This project relies on multiple external packages. If installation issues occur, check the Python version and package settings.

- **Checkpoints:**
  Pre-trained checkpoints are required for `oto.ini` generation. Ensure the correct files are placed in `src/ckpt`.

## Contributing

Bug reports, feature requests, and pull requests are welcome. Please use [Issues](https://github.com/Lqm1/SOFA-oto.ini/issues) for discussions.

## License

This project is licensed under the [GPL-3.0 License](https://www.gnu.org/licenses/gpl-3.0).

## Contact

For inquiries or suggestions, feel free to contact [info@lami.zip](mailto:info@lami.zip).

