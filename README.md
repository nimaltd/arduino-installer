# arduino-installer

Installs embedded C and C++ libraries for Arduino, from GitHub, from a zip, or from a folder.

It puts a library where Arduino finds it, the way you choose: in the libraries folder of your sketchbook, where Library Manager installs to, for every sketch, or in the `src` folder of one sketch, for that sketch alone. A library written for any project gets the `library.properties` Arduino knows it by, the libraries it needs go in first, and its settings are kept through every update.

It works with any library that has an `installer.yml` at the root of its repository. I wrote it for my own [NimaLTD](https://github.com/nimaltd) libraries, and they all have one, but nothing in it is tied to them: add an `installer.yml` to yours, as shown [below](#for-someone-writing-a-library), and it installs the same way. The same file serves [stm32-installer](https://github.com/nimaltd/stm32-installer), [zephyr-installer](https://github.com/nimaltd/zephyr-installer) and [esp32-installer](https://github.com/nimaltd/esp32-installer).

The Arduino IDE, version 1 or 2, and arduino-cli all find what it installs, since both places are ones Arduino itself looks in.

Every command below uses `owner/example`, the library's GitHub owner and name, such as `nimaltd/ee24`. Put the real ones in its place.

---

## Installing a library

Install the installer once. This needs internet:

```bash
pip install arduino-installer
```

Then install a library by its GitHub owner and name. To see it work first, take [arduino-installer-example](https://github.com/nimaltd/arduino-installer-example), a library made for trying the installer on:

```bash
arduino-installer nimaltd/arduino-installer-example
```

It builds for any board, and prints on Serial. Its README walks through both places a library can go, a setting kept through an update, an option, and an uninstall. Any other library goes in the same way, as `arduino-installer owner/example`.

To update it later, `pip install --upgrade arduino-installer`. To remove it, `pip uninstall arduino-installer`.

On Windows, if `arduino-installer` is not found after installing, pip put it in a folder that is not on your PATH. `python -m arduino_installer owner/example` runs the same thing.

### Where a library goes

Run from a sketch's folder, the one holding `blink.ino` for a sketch called `blink`, the installer asks:

```
This is the sketch blink. Where do the libraries go?
  1  the libraries folder, for every sketch: C:/Users/you/Documents/Arduino/libraries
  2  this sketch's src folder, for this sketch only
Install into [1]:
```

Press Enter for the libraries folder. Run from anywhere else, that is where it goes without a question. `--into libraries` or `--into sketch` answers it on the command line, and in a script, where nobody can answer, the libraries folder is taken.

| | The libraries folder | A sketch's src folder |
|---|---|---|
| Which sketches see it | every sketch | that sketch alone |
| You include it as | `#include "example.h"` | `#include "src/example/src/example.h"` |
| Its settings | one set, for every sketch | that sketch's own |
| It goes into | `Arduino/libraries/example/` | `blink/src/example/` |
| Library Manager lists it | yes | no |

In a sketch where the installer has put a library into `src` before, `2` is the answer offered instead, so an update goes where the library already is.

### The libraries folder

It is the `libraries` folder of your sketchbook, the folder the IDE keeps sketches in, and the installer finds it the way Arduino does. The first of these that is set wins:

1. `--sketchbook D:/Arduino`, on the command line.
2. `ARDUINO_DIRECTORIES_USER`, the variable arduino-cli reads.
3. Arduino IDE 2's settings, the sketchbook location in its Preferences.
4. arduino-cli's settings, `directories.user` in `arduino-cli.yaml`.
5. Arduino IDE 1's preferences, the sketchbook location in its Preferences.
6. Where Arduino puts it on a new machine: `Documents/Arduino` on Windows and macOS, `~/Arduino` on Linux.

Every install says which folder it used, and why:

```
Libraries folder: C:/Users/you/Documents/Arduino/libraries  (from Arduino IDE's settings)
```

### What happens

Take `example`, installed into the libraries folder:

```
Arduino/libraries/
  .arduino-installer.json    what is installed here, and where
  example/
    library.properties       written by the installer: how Arduino knows the library
    src/
      example.h              the library's files, as its installer.yml lists them
      example_config.h       its settings, between USER CODE lines
      example.cpp
```

The same library installed into a sketch called `blink`:

```
blink/
  blink.ino
  .arduino-installer.json    what is installed in this sketch
  src/
    example/
      src/
        example.h
        example_config.h
        example.cpp
```

Arduino builds every file of a sketch's `src` folder with the sketch, so nothing else is needed there. It puts none of them on the include path, though, which is why the sketch includes the library by its path, and the last line of the install says exactly which:

```
Done. #include "src/example/src/example.h" and you are away.
```

### A library that needs another

What a library needs always goes into the libraries folder, also when the library itself goes into a sketch. In a sketch's `src` folder one library cannot find another: Arduino looks for `#include "osal.h"` in the libraries folder and nowhere else in the sketch. So the installer says so before it goes in:

```
Requirements
  note    osal, which it needs, goes into the libraries folder
          In a sketch's src folder one library cannot find another. In the libraries folder every library and sketch can.
```

One already in the libraries folder at a version that will do is left alone. Everything is fetched before anything is installed, so when a library cannot be had, nothing is changed.

### Settings

Arduino has no settings menu of its own for a library, so a library's settings are in its configuration header, between `USER CODE BEGIN` and `USER CODE END`:

```c
/* USER CODE BEGIN EXAMPLE_CONFIGURATION */
#define EXAMPLE_PERIOD_MS           250U
/* USER CODE END EXAMPLE_CONFIGURATION */
```

Change them there. Every install and update keeps what is between those lines. In the libraries folder there is one set, for every sketch; installed into a sketch, the sketch has its own.

### What you see

A first install from GitHub, run from a sketch, into the libraries folder:

```
This is the sketch blink. Where do the libraries go?
  1  the libraries folder, for every sketch: C:/Users/you/Documents/Arduino/libraries
  2  this sketch's src folder, for this sketch only
Install into [1]:
Libraries folder: C:/Users/you/Documents/Arduino/libraries  (from the default)
Fetching owner/example ...

example 1.2.0
Driver for the X chip
driver / storage

Requirements
  note    Needs I2C, 400 kHz
          Wire it up and set it up in your sketch.

Folder to install example into [example]:

Files
  written example/src/example.h
  written example/src/example_config.h
  written example/src/example.cpp

Project
  updated library.properties  Wrote example's library.properties, which Arduino knows it by.

Done. #include "example.h" and you are away.
```

### What to install

The argument can be any of these, and you can give several at once:

| You have | You type |
|---|---|
| Nothing yet, and internet | `arduino-installer owner/example` |
| The library's GitHub address | `arduino-installer https://github.com/owner/example` |
| The zip from GitHub's **Download ZIP** | `arduino-installer D:/Downloads/example-main.zip` |
| That zip unpacked, anywhere on disk | `arduino-installer D:/Downloads/example-main` |

A bare name with no owner, like `example`, is a NimaLTD library, `nimaltd/example` on GitHub, unless a folder of that name exists where you run it, in which case the folder is used. A path that does not exist is reported as missing rather than looked up on GitHub.

### Options

| Option | What it does |
|---|---|
| `--into libraries` | Into the libraries folder, for every sketch, without the question |
| `--into sketch` | Into the `src` folder of the sketch this is run from, for it only |
| `--sketchbook D:/Arduino` | The sketchbook folder, the one holding `libraries`, when the installer should not look for it |
| `--project D:/Arduino/blink` | The sketch's folder, when you are not running from it |
| `--dir example2` | The folder to install into, for one library. Asked for when not given, with the library's name as the answer if you just press Enter, or the folder it is already in |
| `--ref v2.0.0` | A tag, a branch or a commit to take from GitHub. When not given, `main`, or `master` for a repository that has no `main` |
| `--key github_pat_...` | A GitHub token, for a library in a private repository. See [A private repository](#a-private-repository) |
| `--uninstall example` | Take the library out. See [Uninstalling a library](#uninstalling-a-library) |
| `--with uptime` | Take this part of the library without being asked. Give it once for each part |
| `--without uptime` | Leave this part out, or take it out of a library already installed |
| `--version` | Show which version of the installer you have, and do nothing else |

### Updating a library

Run the same command again. Every file of the library is replaced, so an update updates, and `library.properties` is written again from the new `installer.yml`. What you wrote between `USER CODE BEGIN` and `USER CODE END` is kept. Outside those lines, the next install replaces it, and when that would lose something of yours the file is saved beside it first, as a `.bak`.

The record of what is installed, and where, is `.arduino-installer.json`: in the libraries folder for what is there, and in a sketch for what is in it.

### Uninstalling a library

```bash
arduino-installer --uninstall example
```

Run from a sketch, it is taken out of the sketch when the sketch has it, and out of the libraries folder otherwise. `--into` says which, when it is in both. Its files go, and its `library.properties`. What was yours is saved before it goes, as a `.bak` beside it: a configuration header with your settings in it, or any file of the library you changed by hand. A file you put in the library's folder yourself is left where it is, and the folder with it.

A library another one needs stays, and the installer says which needs it. One that came into the libraries folder because a library in a sketch needed it stays there too, since other sketches may use it.

### Without internet

On a machine that has internet, `pip download arduino-installer` saves one file, the installer, which needs nothing else. Download the library too, from the green **Code** button, **Download ZIP**. Then, on the machine with no internet:

```bash
pip install arduino_installer-1.0.0-py3-none-any.whl
arduino-installer D:/Downloads/example-main.zip
```

If the library needs another, give that zip on the same line. Behind a proxy, set `HTTPS_PROXY` to its address.

### A private repository

A library in a private repository installs the same way, given a GitHub token that can read it. Make one once:

1. Open [github.com/settings/personal-access-tokens](https://github.com/settings/personal-access-tokens) and click **Generate new token**.
2. Give it a name and an expiry. Under **Resource owner**, pick the account or the organisation that owns the repository.
3. Under **Repository access**, choose **Only select repositories** and pick the library's repository.
4. Under **Permissions**, set **Contents** to **Read-only**:
   - Older layout: open **Repository permissions** and change **Contents** from **No access** to **Read-only**.
   - Newer layout: click **+ Add permissions**, tick **Contents**, then set its access to **Read-only**.

   **Metadata** comes with it by itself. Contents is the one that matters: without it the token can see the repository but not read a file of it.
5. Click **Generate token**, and copy it. GitHub shows it only once.

Then give it with `--key`:

```bash
arduino-installer owner/example --key github_pat_...
```

Or put it in `GITHUB_TOKEN` once, and install by name as usual. That keeps it out of your shell's history, where `--key` leaves it:

**Windows, PowerShell:**

```powershell
$env:GITHUB_TOKEN = "github_pat_..."
arduino-installer owner/example
```

**Windows, Command Prompt:**

```bat
set GITHUB_TOKEN=github_pat_...
arduino-installer owner/example
```

**Linux and macOS:**

```bash
export GITHUB_TOKEN=github_pat_...
arduino-installer owner/example
```

`--key` comes first when both are there. `GH_TOKEN` works as well, and if you use the `gh` command, `gh auth token` prints the token you are signed in with. Whichever way it comes, the token is sent to GitHub and nowhere else.

When the token cannot read the library, the installer says which of these it is:

- **It can see the repository, but cannot read its files.** The token has no Contents permission, only Metadata. Edit the token, and its value stays the same, so the command you ran keeps working: open the tokens page, click the token's name, click **Edit**, set Contents to **Read-only** as in step 4, and click **Update** at the bottom of the page. Then run the same command again.
- **It cannot see the repository.** The repository is not in the token's Repository access. Edit the token as above and add it.
- **GitHub did not accept the token.** It has expired, been revoked, or was copied with a character missing. Make a new one.

A repository of an organisation can need one more step: an organisation that asks for fine-grained tokens to be approved shows the token nothing of its repositories until an owner of the organisation approves it, under its settings, **Personal access tokens**, **Pending requests**.

---

---

## For someone writing a library

Put an `installer.yml` at the root of the repository. Any library can have one, whoever wrote it, and the one file serves arduino-installer and the other installers alike: each reads its own keys and leaves the others' alone.

Every key arduino-installer reads is below, each with what it does. Only `name` and `files` are required; leave out what your library does not need. For a working one to copy, see [arduino-installer-example](https://github.com/nimaltd/arduino-installer-example).

```yaml
name: example                      # the library's name, and its folder
description: Driver for the X chip # one line: shown while installing, and library.properties' sentence
repository: https://github.com/owner/example  # where it comes from: library.properties' url
license: Apache-2.0                # the licence's SPDX name
version: 1.0.0                     # only when the first header has no @version tag

kind: driver                       # driver, middleware, rtos, protocol, filesystem,
                                   # utility or bsp
category: storage                  # sensor, storage, display, communication, wireless,
                                   # rtos, timing, power, input, math or system
provides: []                       # what it gives other libraries: [rtos] for an RTOS

requires:
  arduino_installer: 1.0.0         # the oldest arduino-installer that reads this file
  libraries:                       # other libraries, installed first into the libraries
    - osal >= 1.0.0                # folder; no owner means nimaltd
    - owner/lib                    # anyone else's, as owner/name
  peripherals:                     # hardware it uses, named to the user
    - type: i2c                    # what it is
      note: 400 kHz                # how to set it up

install:
  layout: mirror                   # mirror keeps the repository's folders,
                                   # flat (the default) puts every file at the top

files:
  headers:                         # .h files; the first is the one to #include
    - src/example.h
    - src/example_config.h         # its settings, in USER CODE lines kept on update
  sources:                         # .c and .cpp files, which Arduino builds
    - src/example.cpp
    - from: src/port/spi.c         # a file that goes somewhere of its own,
      to: src/port/spi.c           # whatever the layout says

options:                           # parts the user chooses at install
  uptime:                          # the name typed after --with
    description: Uptime in hours, minutes and seconds  # the question asked
    libraries: []                  # libraries this part needs, installed first
    files:                         # its files, written like files above
      sources:
        - src/example_uptime.cpp

extras:                            # copied as they are, never compiled
  - LICENSE.md                     # LICENSE.md and NOTICE are the default,
  - NOTICE                         # so leave this out if that is all
  - README.md

arduino:                           # read by arduino-installer only, for library.properties
  architectures: [avr, esp32]      # the boards it runs on; ["*"], any, when left out
  category: Data Storage           # Arduino's own category; when left out, the nearest
                                   # to category above
  author: Your Name                # who wrote it; the repository's owner when left out
  maintainer: you@example.com      # who looks after it; the author when left out
  depends:                         # libraries from Library Manager it needs, by name,
    - Adafruit BusIO               # checked at install, and listed for the IDE
    - ArduinoJson (>=6.0.0)        # with a version when one is needed
```

Arduino's categories are Display, Communication, Signal Input/Output, Sensors, Device Control, Timing, Data Storage, Data Processing and Other.

Keys only the other installers read, such as `requires.installer`, `zephyr` and `esp32`, can stay in the same file. This installer skips them.

Leave `version` out. The installer reads the version from the `@version` tag in the file comment of the first header listed, so it is written in the code and nowhere else.

`requires.arduino_installer` is the oldest arduino-installer that reads the file correctly. It is checked before anything else in the file is read, so an older installer stops with a message saying to update, rather than read the file wrongly. Write it as three numbers, `1.0.0`: unquoted, YAML reads `1.10` as the decimal number `1.1`, and that is refused.

### What Arduino needs of a library

- **Keep the code in `src/`, with `layout: mirror`.** Arduino builds `src/` and every folder in it, and puts `src/` on the include path. A library with no `src/` folder is built from the files at its top instead.
- **Headers beside the code that includes them.** In a sketch's `src` folder nothing is on the include path, so `#include "example.h"` in `example.cpp` works only when the two are in the same folder. A header in another folder of the library is included by its path from there.
- **`extern "C"` in every header of C code.** A sketch is C++, and without it the linker cannot find a function of a `.c` file.
- **Settings in a configuration header**, between `USER CODE` lines the installer keeps, since Arduino has no other place for them.
- **No `install.defines`.** Arduino has no defines for a whole build, so the installer warns about them and sets nothing. Put them in the configuration header instead.

A library made for Arduino that ships its own `library.properties`, listed under `extras` or `files` so it is installed, keeps it: the installer writes one only for a library that has none.

---

## Running the tests

The shared core, [core-installer](https://github.com/nimaltd/core-installer), is a git submodule in `src/core`, so clone with it:

```bash
git clone --recursive https://github.com/nimaltd/arduino-installer.git
```

In a clone made without `--recursive`, `git submodule update --init` fetches it. Then:

```bash
python test/run_tests.py
```

CI also installs a small library from `test/e2e/`, and the one it needs, with the installer it just built: into the libraries folder for one sketch, and into the `src` folder of another, whose setting it then changes and installs again. It builds both for an Uno with arduino-cli, each sketch checking its own setting, then takes the library out of the sketch again. So every release is known to work with real Arduino.

---

## Support

I write these tools and libraries in my own time and give them away, because good tools should be easy to get. If this one saved you an afternoon, there are two things that genuinely help:

**Star the repo.** It costs you one click, it helps other engineers find the tool, and it is the main reason I keep going.

**[Buy me a coffee on Ko-fi](https://ko-fi.com/nimaltd).** Any amount is a real motivation to keep writing, documenting and maintaining this work.

[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=for-the-badge&logo=github)](https://github.com/NimaLTD)
[![YouTube](https://img.shields.io/badge/YouTube-Subscribe-red?style=for-the-badge&logo=youtube)](https://youtube.com/@nimaltd)
[![Instagram](https://img.shields.io/badge/Instagram-Follow-purple?style=for-the-badge&logo=instagram)](https://instagram.com/github.nimaltd)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/nimaltd)
[![Email](https://img.shields.io/badge/Email-Contact-red?style=for-the-badge&logo=gmail)](mailto:nima.askari@gmail.com)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support-orange?style=for-the-badge&logo=ko-fi)](https://ko-fi.com/nimaltd)

---

## License

Apache License 2.0. See [LICENSE](https://github.com/nimaltd/arduino-installer/blob/main/LICENSE).
