# Contents
* [About](#about)
  * [Performance](#performance)
  * [Supported audio formats](#supported-audio-formats)
* [Usage](#usage)
  * [Downloading the program](#downloading-the-program)
  * [Program overview](#program-overview)
  * [Setting up Virtual Audio Cable](#setting-up-virtual-audio-cable)
    * [What is Virtual Audio Cable](#what-is-virtual-audio-cable)
    * [Why is VBA needed](#why-is-vba-needed)
    * [Installing VBA](#installing-vba)
* [For developers](#for-developers)
  * [Requirements](#requirements)
  * [Running program from source code](#running-program-from-source-code)
  * [QT layout files](#qt-layout-files)
  * [Contributing](#contributing)
* [License](#license)

# About

![about](readme_images/about.png)

Simple program that keeps track of your saved hot-keys which you link to certain sound files.

When you press hot-key the program plays the sound file to selected sound device.

Idea is to use it in background while you're in voice chat, and you can play meme sounds to your microphone.

## Performance

The program is designed to run in the background without taking much CPU/RAM.

On my system it takes around 17MB, 25MB at most and around 0.3% of CPU - this is with playing maximum (10) of
sounds at the same time.

It can go much higher than 10, it's just an arbitrary number as I don't see why would you torture yourself with more
than 10 sounds playing at the same time.

## Supported audio formats

Depends on your system multimedia backend:

- Windows: [DirectShow](https://docs.microsoft.com/en-us/windows/win32/directshow/supported-formats-in-directshow?redirectedfrom=MSDN)
- Linux: [gstreamer](https://gstreamer.freedesktop.org/features/)
- MacOS:  [QuickTime](https://support.apple.com/en-us/HT201290)

In short depends on your system, but formats that should be supported by all 3 are `wav` and `mp3`

Best way to see if some format is supported is to try to add it and play it,
if it doesn't play your system does not currently have the right dependencies for that format.

# Usage

## Downloading the program

For Windows, you can download pre-built executables found at [releases](https://github.com/albertopoljak/MC-Fart-Mic/releases)

If you wish to run from the source code yourself, or you are in a need for another system other than Windows then see [Running program from source code](#running-program-from-source-code)

## Program overview

TODO

![todo](readme_images/todo.png)

## Setting up Virtual Audio Cable

### What is Virtual Audio Cable

VBA or Virtual Audio Cable is a virtual cable that forwards all audio coming in the cable input to the cable output.

So basically it comes in 2 parts - it has input device (takes sounds in) and output device (plays sound).

Any sound that comes to the input will get forwarded to the output.

Virtual means it's just on software level aka it's a program you install like any else.

### Why is VBA needed

Playing sounds to input device (microphone etc) while being cross-platform is not really an easy task to code.

It's much easier and better to rely on software driver that was made system specific.

Main idea of the program is to emulate playing sounds to the microphone as if you were speaking in it.
Now microphones are usually designed to record something so libraries dealing with them mostly have the ability to do only that.

I did a lot of exploring and tried many libraries including mixing them but none of them were able to do things I needed:

* low performance and memory footprint
* at minimum be able to play mp3
* ability to list input/output devices
* [optional] output to input device somehow

I guess the alternative is to interact with low level system specific code and write the code yourself - so no.

TODO FFMPEG lib might do the trick?

Thus, we use an external program for microphone sound emulation.

### Installing VBA

It depends on your system. TODO

# For developers

## Requirements

Program itself is cross-platform and should be compatible with:

* Windows, Linux, UNIX, OS X


You need Python 3.8 (should work with 3.5+ too but program was made and locked with 3.8 so use that unless you absolutely can't).

In Ubuntu, Mint and Debian you can install Python 3 like this:

    $ sudo apt-get install python3 python3-pip

For other Linux flavors, macOS and Windows, packages are available at http://www.python.org/getit/


This project uses [Pipenv](https://realpython.com/pipenv-guide/) packaging.

If you don't already have pipenv installed, install it in global environment:

    $ pip install pipenv

Then install dependencies:

    $ cd mc_fart_mic
    $ pipenv install

Above commands will set up new environment with required dependencies.


To actually play sound to your microphone (or any **input** device) you need to have third party software driver.
Please see [Setting up Virtual Audio Cable](#setting-up-virtual-audio-cable)

To play device to any **output** device (aka any kind of speaker/headphone etc) you don't need any kind of driver.
But then you will only be able to play sounds to yourself which isn't really anything special.

## Running program from source code

After you're done with [requirements](#requirements) start the program by simply running `main_menu.py`:

```bash
$ cd mc_fart_mic
$ python main_menu.py
```

## QT layout files

Layout files are generated with Qt designer. You can edit them manually but that's the hard way, easier way is to use
Qt designer program where you can just drag&dop elements and can visually immediately see how will the window look.

To use you first need to install development dependencies:

    $ pipenv install --dev

Then either run designer manually or run from pre-made script entry with:

    $ pipenv run designer

When the designer opens just open the layout files and edit as you wish.

# Contributing

Any sort of contribution/discussion is welcome - see the [CONTRIBUTING.md](CONTRIBUTING.md) file for details.

# License

This project is licensed under the GPLv3 License - see the [LICENSE.md](LICENSE.md) file for details.
