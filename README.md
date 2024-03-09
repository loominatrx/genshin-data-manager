# genshin-data-manager

<sup>A data manager for Android version of Genshin Impact.</sup>

genshin-data-manager allows you to download Genshin Impact's required data without leaving your Genshin Impact open on your phone.

## Features

- Download amlost all required game assets to run Genshin Impact,
- Download different voice packs,
- Download specific game assets (whether it's the main assets, voice packs, or cutscenes),
- Update the game files directly without removing them,
- Copy some of/all the game files from your PC to your Android phone.

## Requirements

- Working PC (either Windows or Linux, not sure with macOS)
- Genshin Impact's required storage (20 GB+, both on your PC and your phone)
- Python 3.x+
- [Android Platform Tools](https://developer.android.com/tools/releases/platform-tools#downloads)
- [aria2c](https://github.com/aria2/aria2/releases)

## How to use

- Clone this repository using one of the following methods:
    - `git clone https://github.com/loominatrx/genshin-data-manager`
    - or download the source directly [here](https://github.com/loominatrx/genshin-data-manager/archive/refs/heads/new.zip) and extract it somewhere
- Extract Android Platform Tools and aria2c to the `genshin-data-manager` folder
- `cd genshin-data-manager`
- Run `pyhton3 main.py` on your terminal

## Notes

- If your storage speed is painfully slow, resuming downloads takes some time. Especially when you've downloaded tons of files.
- If you opened Genshin for the first time after you installed it or wanted to update the game, you ***MUST*** copy the **main assets, English(US) voice pack, and cutscenes** in order to get into the game.
- You can freely delete the voice packs and the cutscenes to free up some space after getting in the game.
- genshin-data-manager cannot downlaod pre-update files at the moment.