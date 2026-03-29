# Sodor Railways Expansion - The Thomas The Tank Engine set for OpenTTD

The Sodor Railways Expansion (OpenTTE) is a train graphis set (newGRF) for OpenTTD, including vehicles from the Thomas The Tank Engine universe

This set is intended to be used as an add-on expansion for BRTrains in order to allow for more complete gameplay, although it can also be played as a standalone set with some limitations. Use alongside other sets outside of the BRTrains group of newGRFs is not supported and you may fine graphical glitches or discrepancies in scale

This newGRF is available under the GPLv2 license, and all contributions are assumed to be offered under the same license.

## Installation
Grab the latest release from the in-game content downloader.

Alternatively get it from the ![Releases](../../releases/) page and copy it into your `OpenTTD/newGRF` folder.

## Compiling from source

### Prerequisites

Python 3.14+ is required to build the project, earlier versions of Python 3 may work but have not been tested

You will also require the following packages, available from PIP
- PyYaml
- Pillow (PIL)
- NML

Currently (due to the use of the "badge" feature which is part of NML trunk but not yet released), a local copy of NML is required. Download this from the OpenTTD Github and place it in the `../nml` folder, one directory level above the folder this application is in. Eg if this project is `development/OpenTTE2`, place NML at `development/nml`. This step will not be necessary once NML has a released version higher than 0.8.1

To build, run the build script with:

```bash
python build.py
```

This will compose images (eg purchase sprites) and generate NML, then collate and compile the NML. Finally it will attempt to copy the newGRF to your `OpenTTD/newgrf` folder if located in the expected location on Windows (with or without OneDrive) or MacOS. Untested on Linux. If the copy fails, simply copy the `build/opentte.grf` file to that folder manually

## Contributing

Pull requests are always welcome, please keep them small and split large changesets into smaller PRs. Discussion on Discord is always useful before changing anything important

## Discussion
For suggestions, requests, bug reports, or general discussion, please use either

- Our TT-Forums thread
https://www.tt-forums.net/viewtopic.php?f=26&t=54189&start=40
- Or the BRTrains Discord https://discord.gg/5yPtsUzzxG

## Credits
- Audigex: Development and artwork
- Fabian/TheThomasFan: Artwork

Honourable memtions to DanMacK, SalvaCottontail, Bazek for their work on the predecessor version 1 project, which shares no code or art with this project but was nevertheless an important part of its developmental history

## License
This project is licensed under the GPLv2 license
See [LICENSE](./LICENSE) for license details