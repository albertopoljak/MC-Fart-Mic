# MC Fart Mic

Simple helper program that keeps track of your saved hot-keys which you link to certain sound files.

When you press hot-key the program plays the sound file to selected sound device.

Idea is to use it in background while you're in voice chat and you can play meme sounds to your microphone.

## Requirements

Program itself is cross-platform and should be compatible with:

* Windows, Linux, UNIX, OS X


You need Python 3.5 or later.

In Ubuntu, Mint and Debian you can install Python 3 like this:

    $ sudo apt-get install python3 python3-pip

For other Linux flavors, macOS and Windows, packages are available at

  http://www.python.org/getit/
 
Aside from Python you also need PyQt5 which you can install from requirements:

    $ pip install -r requirements.txt


To actually play sound to your microphone (or any **input** device) you need to have third party software driver.
Please see [Virtual Audio Cable](#virtual-audio-cable)

To play device to any **output** device (aka any kind of speaker/headphone etc) you don't need any kind of driver.
But then you will only be able to play sounds to yourself which isn't really anything special.


## Virtual Audio Cable

Cross-platform task to program outputting sounds to input device (microphone etc) is not really a small deal.

It's much easier and better to rely on software driver that was made system specific.

#### What is a Virtual Audio Cable

VBA or Virtual Audio Cable is a virtual cable that forwards all audio coming in the cable input to the cable output.

So basically it comes in 2 parts - it has input device and output device. Any sound that comes to input will get forwarded to output.

Virtual means it's just on software level aka it's a program you install like any else.

#### Why is VBA needed

Main idea of the program is to play sounds to output device (microphone). Now microphones are usually designed to **output**
something so libraries dealing with them mostly have the ability to only record.


I did a lot of exploring and tried many libraries including mixing them but none of them were able to do things I needed:

* low performance and memory footprint
* at minimum be able to play mp3
* ability to list input/output devices
* [optional] output to input device somehow

I guess the alternative is to interact with low level system specific code and write the code yourself - so no.

#### Installing VBA

It depends on your system. TODO

## Program usage

To start simply run:

```bash
$ cd mc_fart_mic
$ python main_menu.py
```

## Supported audio formats

Depends on your system multimedia backend:

- Windows: [DirectShow](https://docs.microsoft.com/en-us/windows/win32/directshow/supported-formats-in-directshow?redirectedfrom=MSDN)
- Linux: [gstreamer](https://gstreamer.freedesktop.org/features/)
- MacOS:  [QuickTime](https://support.apple.com/en-us/HT201290)

In short depends on your system, but formats that should be supported by all 3 are wav and mp3

Best way to see if some format is supported is to try to add it and play it, if it doesn't play it isn't supported on your system.

## Performance

The program is designed to run in the background without taking much CPU/RAM.

On my system it takes around 17MB, 25MB at most and around 0.3% of CPU - this is with playing maximum (10) of
sounds at the same time.

It can go much higher than 10, it's just an arbitrary number as I don't see why would you torture yourself with more
than 10 sounds playing at the same time.

## Example usage

TODO

## Contributing

Any sort of contribution/discussion is welcome - see the [CONTRIBUTING.md](CONTRIBUTING.md) file for details.

## License

This project is licensed under the GPLv3 License - see the [LICENSE.md](LICENSE.md) file for details.

