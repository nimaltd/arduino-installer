# arduino-installer

Installs embedded C and C++ libraries for Arduino, from GitHub, from a zip, or from a folder.

It puts a library where Arduino finds it, the way you choose: in the libraries folder of your sketchbook, where Library Manager installs to, for every sketch, or in the `src` folder of one sketch, for that sketch alone. A library written for any project gets the `library.properties` Arduino knows it by, the libraries it needs go in first, and its settings are kept through every update.

It works with any library that has an `installer.yml` at the root of its repository. I wrote it for my own [NimaLTD](https://github.com/nimaltd) libraries, and they all have one, but nothing in it is tied to them: add an `installer.yml` to yours, as shown [below](#for-someone-writing-a-library), and it installs the same way. The same file serves [stm32-installer](https://github.com/nimaltd/stm32-installer), [zephyr-installer](https://github.com/nimaltd/zephyr-installer), [esp32-installer](https://github.com/nimaltd/esp32-installer) and [pio-installer](https://github.com/nimaltd/pio-installer).

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

When a newer arduino-installer is out, the last line of a run says so, with that command. It asks PyPI at most once a day, waits no more than two seconds for an answer, and says nothing when there is none. `--no-update-check` turns it off, and so does `INSTALLER_NO_UPDATE_CHECK` set to anything. On a build server, where `CI` is set, it is off already.

On Windows, if `arduino-installer` is not found after installing, pip put it in a folder that is not on your PATH. `python -m arduino_installer owner/example` runs the same thing.

### Every command

Each command with `owner/example` standing for the library. An update is the install again. Every option is explained under [Options](#options).

| To | Run |
|---|---|
| Install the installer | `pip install arduino-installer` |
| Update the installer | `pip install --upgrade arduino-installer` |
| Remove the installer | `pip uninstall arduino-installer` |
| See which version you have | `arduino-installer --version` |
| See every option | `arduino-installer --help` |
| Install a library from GitHub | `arduino-installer owner/example` |
| Install one release of it, a branch or a commit | `arduino-installer owner/example@v2.0.0` |
| Install it by its GitHub address | `arduino-installer https://github.com/owner/example` |
| Install it from a downloaded zip | `arduino-installer D:/Downloads/example-main.zip` |
| Install it from a folder on disk | `arduino-installer D:/Downloads/example-main` |
| Install several at once, such as a library and the zip of one it needs | `arduino-installer D:/Downloads/example-main.zip D:/Downloads/osal-main.zip` |
| Install into a folder you choose, without the question | `arduino-installer owner/example --dir example2` |
| Install into a sketch you are not running from | `arduino-installer owner/example --project D:/Arduino/blink` |
| Install into the libraries folder, for every sketch | `arduino-installer owner/example --into libraries` |
| Install into this sketch's src folder, for it only | `arduino-installer owner/example --into sketch` |
| Use a sketchbook the installer does not find by itself | `arduino-installer owner/example --sketchbook D:/Arduino` |
| Take an option of the library without the question | `arduino-installer owner/example --with uptime` |
| Leave an option out, or take it out of a library already installed | `arduino-installer owner/example --without uptime` |
| Run a step of the library without the question | `arduino-installer owner/example --run make-key` |
| Leave a step unrun, without the question | `arduino-installer owner/example --no-run make-key` |
| Answer every question with the answer offered, and run every step, for a script | `arduino-installer owner/example --yes` |
| Install from a private repository | `arduino-installer owner/example --key github_pat_...` |
| Leave out the check for a newer installer | `arduino-installer owner/example --no-update-check` |
| Update a library | `arduino-installer owner/example` |
| Uninstall a library | `arduino-installer --uninstall example` |
| Uninstall several, in any order | `arduino-installer --uninstall osal example` |
| Uninstall from this sketch, when the libraries folder has it too | `arduino-installer --uninstall example --into sketch` |
| Run it when `arduino-installer` is not found | `python -m arduino_installer owner/example` |

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

It comes from the release the library names for it, or else from its default branch. One already in the libraries folder at a version that will do is left alone. Everything is fetched before anything is installed, so when a library cannot be had, nothing is changed.

### Settings

Arduino has no settings menu of its own for a library, so a library's settings are in its configuration header, between `USER CODE BEGIN` and `USER CODE END`:

```c
/* USER CODE BEGIN EXAMPLE_CONFIGURATION */
#define EXAMPLE_PERIOD_MS           250U
/* USER CODE END EXAMPLE_CONFIGURATION */
```

Change them there. Every install and update keeps what is between those lines. In the libraries folder there is one set, for every sketch; installed into a sketch, the sketch has its own.

### Files that become yours

A library installed into a sketch can bring files that belong to the sketch rather than to the library, such as an `arduino_secrets.h` for your network's name and password: a start, made for you to fill in. Each is created in the sketch's folder only when it is not there:

```
Files
  written src/example/src/example.h
  created arduino_secrets.h  yours from now on
```

From then on it is yours. An update never writes over it, and says so with `kept arduino_secrets.h  yours`. An uninstall leaves it where it is, with `kept arduino_secrets.h  yours, not removed`. A library can never put such a file over the sketch's `.ino` files, nor outside the sketch's folder.

The libraries folder is shared by every sketch, so it has no place for such files. A library that brings them, installed there, stops before anything is written and says to install it into a sketch, with `--into sketch`.

### Steps a library runs

A library installed into a sketch can need something made that no file can carry, such as a key made fresh for each device. It names a step for that, and once its files are in, the installer shows you exactly what will run, and asks:

```
Run
  make-key     Make the device's key, device_key.h
               python tools/make_key.py device_key.h
               Run it? [Y/n]:
```

Enter runs it, in the sketch's folder. A Python script runs with the same Python as the installer, so it works the same on every computer. `n` leaves it, and the output says how to run it later. In a script, where nobody can answer, it is not run.

Nothing in a library's `installer.yml` can skip the question. Only you can: `--run make-key` runs that step without asking, `--no-run make-key` leaves it, and `--yes` runs every step and takes the offered answer to every other question, for a script or a build server.

A step that makes a file can name it, and when that file is already in the sketch the step is skipped without a question, so a second install never makes a second key. A step that names no file and ran before is not asked about again either, until the library changes what it runs. When a step fails, what was installed stays installed, and the installer ends with exit code 1, so a script notices. Steps need a sketch to run in. In the libraries folder they are not run, the install goes ahead, and the output says to install into a sketch to have them run.

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
| One release of it, a branch, or a commit | `arduino-installer owner/example@v2.0.0` |
| The library's GitHub address | `arduino-installer https://github.com/owner/example` |
| The zip from GitHub's **Download ZIP** | `arduino-installer D:/Downloads/example-main.zip` |
| That zip unpacked, anywhere on disk | `arduino-installer D:/Downloads/example-main` |

A bare name with no owner, like `example`, is a NimaLTD library, `nimaltd/example` on GitHub, unless a folder of that name exists where you run it, in which case the folder is used. A path that does not exist is reported as missing rather than looked up on GitHub.

From GitHub, a library comes from its repository's default branch, the one GitHub shows first, whatever the repository calls it. After an `@`, a tag, a branch or a commit takes exactly that instead, and so does a GitHub address ending in `/tree/v2.0.0`. Every file comes from one commit, even when the branch moves on while they download, and the record keeps that commit, so you can always tell what you built with.

### Options

| Option | What it does |
|---|---|
| `--into libraries` | Into the libraries folder, for every sketch, without the question |
| `--into sketch` | Into the `src` folder of the sketch this is run from, for it only |
| `--sketchbook D:/Arduino` | The sketchbook folder, the one holding `libraries`, when the installer should not look for it |
| `--project D:/Arduino/blink` | The sketch's folder, when you are not running from it |
| `--dir example2` | The folder to install into, for one library. Asked for when not given, with the library's name as the answer if you just press Enter, or the folder it is already in |
| `--ref v2.0.0` | A tag, a branch or a commit to take from GitHub, the same as `owner/example@v2.0.0`. When not given, the repository's default branch |
| `--key github_pat_...` | A GitHub token, for a library in a private repository. See [A private repository](#a-private-repository) |
| `--uninstall example` | Take the library out. See [Uninstalling a library](#uninstalling-a-library) |
| `--with uptime` | Take this part of the library without being asked. Give it once for each part |
| `--without uptime` | Leave this part out, or take it out of a library already installed |
| `--run make-key` | Run this step of the library without being asked. Give it once for each step. See [Steps a library runs](#steps-a-library-runs) |
| `--no-run make-key` | Leave this step unrun, without being asked |
| `--yes` | Take the answer each question offers, without asking, and run every step. For a script or a build server |
| `--no-update-check` | Do not ask PyPI whether a newer arduino-installer is out |
| `--version` | Show which version of the installer you have, and do nothing else |

### Updating a library

Run the same command again. Every file of the library is replaced, so an update updates, and `library.properties` is written again from the new `installer.yml`. What you wrote between `USER CODE BEGIN` and `USER CODE END` is kept. Outside those lines, the next install replaces it, and when that would lose something of yours the file is saved beside it first, as a `.bak`.

The record of what is installed, and where, is `.arduino-installer.json`: in the libraries folder for what is there, and in a sketch for what is in it. For each library it also keeps where it came from, down to the commit, and the steps that ran.

### Uninstalling a library

```bash
arduino-installer --uninstall example
```

Run from a sketch, it is taken out of the sketch when the sketch has it, and out of the libraries folder otherwise. `--into` says which, when it is in both. Its files go, and its `library.properties`. What was yours is saved before it goes, as a `.bak` beside it: a configuration header with your settings in it, or any file of the library you changed by hand. A file you put in the library's folder yourself is left where it is, and the folder with it, and so are the [files that became yours](#files-that-become-yours).

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

## For someone writing a library

Put an `installer.yml` at the root of the repository. Any library can have one, whoever wrote it, and the one file serves arduino-installer and the other installers alike: each reads its own keys and leaves the others' alone.

Every key arduino-installer reads is below, each with what it does, as a manifest asking for 2.1.0 writes it. Only `name` and its `headers` or `sources` are required; leave out what your library does not need. What changed in 2.1.0, and how a manifest from before reads, is under [Paths, from 2.1.0](#paths-from-210). For a working one to copy, see [arduino-installer-example](https://github.com/nimaltd/arduino-installer-example).

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
  arduino_installer: 2.1.0         # the oldest arduino-installer that reads this file
  libraries:                       # other libraries, installed first into the libraries
    - osal >= 1.0.0                # folder; no owner means nimaltd
    - owner/lib                    # anyone else's, as owner/name
    - owner/lib@v1.2.0             # a tag, branch or commit, not its default branch
    - source: owner/other@v2.9.3   # a repository with no installer.yml of its own,
      manifest: manifests/other.yml  # with one this library carries for it
      minimum: 2.9.0               # the oldest version that will do
  peripherals:                     # hardware it uses, named to the user
    - type: i2c                    # what it is
      note: 400 kHz                # how to set it up

headers:                           # .h files; the first is the one to #include
  - src/example.h                  # every file keeps its path: the library's src/example.h
  - src/example_config.h           # its settings, in USER CODE lines kept on update
sources:                           # .c and .cpp files, which Arduino builds
  - src/example.cpp
  - src/port/*.c                   # a wildcard, matched the way a shell would:
                                   # * inside one folder, ** across any number of them
  - from: extra/spi.c              # a file that goes somewhere of its own,
    to: src/port/spi.c             # in the library's folder

options:                           # parts the user chooses at install
  uptime:                          # the name typed after --with
    description: Uptime in hours, minutes and seconds  # the question asked
    libraries: []                  # libraries this part needs, installed first
    sources:                       # its files, written like headers and sources above
      - src/example_uptime.cpp

extras:                            # copied as they are, never compiled
  - LICENSE.md                     # LICENSE.md and NOTICE are the default,
  - NOTICE                         # so leave this out if that is all
  - README.md                      # in the library's folder
  - root: tools                    # 2.1.0: tools/ into the sketch's folder instead, as the
                                   # library's own, written again on every install, into a
                                   # sketch only

once:                              # the sketch's own files, installed into a sketch only:
                                   # made when missing, then the user's
  - data/example.json              # 2.1.0: a path alone lands at that path in the sketch
  - from: templates/arduino_secrets.h  # the file in the repository, to the sketch's folder
    to: arduino_secrets.h          # to: another place in the sketch

run:                               # steps run once the files are in, each asked about
                                   # first, installed into a sketch only
  - label: make-key                # the name typed after --run
    description: Make the device's key, device_key.h  # shown with the question
    script: tools/make_key.py      # Python, run with the installer's own Python, from the
                                   # sketch's folder, or {library}/... in the library's
    args: [device_key.h]           # or command: [program, arguments], with no shell
    unless: device_key.h           # skipped when this file is in the sketch already

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

Keys only the other installers read, such as `requires.stm32_installer`, `zephyr` and `esp32`, can stay in the same file. This installer skips them.

Leave `version` out. The installer reads the version from the `@version` tag in the file comment of the first header listed, so it is written in the code and nowhere else.

`requires.arduino_installer` is the oldest arduino-installer that reads the file correctly. It is checked before anything else in the file is read, so an older installer stops with a message saying to update, rather than read the file wrongly. Write it as three numbers, `1.0.0`: unquoted, YAML reads `1.10` as the decimal number `1.1`, and that is refused.

A library that uses anything 2.0.0 brings says `requires.arduino_installer: 2.0.0`: `once` files in the sketch's folder, `run`, or a library it needs given with an `@` or a `manifest`. The version also decides where `once` files go. A manifest asking for 2.0.0 or newer puts them in the sketch's folder, and one asking for less keeps the meaning it was written for, the library's own folder, so a release tagged before 2.0.0 still installs as it did.

### Paths, from 2.1.0

A manifest asking for `requires.arduino_installer: 2.1.0` has one rule for every path that names a place in the sketch's folder: it starts at the sketch's folder. `{library}` at its start names the library's own folder instead, wherever `--dir` put it. A path that names a file of the library, under `headers`, `sources`, `extras` or `once`, or as a `from`, is a path in the repository, as always.

And every file is copied to the path it has, unchanged, unless a `to` says otherwise, so a path alone is all an entry needs: `src/example.c` lands at `src/example.c` in the library's folder, so `install.layout` is gone, `flat` is refused and `mirror` says nothing new. A `once` file lands at its own path in the sketch's folder: `- data/example.json` at `data/example.json`, where before 2.1.0 it was written `- from: data/example.json` and took only its name. And `headers` and `sources` need no `files` around them; `files` still reads, but not both at once.

A `to` gives a file another place, where its list puts files. Under `headers`, `sources` and `extras` that is the library's folder, so `- from: src/example.h, to: example.h` lands at the top of it, and the include path follows. Under `once` it is the sketch's folder, where every `once` file lands. A `root` puts an extra in the sketch's folder instead of the library's: `- root: tools` takes the library's `tools/` to the sketch's `tools/`. Code has no `root`, since it is built in the library's folder, and a `once` file needs none. Wherever a `from` would be the same path as its `to` or `root`, leave it out: `- root: tools` is `- from: tools, root: tools`.

| Key | Starts at |
|---|---|
| `headers`, `sources`, `extras`, `once`, `from` | the library's repository |
| `to` under `headers`, `sources` and `extras` | the library's folder |
| `once.to`, `extras.root` | the sketch's folder |
| `run.script`, `run.unless` | the sketch's folder, or the library's with `{library}/` |
| `{library}` in `run.args` and `run.command` | the library's folder, as the step names it from the sketch's folder |

An extra with a `root` lands in the sketch's folder, as the library's own: a file at `root` itself, the files of a folder under it with their path below it, those a wildcard matches under it with their names; an extra's `to` places them the same way in the library's folder. It is written again on every install, a file of it the new version no longer ships is removed, and an uninstall takes it out. A file already there that the installer did not put there is the user's, and is never written over: the install stops and says so.

In every manifest, a wildcard matches the whole path, the way a shell does, and the same whether the library comes from GitHub or a folder: `*` and `?` stay inside one folder, `**` crosses any number of them, none included, and `[ab]` is one of a set. So `*.c` is the `.c` files at the top, `src/*.c` those in `src`, and `src/**/*.c` every one below `src`, however deep. And two files of the code that would land in one place, such as two `util.c` that `flat` put side by side, are refused when the manifest is read, where the second used to replace the first without a word.

```yaml
extras:
  - root: tools                    # tools/keygen.py and tools/keygen.md, into the sketch's folder
run:
  - label: signing-key
    script: tools/keygen.py        # from the sketch's folder
    unless: sign_key.pem
```

A step's script has to be one the install puts in place, an extra with a `root` or a `once` file, or with `{library}`, a file of the library's folder; anything else is refused when the manifest is read. A manifest asking for less than 2.1.0 keeps the meaning it was written for: its script is found in the library as it was fetched, and `{library}` is left as it is written.

### Files of the sketch's own

A file that belongs to the sketch rather than to the library goes under `once`, such as an `arduino_secrets.h` for the user to fill in. It is created in the sketch's folder when it is missing, and is the user's from then on: never replaced by an update, never removed by an uninstall.

```yaml
once:
  - from: templates/arduino_secrets.h
    to: arduino_secrets.h              # a place of its own, in the sketch's folder
```

`from` is a file of the library's repository, and `to` its place from the sketch's folder. From 2.1.0 a path alone will do, `- arduino_secrets.h`, landing at that same path, and a `to` is only needed for another place; before, each entry is a mapping with a `from`, and a `to` left out meant its own name, at the top. A `once` file has no `root`: it always lands in the sketch's folder. Each is checked before anything is written: `to` stays inside the sketch, is none of its `.ino` files, and does not point into the library's own folder, which every install replaces. Two entries with one `to` are refused. And `from`, like every file a manifest names, stays inside the library: no `..`, no absolute path, no link leading out of it.

The libraries folder belongs to no sketch, so there a library with `once` files stops before anything is written, saying to install it into a sketch. Settings belong in the configuration header's USER CODE lines, which work in both places.

### Steps run after the install

Something no file can carry, such as a key made fresh for each device, is made by a step under `run`. It runs once the library's files are in, in the sketch's folder:

```yaml
extras:
  - root: tools                        # tools/make_key.py, into the sketch's folder
run:
  - label: make-key
    description: Make the device's key, device_key.h
    script: tools/make_key.py          # the sketch's tools/make_key.py
    args: [device_key.h]
    unless: device_key.h
```

- `label` names the step, typed after `--run`, in lower case letters, digits, `_` and `-`.
- `description` is shown with the question.
- `script` is a Python file, run with the installer's own Python, so it works on every computer the installer does. From 2.1.0 it is a path from the sketch's folder, where an extra with a `root` or a `once` file put it, or `{library}/...` in the library's folder, see [Paths, from 2.1.0](#paths-from-210); before, it is a file of the library's repository. Or `command`, a program and its arguments as a list, `[openssl, rand, -out, device.key, "32"]`, run as it is, with no shell. One of the two, never both.
- `args` are added after either.
- `unless` names a file the step makes, from the sketch's folder. When it is there, the step is skipped without a question.

The step sees where things are in its environment: `INSTALLER_PROJECT`, the sketch's folder, `INSTALLER_LIBRARY`, the library's folder in it, `INSTALLER_NAME` and `INSTALLER_VERSION`, the library's, and `INSTALLER`, `arduino-installer`.

The user is always asked, and is shown exactly what will run. Nothing in the manifest can turn that off, only the user, with `--run` or `--yes`. A step with no `unless` that ran before is not asked about again until what it runs changes, so make it safe to run twice anyway. A step that fails leaves the install as it is and ends the run with exit code 1. Steps need a sketch to run in: in the libraries folder they are left unrun, as a no would leave them, and the install goes ahead.

### A library it needs

`requires.libraries` lists the libraries yours needs, each installed first into the libraries folder when it is missing or older than the version given:

```yaml
requires:
  libraries:
    - osal >= 1.0.0                    # no owner means nimaltd: github.com/nimaltd/osal
    - someone/lib                      # anyone else's, by owner and name
    - someone/lib@v1.2.0               # exactly this tag, branch or commit
    - source: someone/plain@v2.0.0
      manifest: manifests/plain.yml    # an installer.yml for a repository without one
      minimum: 2.0.0
```

Without an `@`, a library comes from its repository's default branch. The last form installs a library whose repository has no `installer.yml` of its own: yours carries one for it, at the path given, written as if it sat at the root of that repository. A library from Library Manager is not one of these: name it under `arduino.depends`.

### What Arduino needs of a library

- **Keep the code in `src/`, with `layout: mirror`, or from 2.1.0 with no layout at all, since every file keeps its path.** Arduino builds `src/` and every folder in it, and puts `src/` on the include path. A library with no `src/` folder is built from the files at its top instead.
- **Headers beside the code that includes them.** In a sketch's `src` folder nothing is on the include path, so `#include "example.h"` in `example.cpp` works only when the two are in the same folder. A header in another folder of the library is included by its path from there.
- **`extern "C"` in every header of C code.** A sketch is C++, and without it the linker cannot find a function of a `.c` file.
- **Settings in a configuration header**, between `USER CODE` lines the installer keeps, since Arduino has no other place for them.
- **No `install.defines`.** Arduino has no defines for a whole build, so the installer warns about them and sets nothing. Put them in the configuration header instead.

A library made for Arduino that ships its own `library.properties`, listed under `extras`, `headers` or `sources` so it is installed, keeps it: the installer writes one only for a library that has none.

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
