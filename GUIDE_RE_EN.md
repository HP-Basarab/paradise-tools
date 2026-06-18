# 🌍 ENGLISH VERSION

> **📌 Recentering note — summary produced by AI**
>
> This document gathers in one place everything discovered, deduced and validated so far about the Tamagotchi Paradise (memory map, checksums, sprites, ghosts, biomes, save, language, tools, and the investigative method). It serves me as a single reference point to continue the reverse-engineering work.
>
> It exists in **two versions in this file**: first the **French version** (above), then a **complete English translation** in a dedicated section at the end, to also document in English.

---

# 🛠️ The Complete Guide: Hacking the Tamagotchi Paradise from A to Z

> **For whom?** This guide is written for two people at once:
> - **The complete beginner** 🟢 — who has never opened a hex editor in their life. Every complicated word is explained the first time it appears.
> - **The developer** 🔵 — who wants the exact addresses, the formulas, and copy-ready code.
>
> Read it in order the first time. Afterwards, use the reference tables (§19) and the glossary (§20) like a dictionary.
>
> **Absolute golden rule, to read before everything else:** you always work **on a COPY** of a recent dump of your own console. You never modify the original. If something goes wrong, you re-flash the original and everything comes back as before. With this, **you cannot permanently break your console** as long as the chip itself responds.

---

## 📑 Table of contents

0. [How to read this guide](#en0)
1. [What is this, exactly?](#en1)
2. [The absolute basics](#en2) — bit, byte, hexadecimal, address, little-endian
3. [The hardware and the wiring](#en3)
4. [Step 1 — Reading the chip (making a "dump")](#en4)
5. [Step 2 — What's inside the .bin file](#en5) — the memory map
6. [Encryption (and why you almost never need it)](#en6)
7. [Checksums — the heart of hacking](#en7)
8. [Step 3 — Modifying the save](#en8)
9. [Characters: identity, stages, biome](#en9)
10. [Sprites and appearance](#en10)
11. [Eye/mouth positions (animations)](#en11)
12. [Ghosts (the "phantom" characters)](#en12)
13. [The biome system](#en13)
14. [Unlock codes](#en14)
15. [Step 4 — Rewriting the chip ("flashing")](#en15)
16. [Advanced tools: Ghidra and SWD](#en16)
17. [Practical recipes ("I want to do X")](#en17)
18. [The Python toolbox](#en18)
19. [Reference tables](#en19)
20. [Glossary for the complete beginner](#en20)
21. [Troubleshooting and safety](#en21)
22. [How all of this was discovered](#en22) — the detective's method

---

<a name="en0"></a>
## 0. How to read this guide

Throughout the document you'll see two kinds of callouts:

> 🟢 **For everyone** — the simple explanation, in plain language, assuming you know nothing.

> 🔵 **Technical detail** — the exact values, addresses, formulas and code. If you're a beginner, you can skip these callouts on the first pass and come back to them later.

The code blocks (on a grey background) are mostly **Python**. Python is a very readable programming language; even without knowing it, you'll often understand what it does by reading the comments (the lines starting with `#`).

---

<a name="en1"></a>
## 1. What is this, exactly?

### The console
The **Tamagotchi Paradise** is a small virtual pet released recently. Inside, there is:
- a **microcontroller** (the "brain"): a **Sonix SNC7330**. It's a chip from the **ARM Cortex-M** family (the same kind of core found in billions of connected objects). It executes instructions in the **Thumb** format (a compact variant of ARM machine language);
- a **flash memory chip**: a **MX25L12835F**. This is where everything is stored: the program, the images, your save. It is **16 megabytes** (we'll see below what that means exactly).

> 🟢 **For everyone** — Picture the console as a mini-computer. The "brain" (SNC7330) reads its instructions and images from a "hard drive" (the MX25L12835F flash). Hacking the console = **reading this hard drive, modifying it, then rewriting it**.

### What "hacking" means here
We're not "pirating" anything illegal: it's **YOUR** toy, and we're doing **reverse engineering** — that is, examining how it works in order to **modify it to our taste**. Concretely, you'll be able to:
- change the **language** of the console,
- rename your planet and your items,
- give yourself **Gotchi Points**, change the **date**, **hunger**, **happiness**,
- **change the appearance** of characters (give them the body/eyes/mouth of another),
- **add or remove** "phantom" characters (ghosts),
- change the **biome** (Sky, Earth, Water, Jade).

### The starting vocabulary
- **Firmware**: the software embedded in the console (the program + the data). It's everything that's on the flash.
- **Dump**: an **exact copy** of the flash contents, saved to a file on your PC (a `.bin` file). "Making a dump" = reading the chip and saving its contents.
- **Flashing**: the reverse operation — **writing** a `.bin` file to the chip.
- **Patching**: modifying the `.bin` file (on your PC) before re-flashing it. A "patch" is a modification.

---

<a name="en2"></a>
## 2. The absolute basics

This section is **fundamental** if you're a beginner. Take 10 minutes; afterwards, everything else flows naturally.

### 2.1 Bit and byte
- A **bit** is the smallest possible piece of information: `0` or `1`.
- A **byte** = **8 bits** grouped together. A byte can represent a number from **0 to 255** (256 possible values).

Your 16-megabyte flash therefore contains roughly **16 million bytes** — each being a small number between 0 and 255.

### 2.2 Hexadecimal (base 16)
Humans count in base 10 (digits 0 to 9). Computer people often write bytes in **hexadecimal** (base 16) because it's more convenient. In hex, the "digits" go from 0 to 15, but since we don't have symbols for 10–15, we use the letters **A to F**:

| Decimal | 0 | 1 | … | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|
| Hex | 0 | 1 | … | 9 | A | B | C | D | E | F |

- We prefix hex with **`0x`** to distinguish it. So `0x0A` = 10, `0xFF` = 255, `0x10` = 16.
- **A byte is written with exactly 2 hex digits** (from `0x00` to `0xFF`). That's why we see sequences like `13 02 03 06`: those are 4 bytes.

> 🟢 **For everyone** — Just remember: `0xFF` = 255 = "byte all 1s" = the maximum value of a byte. An area "full of FF" is a **blank** (erased) area.

### 2.3 Address and offset
The flash is a long row of 16 million slots, numbered starting from 0. The number of a slot is called its **address** (or **offset**, synonymous here). It's written in hex.

- Address `0x0` = the very first byte.
- Address `0xEFE000` = byte number 15,720,448 (that's where your save begins, as we'll see).

When we say "the language field is at **save+0x7B**", it means: "start from the beginning of the save, move forward by `0x7B` (= 123) bytes, and read there".

### 2.4 Reading a number across several bytes: u8, u16, u32
A single byte only goes up to 255. To store larger numbers, several are combined:
- **u8** = *unsigned 8-bit* = 1 byte (0 to 255).
- **u16** = *unsigned 16-bit* = 2 bytes (0 to 65,535).
- **u32** = *unsigned 32-bit* = 4 bytes (0 to ~4.2 billion).

The **`s`** instead of the **`u`** (e.g. **s16**) means **signed**: the number can be negative (useful for on-screen positions, e.g. `oy = -33`).

### 2.5 Little-endian (VERY important)
When a number spans several bytes, in what order are they stored? The SNC7330 uses **little-endian**: **the least significant byte is written first**.

A concrete example. The number **`0x1234`** (u16) is stored in memory as: `34 12` (the low-order byte `0x34` first, then `0x12`).

Another example, a u32: **`0x3745D94A`** is stored as `4A D9 45 37`.

> 🟢 **For everyone** — If you see `4A D9 45 37` in an editor and you want the "real" number, you **reverse the byte order**: `37 45 D9 4A` → `0x3745D94A`. This is beginner mistake #1. All the tools in this guide handle this for you, but you need to know it to read a dump by hand.

> 🔵 **Technical detail** — In Python, the `struct` module reads little-endian with the `<` prefix:
> ```python
> import struct
> def u16(b, o): return struct.unpack_from("<H", b, o)[0]   # H = u16
> def u32(b, o): return struct.unpack_from("<I", b, o)[0]   # I = u32
> def s16(b, o): return struct.unpack_from("<h", b, o)[0]   # h = s16 (signed)
> # b = the file contents (bytes), o = the offset to read at
> ```

### 2.6 What is a hex editor?
It's a piece of software that displays a file **byte by byte** in hex, in a grid. Each line shows an address, then 16 bytes, then their "text" version. It's the basic tool for looking at a dump.
- Free examples: **HxD** (Windows, very simple), **ImHex** (cross-platform, more advanced), **010 Editor** (paid, powerful).
- In this guide, we'll do most modifications with **small Python programs** or **prepared web editors** — safer and faster than by hand. But knowing how to open a dump in HxD to "see" is valuable.

### 2.7 What is a checksum? (overview)
A **checksum** is a small number computed from a block of data, used to **verify that the data is not corrupted**. If you modify a byte without recomputing the checksum, the console can detect the inconsistency and **refuse** the data.

> 🟢 **For everyone** — Think of the checksum like the "total" at the bottom of a store receipt. If you change a price without changing the total, it no longer adds up. When modifying the firmware, you often have to **recompute the total**. That's the whole subject of §7, and it's the secret to clean hacking.

---

<a name="en3"></a>
## 3. The hardware and the wiring

### 3.1 What you need
1. **An SPI programmer.** It's the box that talks to the flash chip. You're using a **CH347** (excellent, fast). A known alternative is the **CH341A** (cheaper, slower, 3.3 V mandatory).
2. **The Asprogrammer software** (by *nofeletru*, also called *UsbAsp-flash*). It's the interface on your PC that drives the CH347.
3. **Something to connect to the chip.** Two cases:
   - the chip is on a socket or you've desoldered it → a **SOIC8 adapter/clip**;
   - you want to avoid soldering → a **SOIC "clip"** that clamps onto the chip, or **pogo pins** (small spring-loaded points) on the board's **test pads** (see §19.5).

> 🟢 **For everyone** — The programmer is a translator between your PC (USB) and the chip (SPI protocol). Asprogrammer is the application that tells it "read" or "write". The clip/pogo pins are just the physical means of touching the right pins of the chip.

### 3.2 The chip: MX25L12835F
- **Capacity: 128 Mbit = 16 MB = `0x1000000` bytes.** (128 Mbit ÷ 8 = 16 MB.)
- **Type: SPI flash.** SPI = a simple serial communication protocol over 4 wires.
- **Internal organization:** memory is read byte by byte, but **writing is done in pages of 256 bytes** and **erasing in sectors of 4 KB** (0x1000 bytes). You cannot rewrite a byte "over" another: you must **erase** first (erasing sets everything to `0xFF`), then **program**.
- Equivalent variants you may encounter: **MX25L12833F**, **KH25L12833FM2I-10G** (Macronix). Same size, same behavior.

> 🔵 **Technical detail — SPI commands of the MX25L** (useful if you write a `.pas` script, §15):
> | Command | Byte | Role |
> |---|---|---|
> | READ | `0x03` | read data |
> | Page Program | `0x02` | write a page (256 b) |
> | Write Enable (WREN) | `0x06` | allow writing (mandatory before every write/erase) |
> | Read Status Register | `0x05` | read the status; **bit 0 = WIP** (Write In Progress) |
> | Sector Erase 4K | `0x20` | erase a 4 KB sector |
> | Block Erase 64K | `0xD8` | erase a 64 KB block |
> | Chip Erase | `0xC7` | erase **the entire** chip |
> | Write Status Register | `0x01` | write the status register (unlock) |

### 3.3 Physical precautions
- **Always 3.3 V**, never 5 V (you'd fry the chip). The CH347/CH341A have a selector or a 3.3 V version.
- Align the chip's **pin 1** with pin 1 of the clip (a dot or marker indicates pin 1).
- If the console is powered on while you connect with the clip, there can be conflicts; ideally the chip is read with the SNC7330 powered down (or you hold the console in reset — see RST test pads §19.5).

---

<a name="en4"></a>
## 4. Step 1 — Reading the chip (making a "dump")

This is the very first operation, and the most important: **getting a copy of your console**.

### 4.1 The procedure in Asprogrammer
1. Plug the CH347 into USB, connect the clip/pogo pins to the chip.
2. Open **Asprogrammer**.
3. At the top, choose the **programmer type**: `CH347`.
4. Click **Detect** (or the chip detection icon). Asprogrammer should recognize a **MX25L12835F** (or equivalent). If it's not auto-detected, select it manually from the Macronix list (size 128 Mbit).
5. Click **Read IC** (read the chip). Reading the 16 MB takes from a few seconds to a minute depending on the programmer.
6. **File → Save**: save the result as `.bin`. **Name it clearly and with a date**, for example `my_console_sky_2026-06-17.bin`.

> 🟢 **For everyone** — "Read IC" copies the chip to the Asprogrammer window (a built-in hex editor). "Save" writes that copy to a file on your PC. This `.bin` file **IS** your dump.

### 4.2 The golden rule (again)
- **Keep this original dump intact, separate, forever.** It's your safety net: if a modification fails, you re-flash this file and the console returns exactly to its prior state.
- **You always work on a COPY** of this file, never on the original.
- When you make an important modification (changing the active character, the biome…), first make a fresh dump: it contains your most recent progress.

### 4.3 Verify the dump is good
A valid dump is **exactly 16,777,216 bytes** (16 MB). If the size is different, the read failed (bad clip contact most often) → start over.

> 🔵 **Technical detail** — Quick check in Python:
> ```python
> data = open("my_console_sky_2026-06-17.bin", "rb").read()
> print(len(data), "bytes")           # should print 16777216
> print(hex(len(data)))               # should print 0x1000000
> # Small consistency test: the very beginning contains the "load table"
> print(data[0:8])                    # should contain b"SONIXDEV"
> ```
> If `data[0:8]` is indeed `b'SONIXDEV'`, your dump starts correctly.

---

<a name="en5"></a>
## 5. Step 2 — What's inside the .bin file (the memory map)

The 16 MB dump is not a formless block: it is **divided into zones**, each with a role. Here's the complete map. Don't memorize it — return to it like a subway map.

### 5.1 The complete memory map

| Address range | Size | Zone | What it's for |
|---|---|---|---|
| `0x0` – `0xFFF` | 4 KB | **Firmware header** | boot information (bootrom) |
| `0x1000` – `0x10FFF` | 64 KB | **PRAM firmware** | **encrypted code** (AES-256), §6 |
| `0x11000` – `0x10FFFF` | ~1 MB | **XIP code** | the main program, **plaintext** |
| `0x110000` – `0x110FFF` | 4 KB | **DPD firmware** | persistent bootrom data |
| `0x111000` – `0x8286C3` | ~8 MB | **Assets** | images, texts, game data ("ARC2" archive) |
| `0x8286C4` – `0xD48FFF` | ~5 MB | **Unused** | filled with `0xFF` |
| `0xD49000` – `0xD49FFF` | 4 KB | **Version block** ⭐ | the **biome flag** + checksum, §13 |
| `0xD4A000` – `0xD4DFFF` | 16 KB | **DL items staging** | downloaded items waiting |
| `0xD4E000` – `0xDEDFFF` | 640 KB | **DL items stored** | "lab" items (40 slots of `0x4000`) |
| `0xDEE000` – `0xE45FFF` | 376 KB | **Ghost data** ⭐ | the "phantom" characters, §12 |
| `0xE46000` – `0xE65FFF` | 128 KB | **Ghost reception** | ghosts received from other consoles |
| `0xE66000` – `0xE85FFF` | 128 KB | **Ghost export** | data to share |
| `0xE86000` – `0xEFDFFF` | 472 KB | **Friend screenshots** | community captures |
| `0xEFE000` – `0xEFEFFF` | 4 KB | **Main save** ⭐ | **your save**, §8 |
| `0xEFF000` – `0xEFFFFF` | 4 KB | **Save backup** | backup copy of the save |
| `0xF00000` – `0xFFFFFF` | 1 MB | **Reserved** | |

The ⭐ are the zones you'll modify most often.

> 🟢 **For everyone** — Three big families to remember:
> 1. **The program** (`0x1000` to ~`0x110000`): the game "engine". We rarely touch it (and the `0x1000`-`0x10FFF` part is encrypted).
> 2. **The assets** (`0x111000` to ~`0x828000`): all the **images** and **texts**. That's where we change appearances and names.
> 3. **The user data** (starting at `0xD49000`): **biome, ghosts, and your save**. That's where we change your progress.

### 5.2 The "ARC2" archives
The assets are stored in a homemade archive format called **ARC2** (a bit like a `.zip` file, but simple). An ARC2 archive can **contain others** (like nested folders).

> 🔵 **Technical detail — structure of an ARC2 archive**
> - **Header, 16 bytes:**
>   - `+0x00`: signature `"ARC2"` (in hex `0x32435241`)
>   - `+0x04`: **checksum** (sum of bytes from `+0x08` to the end) — see §7
>   - `+0x08`: `length` = (total archive size − 16)
>   - `+0x0C`: `num_files` = number of files in the archive
> - **Then an entry table, 16 bytes each:**
>   - `+0x00`: flags (0 = no compression)
>   - `+0x04`: `offset` (relative to the archive start)
>   - `+0x08`: `compressed_length`
>   - `+0x0C`: `uncompressed_length`
> - The **main** archive is at `0x111000`. It contains 3 files: **Data** (game data), **Sprites** (images), **Strings** (texts, which is itself an archive of **9 language tables**).
>
> ```python
> ARC2 = 0x32435241
> def arc2_files(b, base):
>     assert u32(b, base) == ARC2, "not an ARC2 archive"
>     n = u32(b, base+12); out = []
>     for i in range(n):
>         e = base + 16 + i*16
>         out.append({"flags": u32(b,e), "offset": base+u32(b,e+4),
>                     "clen": u32(b,e+8), "ulen": u32(b,e+12)})
>     return out
> ```

You don't need to understand this in detail to use the ready-made tools. But it's useful to know that "modifying an image" = "modifying a byte **inside** an archive", and that this will involve **recomputing the archive's checksum** (§7).

---

<a name="en6"></a>
## 6. Encryption (and why you almost never need it)

### 6.1 The good news first
Out of the 16 MB of the flash, **only one small zone is encrypted**: the **PRAM firmware** (`0x1000` to `0x10FFF`, i.e. 64 KB). **Everything else is plaintext** (directly readable): the XIP code, the assets (images, texts), the ghosts, and **your save**.

> 🟢 **For everyone** — "Encrypted" means scrambled with a secret key: unreadable without the key. "Plaintext" means readable as-is. Since **99% of what you'll modify is plaintext** (images, texts, save, biome, ghosts), **you'll almost never have to touch the encryption.** You can skim this section and come back to it if one day you want to modify the engine code itself.

### 6.2 What it is, for the curious
The encryption uses **AES-256 in CBC mode**, following a scheme specific to Sonix (the microcontroller's brand). The details have been fully understood and verified.

> 🔵 **Technical detail — Sonix V3 encryption scheme (SNC7330)**
> - **Load table** at the very start of the flash (`0x0`, 512 bytes). Observed fields: `MARK="SONIXDEV"`, `TABLE_VERSION=0x5A5A0033` (V3), `LOAD_CFG=0x13` (encrypted + CRC check), `ADDR_USERCODE=0x60001000`, `SIZE_USERCODE=0x10000`, `CRC_CHK_SUM=0x3745D94A` (the CRC32 of the **decrypted** code), and **`AES_KEY` (32 bytes) entirely ZERO** at offset `0x28` (SNC7330 default value).
> - **Device key = `0x5aaf34fb`** (a 32-bit internal fuse). It's the **only true secret key**. It is used only to derive the CBC "initialization vector" (IV).
> - **The AES peripheral works in REVERSED byte order** for keys/IV/blocks. The algorithm:
>   1. *IV material* = `AES_KEY[0:16]` XOR device_key (word by word). Null key ⇒ `[DK, DK, DK, DK]`.
>   2. *Derived IV* = AES-ECB-encrypt(IV material, key = `AES_KEY[16:32]`), in reversed semantics.
>   3. *CBC (V3)*: per block, decrypt then XOR with the IV; the encrypted block becomes the next IV; **the IV is reset to the derived IV every `0x1000` bytes**.
> - **Verification:** the CRC32 of the decrypted code is indeed `0x3745D94A`, and the ARM "vector table" is valid (SP = `0x1801EE38`, Reset = `0x000002F5` in Thumb). The PRAM code executes in the `0x18000000` region (SRAM).
> - **Decrypt → patch → re-encrypt pipeline verified 100%** (re-encrypting reproduces the original bit for bit). Reference: `github.com/GMMan/snc73xx-firmware-encryption` and `sonix-boot-decrypter`.

### 6.3 The practical lesson
> ⚠️ **Absolutely remember:** to edit **assets**, the **XIP**, the **save**, the **ghosts** or the **biome**, you **NEVER** need to decrypt/re-encrypt anything. The encryption only concerns the 64 KB of PRAM. This is confirmed empirically on the real consoles.

---

<a name="en7"></a>
## 7. Checksums — the heart of hacking

This is **the** section to understand. Once you master checksums, modifying the console becomes mechanical.

### 7.1 The principle (in-depth recap)
When the firmware stores an important block of data, it computes a **small summary number** (the checksum) from that block, and stores it right next to it. Later, it **recomputes** and **compares**: if it doesn't match, the data is considered corrupted.

> 🟢 **For everyone** — So if you modify a byte "by hand" without recomputing the checksum, two things can happen:
> - either the console **rejects** the modification (for the save, for example, it recreates a fresh game),
> - or, if that particular checksum is **not verified at startup** (the case for some), it goes through anyway.
>
> The secret to clean hacking: **after each modification, recompute the right checksum.** All the tools in this guide do it automatically. This section explains which ones exist and how they're computed, so you understand what's happening.

### 7.2 The console's 7 checksums

Here is the summary table. Each row is detailed right after.

| # | What | Where it's stored | How it's computed | Status |
|---|---|---|---|---|
| 1 | **ARC2** (archives) | `+0x04` of the archive | sum of **bytes** from `+0x08` to the end | ✅ cracked |
| 2 | **Ghost** | `+0x00` and `+0x04` of the ghost | sum of **32-bit words**; `w0 + w4 = 0` | ✅ cracked |
| 3 | **Version block** | `0xD49FF8` and `0xD49FFC` | `V = 0xFFFFFC03 − (sum of bytes from 0 to 0xD49FF8)` | ✅ cracked (not verified at boot) |
| 4 | **PRAM code (CRC32)** | load table `+0x24` | standard CRC32 of the decrypted code | ✅ cracked |
| 5 | **Save** | `0xEFE000`, bytes 0-3 | **CRC-16 Rocksoft** over `[+0x04 : +0x1000]` | ✅ **cracked** |
| 6 | **Screenshot** | `+0x00` / `+0x04` of the sprite | sum of 32-bit words; `sum + complement = 0xFFFFFFFF` | ✅ cracked |
| 7 | **TCP chunk** | network packet header | CRC-16 Rocksoft (poly `0x8005`) | ✅ cracked |

> 🟢 **For everyone** — In practice, for 95% of your hacks, you'll use only **three** of them: **#1 (ARC2)** when you touch images/texts, **#2 (ghost)** when you touch ghosts, and **#5 (save)** when you touch your save.

### 7.3 Checksum #1 — ARC2 (image and text archives)
**When to use it:** whenever you modify a byte **inside** an archive (sprite, text, game data).

**Formula:** a simple **sum of all bytes** from `archive + 0x08` to the end of the archive, stored as u32 (little-endian) at `archive + 0x04`.

```python
def arc2_fix_checksum(b, base, total_len):   # total_len = size of the entire archive
    s = sum(b[base+8 : base+total_len]) & 0xFFFFFFFF
    struct.pack_into("<I", b, base+4, s)
```

> ⚠️ **Golden rule of ordering (hard-won lesson):** archives are **nested** (the *Strings* archive is stored INSIDE the *Main* archive). If you modify a text, you must recompute the checksum of **Strings first**, THEN that of **Main**. The reverse corrupts everything. General rule: **always the inner archive before the outer archive.**

### 7.4 Checksum #2 — Ghost
**When to use it:** when you modify, add or remove a ghost (§12).

**Formula:** `w0` (at `+0x00`) = sum of all **32-bit words** from `+0x08` to the end of the record. `w4` (at `+0x04`) = the negation of `w0`, so that **`w0 + w4 = 0`**. This property also serves as a **signature** to spot ghosts in the dump.

```python
def ghost_fix_checksum(b, base):
    tlen = u32(b, base+0x10C)            # length of the record
    end  = base + ((tlen + 3) & ~3)      # rounded up to a multiple of 4
    s = 0
    for o in range(base+8, end, 4):
        s = (s + u32(b, o)) & 0xFFFFFFFF
    struct.pack_into("<I", b, base+0,  s)
    struct.pack_into("<I", b, base+4, (-s) & 0xFFFFFFFF)
```

### 7.5 Checksum #3 — Version block
**When to use it:** when you change the **biome** (§13). As a precaution only.

**Formula:** `V = (0xFFFFFC03 − sum_of_bytes(from 0 to 0xD49FF8)) modulo 2³²`. We store `V` at `0xD49FF8` and its binary complement `~V` at `0xD49FFC` (invariant: `V XOR ~V = 0xFFFFFFFF`).

```python
def calc_version_checksum(data):
    MAGIC, END = 0xFFFFFC03, 0xD49FF8
    s = sum(data[:END]) & 0xFFFFFFFF
    V = (MAGIC - s) & 0xFFFFFFFF
    return V, (~V) & 0xFFFFFFFF
```

> ⭐ **Important discovery:** this checksum is **NOT verified at startup.** We proved it: a real console whose checksum is *invalid* **still works**, and a firmware edited with this invalid checksum **booted**. So for asset/save/ghost edits, **you don't need to recompute it**. We only recompute it as a precaution during a biome change.

### 7.6 Checksum #5 — Save (your save) ✅ cracked
**When to use it:** **every time** you modify your save (language, points, character, date, hunger, happiness…). Unlike #3, **this one IS verified**: a save with the wrong checksum is rejected (the console recreates a fresh game).

**Algorithm: CRC-16 "Rocksoft".** It's a 16-bit CRC with these precise parameters:
- polynomial **`0xA001`** ("reflected" form of the `0x8005` standard),
- initial value **`0x0000`**,
- input and output **reflected** (*refin = refout = true*),
- no final XOR (*xorout = 0*).

It's computed over the bytes **`[save+0x04 : save+0x1000]`** (the entire contents of the save bank **except** the first 4 bytes, which contain the checksum itself). We store the result as u16 (little-endian) at **`save+0x00`**, and its complement at **`save+0x02`**.

```python
def crc16_rocksoft(data):
    crc = 0x0000
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if (crc & 1) else (crc >> 1)
    return crc & 0xFFFF

def save_fix_checksum(b, save_base):                 # save_base = 0xEFE000 or 0xEFF000
    crc = crc16_rocksoft(b[save_base+0x04 : save_base+0x1000])
    struct.pack_into("<H", b, save_base+0x00, crc)
    struct.pack_into("<H", b, save_base+0x02, (~crc) & 0xFFFF)
```

### 7.7 Checksums #4, #6, #7 (for the record)
- **#4 — CRC32 of the PRAM code** (poly `0xEDB88320`, the standard CRC32): only if you modify the encrypted engine code. Rare.
- **#6 — Screenshot**: sum of the 32-bit words of a capture sprite, with `sum + complement = 0xFFFFFFFF`. Only to tinker with community screenshots.
- **#7 — TCP chunk**: CRC-16 Rocksoft (poly `0x8005`) over network packets, useful only for console-to-console communication (advanced protocol, outside this guide).

---

<a name="en8"></a>
## 8. Step 3 — Modifying the save

Here's the most rewarding part for getting started: changing your progress. That's where we give points, change the language, etc.

### 8.1 The two banks (main + backup)
The save exists in **duplicate**:
- **main bank** at `0xEFE000` (4 KB),
- **backup bank** at `0xEFF000` (4 KB).

The console chooses a **valid** bank (with the right checksum) to load your game.

> 🟢 **For everyone — the rule to make your modification "take":** modify the **main bank**, recompute its checksum (#5), then **fill the backup bank with `0xFF`** (blank area). This way the console has only one valid save — yours — and uses it for sure. If you leave an old valid backup, the console might load the old one instead.

> 🔵 **Technical detail** — In practice the tool: (1) writes the new values to `0xEFE000`, (2) calls `save_fix_checksum(b, 0xEFE000)`, (3) fills `0xEFF000`–`0xEFFFFF` with `0xFF`. This is the hardware-validated behavior (the "backup" bug of the early versions came from forgetting this step).
> ```python
> for o in range(0xEFF000, 0xF00000):   # clear the backup bank
>     b[o] = 0xFF
> ```

### 8.2 The save map (offsets relative to the start of the bank)

| Offset | Type | Field | Notes |
|---|---|---|---|
| `+0x00` | u16 | **CRC-16** | checksum #5 |
| `+0x02` | u16 | **CRC complement** | `~CRC` |
| `+0x1C` | u16 | **Year** | console date |
| `+0x1E` | u16 | **Month** | |
| `+0x20` | u16 | **Day** | |
| `+0x22` | u16 | **Hour** | |
| `+0x24` | u16 | **Minute** | |
| `+0x26` | u16 | **Second** | |
| `+0x64` | u32 | **Device UID** | unique identifier |
| `+0x68` | text | **Planet name** | 16-bit codes, max 12 characters (§10.5 for the encoding) |
| `+0x7B` | u8 | **Language** | **4=EN, 5=DE, 6=FR, 7=ES, 8=IT** |
| `+0xA8` | u16 | **Number of days** | age of the game in days |
| `+0xB4` | u16 | **Gotchi Points** | max 65535 |
| `+0x108` | u16 | **chara_id** (active character) | the identity of the living character (§9) |
| `+0x10A` | u16 | **eye_chara_id** | the identity of the eyes |
| `+0x10C` | u16 | **Age timer** | progression toward the next stage |
| `+0x120` | u8 | **Hunger ("yum")** | max 6 |
| `+0x121` | u8 | **Happiness (mood)** | max 20 |

> 🟢 **For everyone** — Example: to switch the console to **French**, you set the byte at `save+0x7B` to the value **6**. To give yourself the **maximum Gotchi Points**, you write **65535** (`0xFFFF`) as u16 at `save+0xB4`. Each time, you **recompute checksum #5** and **clear the backup**, otherwise it won't "take".

### 8.3 Complete end-to-end example (changing the language to French)
```python
import struct
SAVE = 0xEFE000
b = bytearray(open("my_copy.bin", "rb").read())   # we work on a COPY

# 1) modify the language field (FR = 6)
b[SAVE + 0x7B] = 6

# 2) recompute the main save's checksum
def crc16_rocksoft(data):
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if (crc & 1) else (crc >> 1)
    return crc & 0xFFFF
crc = crc16_rocksoft(b[SAVE+0x04 : SAVE+0x1000])
struct.pack_into("<H", b, SAVE+0x00, crc)
struct.pack_into("<H", b, SAVE+0x02, (~crc) & 0xFFFF)

# 3) clear the backup bank
for o in range(0xEFF000, 0xF00000):
    b[o] = 0xFF

# 4) save the result (file to flash)
open("my_copy_FR.bin", "wb").write(b)
print("OK — flash my_copy_FR.bin")
```

> 🔵 **Important note (update vs old notes)** — The save checksum **was** considered "unsolved" in older documents. It is now **cracked** (CRC-16 Rocksoft, above) and verified. This unlocks **all** save modifications: active character, date, points, hunger, happiness, language, planet name. You no longer need SWD or Ghidra for this.

---

<a name="en9"></a>
## 9. Characters: identity, stages, biome

### 9.1 The `chara_id`
Each character in the game has a unique **numeric identifier**, the `chara_id`. It's what says "this character is HORHOTCHI" or "this character is a baby". A few examples:

| chara_id | Name | Stage / biome |
|---|---|---|
| 1001 | BABYMARUTCHI | baby |
| 2004 | SKY KID | child (Sky) |
| 3016 | ROCKY YOUNG | teen (Sky) |
| 4050 | **HORHOTCHI** | adult (Sky) |
| 4058 | KUCHIPATCHI | adult (Sky) |
| 4065 | MAGMATCHI | adult (Sky) |
| 4022 | MAMETCHI | adult (Earth) |
| 4041 | URUOTCHI | adult (Water) |

> 🔵 **Technical detail — ID ranges by biome:** baby `1001`; children `2002`-`2004`, `2069`; teens `3005`-`3016` and `3070`-`3073`; **Earth `4017`-`4033`**; **Water `4034`-`4049`**; **Sky `4050`-`4065`**; specials `4066`-`4068`; **Forest/Jade `4074`-`4090`**; lab items `4800`-`4803`. The full list is in §19.1.

### 9.2 The life stages
A Tamagotchi evolves: **egg → baby → child → teen → adult**. The stage is tied both to the `chara_id` (a baby has a baby id) and to an **age timer** in the save (`save+0x10C`). Forcing a stage requires changing the `chara_id` **and** resetting this timer — it's an advanced operation.

### 9.3 The food chain (who becomes what)
In each biome, there are **16 characters**, organized into **4 chains of 4** (based on the food you give). For example, in the Sky: the "chicken" chain leads to HORHOTCHI, the "corn" chain to KUCHIPATCHI, etc.

> 🔵 **Technical detail** — In the character table (§10.4), the `+0x08` field encodes membership in a chain (`0x12D`-`0x130` for the Sky). The `+0x0E` field encodes the biome (1=Earth, 2=Water, 3=Sky). **Warning:** the `+0x04` field of this record is a **trap** — it is NOT the index of the displayed sprite (see §10.3).

---

<a name="en10"></a>
## 10. Sprites and appearance

### 10.1 What is a sprite?
A **sprite** is a small image (a drawing) used by the game: a character's body, its eyes, its mouth, an object… All the game's images are sprites, stored in the **Sprites package** of the main archive.

> 🔵 **Technical detail** — The Sky's Sprites package contains **1449 sprites**. It starts with an **offset table** (a directory that says where each sprite is), followed by the data. Each sprite has a **24-byte header** then its pixels.
> ```python
> MAIN = 0x111000
> # 16b entries at MAIN+16 (file0=Data), +32 (file1=Sprites), +48 (file2=Strings)
> f1_off = u32(b, MAIN+32+4)          # offset of the Sprites package
> SPK = MAIN + f1_off
> nspr = u32(b, SPK) // 4             # number of sprites = first offset / 4
> offs = [u32(b, SPK + i*4) for i in range(nspr)]   # the offset table
> ```
> Sprite header (24 b): `+0x00` data_length(u32), `+0x04` flags, `+0x05` bpp (0=1, 1=2, 2=4, 3=8 bits/pixel), `+0x06` num_sprites(u16), `+0x08` width, `+0x09` height, `+0x0A` offset_x(s8), `+0x0B` offset_y(s8), `+0x0C` image_w, `+0x0D` image_h, then palette and pixels. Pixels can be **RLE-compressed** (flag `0x20`) and/or **XORed with `0x53`** (flag `0x80`).

### 10.2 The key discovery: one character = 6 sprites
An adult character is **not a single drawing**: it is composed of **6 consecutive sprites**:
1. body (large size, 64×64)
2. eyes (large size, 64×32)
3. mouth (large size, 64×32)
4. body (small size, 32×32)
5. eyes (small size, 32×16)
6. mouth (small size, 32×16)

The "large" version is used for normal display, the "small" one for certain scenes (menus, mini-views).

> 🔵 **Technical detail — HORHOTCHI (reference):** sprites **#531** (body 64×64), **#532** (eyes 64×32), **#533** (mouth 64×32), **#534** (small body 32×32), **#535** (small eyes 32×16), **#536** (small mouth 32×16).

### 10.3 ⚠️ THE #1 trap to avoid
In the character table, the `+0x04` field looks like a sprite index — **but it is not one.** For HORHOTCHI, `+0x04` is 577, whereas its displayed sprites are **531-536**. If you trust `+0x04`, you copy the wrong sprites (e.g. `sprite[586]` which are the *eyes* of BATATCHI, not a body).

> 🟢 **For everyone** — **Rule:** to know which sprites make up a character, **use the mapping below** (verified on hardware with the **tamasprite** tool), never the `+0x04` field.

> 🔵 **Technical detail — mapping of the 16 Sky adults** (formula: `first_sprite = 531 + (rank−33)×6`):
> | Rank | ID | Name | Sprites |
> |---|---|---|---|
> | 33 | 4050 | HORHOTCHI | 531-536 |
> | 34 | 4051 | MONGATCHI | 537-542 |
> | 35 | 4052 | EAGLETCHI | 543-548 |
> | 36 | 4053 | BATCHI | 549-554 |
> | 37 | 4054 | PAPILLOTCHI | 555-560 |
> | 38 | 4055 | KABUTOTCHI | 561-566 |
> | 39 | 4056 | TENTOTCHI | 567-572 |
> | 40 | 4057 | HATCHITCHI | 573-578 |
> | 41 | 4058 | KUCHIPATCHI | 579-584 |
> | 42 | 4059 | BATATCHI | 585-590 |
> | 43 | 4060 | PEACOTCHI | 591-596 |
> | 44 | 4061 | KIWITCHI | 597-602 |
> | 45 | 4062 | GEMTCHI | 603-608 |
> | 46 | 4063 | ORETATCHI | 609-614 |
> | 47 | 4064 | ISHIKOROTCHI | 615-620 |
> | 48 | 4065 | MAGMATCHI | 621-626 |

### 10.4 The character table
> 🔵 **Technical detail** — Records of **30 bytes** (`0x1E`), id at `+0x00`. **Sky: at `0x126ACA`. Jade: at `0x127690`.** Fields: `+0x02` global index, `+0x04` (the trap), `+0x08` food chain, `+0x0E` biome. The `+0x12`/`+0x14` fields have been tested: they **do NOT control** visual placement.

### 10.5 Changing sprites in practice: tamasprite
Since the sprites are **compressed** and of **different sizes** from one character to another, you can't simply "copy-paste" the bytes of one sprite onto another in the dump (the lengths don't match, it breaks the archive). The right method:

- **tamasprite**: a web tool that **displays** each sprite by its index (#531, #549…) and lets you **re-import** an image into a slot. It's the ideal tool to **graphically replace** one character with another (e.g. give HORHOTCHI's body to all adults), because it **recompresses and repacks** the archive correctly for you.

> 🟢 **For everyone** — So to **change the drawing** of a character: you go through **tamasprite** (import an image into the right slot). To change **where** its eyes/mouth sit (without changing the drawing), that's a different piece of data — the "composite definitions" of the next section.

### 10.6 Text encoding (charset)
Names (planet, items, characters) are not in simple ASCII: each character is a **16-bit code**.

> 🔵 **Technical detail** — `0x131` = space; `0x132`-`0x13B` = digits 0-9; **letters: `code = 0x00FD + ASCII_value`** (so 'A' (0x41) → `0x013E`); accents: `0x197`=É, `0x196`=Ç, `0x199`=Ê, `0x1AA`=Ñ; `0x178` = apostrophe.
> ```python
> def decode_char(ci):
>     if ci == 0: return None                       # end of string
>     if ci == 0x0131: return ' '
>     if 0x0132 <= ci <= 0x013B: return chr(ord('0') + (ci - 0x0132))
>     if ci >= 0x00FD:
>         a = ci - 0x00FD
>         if 0x20 <= a <= 0x7E: return chr(a)
>     return '?'
> def encode_char(c):
>     if c == ' ': return 0x131
>     if '0' <= c <= '9': return 0x132 + (ord(c) - ord('0'))
>     o = ord(c)
>     if 0x20 <= o <= 0x7E: return 0x00FD + o
>     return None
> ```

> ⚠️ **Two notions of "language" not to confuse:**
> - the **language table index in the Strings archive**: **French = index 2** (to rename texts);
> - the **device language byte** (`save+0x7B`): **French = 6** (for the interface). These are two different things.

---

<a name="en11"></a>
## 11. Eye/mouth positions (animations) — the "composite definitions"

This is the most subtle subject, and a **piece of good news**: it is now understood and editable.

### 11.1 The problem
When you give HORHOTCHI's body to another character (via the sprites), you notice that **the eyes and mouth remain badly placed**. Why? Because **the position** where each sprite is placed is **not** in the sprite itself: it's in a separate piece of data called a **"composite definition"**. In plain terms: *"where to place each piece when drawing the character"*.

### 11.2 Where it lives
> 🔵 **Technical detail** — The composite definitions of the 16 Sky adults begin at **`0x167C70`** in the dump (it's in the **Data** file of the main archive, relative offset `0x56C30`). **These bytes are directly readable in the dump** (contrary to what older notes suggested — it's only **Ghidra** that doesn't "see" them, because this zone is not loaded in the XIP code, §16).

### 11.3 The structure
> 🔵 **Technical detail**
> - Each adult is described by **exactly 112 "layers"**, in the **same order** for all characters.
> - A layer is: `sprite_id (u16)` + `packed (u16)` + `ox (s16)` + `oy (s16)` + a variable-size *trailer*.
> - The negative `oy` values (e.g. `-33` = `0xFFDF`, `-32` = `0xFFE0`) are the **vertical positions** — that's what changes from one character to another.
> - **Role of each layer:** 0 = body, 1 = eyes, 2 = mouth, 3 = small body, 4 = small eyes, 5 = small mouth.
> - **Shared sprites NOT to remap:** 204, 205, 206 (common shadows/effects).
> - **Block start addresses** (16 adults):
>
> | Body | Name | Block start |
> |---|---|---|
> | 531 | HORHOTCHI | `0x167C70` |
> | 537 | (rank 34) | `0x168354` |
> | 543 | (rank 35) | `0x168A38` |
> | 549 | (rank 36) | `0x16911C` |
> | 555 | (rank 37) | `0x169802` |
> | 561 | (rank 38) | `0x169EE8` |
> | 567 | (rank 39) | `0x16A5CC` |
> | 573 | (rank 40) | `0x16ACB2` |
> | 579 | (rank 41) | `0x16B396` |
> | 585 | (rank 42) | `0x16BA7A` |
> | 591 | (rank 43) | `0x16C15E` |
> | 597 | (rank 44) | `0x16C842` |
> | 603 | (rank 45) | `0x16CF28` |
> | 609 | (rank 46) | `0x16D60C` |
> | 615 | (rank 47) | `0x16DCF0` |
> | 621 | (rank 48) | `0x16E3D4` |

### 11.4 The "relative" (delta) model — the right way to patch
We want all adults to look like HORHOTCHI **and keep its animations**. But the positions **vary slightly from one frame to another** (the body breathes, the eyes blink: `oy` goes from -33 to -35, etc.). If we "flattened" everything to a single value, we would **destroy the animations** (frozen eyes).

The right method is therefore **relative**:
> **Final position of a layer = HORHOTCHI's position for that layer + an offset (delta) specific to the character.**
- delta **0** ⇒ the character is **identical to HORHOTCHI** (positions AND animations preserved);
- non-zero delta ⇒ we uniformly shift that role (e.g. eyes +2) **without breaking** the animation.

> 🟢 **For everyone** — Concretely, we take HORHOTCHI's complete animation as a **template** for everyone. If you want a character to have eyes 2 pixels lower, you set a delta of +2 on its eyes — and it applies to all frames without damaging the movement.

> 🔵 **Technical detail** — After rewriting the `oy`/`ox` of the layers, **recompute the ARC2 checksum of the main archive** (§7.3). It's the only impacted checksum; the save is not touched. The `patcher_offsets_relatif.py` (provided in your tools) reads the HORHOTCHI base **into memory first** (so that a delta on HORHOTCHI doesn't corrupt the base of the others), applies base+delta to each layer, then recomputes the ARC2.

---

<a name="en12"></a>
## 12. Ghosts (the "phantom" characters)

### 12.1 What is it?
**Ghosts** are character records stored in a dedicated zone — basically, the characters you've met/collected, plus the active character. They occupy the zone **`0xDEE000`–`0xE45FFF`**.

### 12.2 How we spot them (signature scan)
The console (and our tools) **scan** the zone looking for valid records, recognized by their **checksum signature** (#2: `w0 + w4 == 0`). No list needed: a slot contains a ghost if it has a consistent checksum.

> 🔵 **Technical detail — ghost scan**
> ```python
> def scan_ghosts(b, start=0xC00000, end=0x1000000, step=4):
>     found = []
>     o = start
>     while o < end - 0x120:
>         w0 = u32(b, o)
>         if w0 != 0 and ((w0 + u32(b, o+4)) & 0xFFFFFFFF) == 0:
>             tlen = u32(b, o+0x10C)
>             if 0x1000 <= tlen <= 0x8000:
>                 stop = o + ((tlen + 3) & ~3)
>                 if stop <= len(b):
>                     s = 0
>                     for q in range(o+8, stop, 4):
>                         s = (s + u32(b, q)) & 0xFFFFFFFF
>                     if s == w0:
>                         found.append(o); o = stop; continue
>         o += 4
>     return found
> ```

### 12.3 The structure of a ghost
> 🔵 **Technical detail** — `+0x00` w0 (checksum), `+0x04` w4 (complement), `+0x08` flags (type), `+0x0C` **character_id (u16)**, `+0x0E` eye_character_id, `+0x10` color, `+0x10C` **total_length (u32)**, **embedded name at `+0x2C` and `+0x46`** (16-bit codes, §10.6).
> - **Sky:** `+0x0C` = the real character_id.
> - **Jade:** `+0x0C` = stage marker (4017 for all adults); the real identity is at **`+0x10A`**; the **embedded name** remains reliable.

### 12.4 Slot layout
> 🔵 **Technical detail** — The zone is divided into slots of `0x2000`, but a ghost in practice occupies **`0x4000`** (16 KB) — so ghosts fall on **even** slots (0, 2, 4…). An **empty** slot is **entirely `0xFF`** (blank flash). **Slot 0** (`0xDEE000`) is the **active character**: we don't delete it. Slot number = `(address − 0xDEE000) / 0x2000`.

### 12.5 Adding / removing a ghost
We verified two essential things: (a) empty slots are `0xFF`, and (b) **there is no ghost counter** in the save to maintain. The resulting model:
- **Adding a character** = **copy the complete record** of an existing ghost into an empty slot (aligned to `0x4000`), then **recompute its checksum #2**. A re-scan then detects it as one more ghost.
- **Removing a character** = **fill its slot with `0xFF`**.

> 🟢 **For everyone** — This assumes the console **scans** the slots (very likely, since no counter exists). **To be confirmed by a hardware test**: add ONE ghost, flash, see if it appears. If so, the mechanism is validated and you can add/remove freely. The provided ghost editor does all this (copy + checksum + protection of slot 0).

> 🔵 **Technical detail — adding a ghost**
> ```python
> def add_ghost(b, empty_base, src_base):       # empty_base aligned to 0x4000, all 0xFF
>     tlen = u32(b, src_base+0x10C); rec = (tlen + 3) & ~3
>     b[empty_base:empty_base+rec] = b[src_base:src_base+rec]
>     ghost_fix_checksum(b, empty_base)         # cf. §7.4
> def remove_ghost(b, base):
>     for o in range(base, base+0x4000):
>         b[o] = 0xFF
> ```

---

<a name="en13"></a>
## 13. The biome system

### 13.1 The two levels (to understand well)
The biome (Earth / Water / Sky / Jade) is managed in **two places**:
1. **A flag in the firmware**, at `0xD49000` (a u32: **1=Earth, 2=Water, 3=Sky, 4=Jade**). This flag is read **only once**: at the **creation of a fresh game**.
2. **Your save**, which once created becomes the **master**: as long as a valid save exists, the biome comes from it and the flag is **ignored**.

### 13.2 How to change biome (validated procedure)
Since the save takes priority, you need **two mandatory actions**:
1. **modify the flag** at `0xD49000` to the desired biome (and **recompute checksum #3** of the version block, as a precaution — §7.5),
2. **erase the save**: fill `0xEFE000`–`0xEFFFFF` with `0xFF`.

Result: at startup, the save being empty/invalid, the console **re-reads the flag**, derives the new biome from it, and **creates a fresh game** on it.

> 🟢 **For everyone** — In plain terms: changing biome = **"I say which biome I want (flag) AND I erase my game to force a new game in this biome".** You **lose your progress** in the process (it's unavoidable, the biome is tied to the game).

> 🔵 **Technical detail** — Earth/Water/Sky share **exactly the same firmware** (0 bytes of difference in code+assets); only the ~11 bytes of the version block differ. **Jade**, however, has a **different** firmware (~10% of assets and code different). The associated config values: Earth/Water/Sky → `f4=0x0001`, `f6=0x0004` (at `0xD49FF4`/`0xD49FF6`); Jade → `f4=0x0002`, `f6=0x0000`.

```python
import struct
VER = 0xD49000
b = bytearray(open("my_copy.bin","rb").read())
struct.pack_into("<I", b, VER, 3)            # 3 = Sky (1=Earth, 2=Water, 4=Jade)
# (recompute the version block checksum, §7.5)
MAGIC, END = 0xFFFFFC03, 0xD49FF8
s = sum(b[:END]) & 0xFFFFFFFF
V = (MAGIC - s) & 0xFFFFFFFF
struct.pack_into("<I", b, 0xD49FF8, V)
struct.pack_into("<I", b, 0xD49FFC, (~V) & 0xFFFFFFFF)
# erase both save banks
for o in range(0xEFE000, 0xF00000): b[o] = 0xFF
open("my_copy_sky.bin","wb").write(b)
```

---

<a name="en14"></a>
## 14. Unlock codes

The game accepts **codes** (entered in the menu, or via QR/shop) to unlock content.

> 🔵 **Technical detail** — The main code table is at **`0x9BA6C`**: **109 codes**, **9 bytes each**, in **raw ASCII**. **No checksum** (it's in the plaintext XIP, and checksum #3 is not verified at boot). A **2nd** alphanumeric table is at `0x9BE41` (likely QR/shop codes). You can therefore read/edit these codes directly, without recomputation.

---

<a name="en15"></a>
## 15. Step 4 — Rewriting the chip ("flashing")

Once your `.bin` is modified, you have to **write** it to the chip.

### 15.1 The simple procedure in Asprogrammer
1. Plug in the programmer and the clip/pogo pins (as for reading).
2. Open Asprogrammer, choose `CH347`, do **Detect**.
3. **File → Open**: open your modified `.bin` (it loads into the Asprogrammer editor).
4. **Unprotect / Unlock** if the chip is write-protected.
5. **Erase IC**: erase the chip (set it to `0xFF`). *Mandatory before writing*, because you can't write "over" existing data.
6. **Program IC** (write): Asprogrammer writes your file.
7. **Verify**: it re-reads and compares to confirm the write is correct.

> 🟢 **For everyone** — The order is always: **Unlock → Erase → Write → Verify.** If "Verify" is OK, your modification is in place: reconnect the console and observe. If something is wrong, **re-flash your original dump** (the safety net).

> ⚠️ Asprogrammer **has no command line**: no automation possible, everything is done by clicks in the interface. (Automation by click simulation would be fragile.)

### 15.2 To go further: a `.pas` script
Asprogrammer can run **Pascal scripts** (`.pas`) that define what the Unlock/Erase/Write/Verify buttons do for your specific chip.

> 🔵 **Technical detail** — A `tamagotchi_paradise.pas` script defines:
> - `{$unlock}`: Write Enable (`0x06`) + Write Status Register (`0x01 0x00`) to unlock.
> - `{$erase}`: Write Enable + Chip Erase (`0xC7`) + wait for completion (poll the WIP bit via Read Status `0x05`).
> - `{$write}`: loop in pages of 256 bytes — Write Enable + Page Program (`0x02`) + 3-byte address + data (`SPIWriteFromEditor`).
> - `{$verify}`: read (`0x03`) + comparison with the editor.
>
> To be placed in Asprogrammer's `scripts\` folder. Usage: open the `.bin`, select the script, click Unlock → Erase → Write → Verify.

### 15.3 How long / what risks?
- Erasing + writing 16 MB generally takes **less than a minute** with a CH347.
- **The worst risk** is an interrupted write (clip moves, USB unplugged) → the chip is in an inconsistent state. **Solution: start over (Erase + Write).** As long as the chip responds to the programmer, **nothing is permanent**: you can always re-flash the original.

---

<a name="en16"></a>
## 16. Advanced tools: Ghidra and SWD

You **don't need** them for the common hacks (save, sprites, ghosts, biome). They're useful when you want to **understand the engine code** itself.

### 16.1 Ghidra (code analysis)
**Ghidra** is a free tool (from the NSA) that **disassembles** and **decompiles** machine code: it transforms the program's bytes into something readable.

> 🔵 **Technical detail — loading the XIP code in Ghidra**
> 1. Extract the XIP: the bytes `flash[0x11000:0x110000]` (1,044,480 bytes).
>    ```python
>    open("code_XIP.bin","wb").write(open("dump.bin","rb").read()[0x11000:0x110000])
>    ```
> 2. In Ghidra: import as **Raw Binary**, **Language = `ARM:LE:32:Cortex`**, **Base Address = `0x60011000`**. At analysis, check *ARM Aggressive Instruction Finder*.
> 3. Address correspondence: `exec_address = 0x60011000 + (flash_offset − 0x11000)`.
>
> **Major limitation:** the **assets** (beyond `0x110000`, so everything that is sprites/texts/tables like `0x167C70`) are **NOT** in the XIP — Ghidra doesn't see them. Moreover, the code accesses the assets through **computed addressing** (register + offset), so **no direct cross-reference**. Conclusion: Ghidra is excellent to **start from a text string** and trace the code that uses it; **unsuitable** for a data table. For these tables, **SWD** (below) is far more efficient.

### 16.2 SWD (live debug)
**SWD** (*Serial Wire Debug*) is the **debugging** mode of ARM chips: with **2 wires** (SWDIO + SWCLK), you can **read/write memory and registers live**, set **breakpoints**, single-step **instruction by instruction**.

> 🟢 **For everyone** — It's like putting the console "on pause" to look at what it does, instant by instant. Ideal for solving the mysteries that remain (e.g. "which address exactly does it read to place the eyes?").

> 🔵 **Technical detail**
> - **SWD pins** (on the test pads, no soldering): `SWCLK = P0.13`, `SWDIO = P0.14`, `SWO = P0.12`. Plus GND and RST (see §19.5).
> - **Hardware:** an **ST-Link V2** (~€15) or a **Raspberry Pi Pico** as *picoprobe* (~€5), + a **pogo pin clip** (~€10). No soldering thanks to the test pads.
> - **Software:** OpenOCD + GDB, or pyOCD.
> - Reminder: the bootrom **enables SWD by default** if there's no valid firmware. A patch (`..._no_crypt_with_swd.ips`) can forcibly re-enable it and disable the encryption check.

---

<a name="en17"></a>
## 17. Practical recipes ("I want to do X")

Each recipe follows the same skeleton: **(0) start from a copy of a fresh dump → (1) modify → (2) recompute the right checksum → (3) handle the backup if it's the save → (4) flash → (5) verify on the console.**

### Recipe A — Switch the console to French
1. `b[0xEFE000 + 0x7B] = 6`
2. recompute the **save checksum** (#5) on the main bank
3. **clear the backup bank** (`0xEFF000`–`0xEFFFFF` ← `0xFF`)
4. flash, verify.

### Recipe B — Give the maximum Gotchi Points
1. `struct.pack_into("<H", b, 0xEFE000 + 0xB4, 65535)`
2. save checksum (#5) + clear the backup
3. flash.

### Recipe C — Change the date
1. write year/month/day/hour/minute/second as u16 at `0xEFE000 + 0x1C…0x26`
2. save checksum (#5) + clear the backup
3. flash.

### Recipe D — Rename the planet
1. encode the name in 16-bit codes (§10.6) and write it at `0xEFE000 + 0x68` (max 12 characters, terminate with `0x0000`)
2. save checksum (#5) + clear the backup
3. flash.

### Recipe E — Unify the Sky adults' positions onto HORHOTCHI
1. use the **relative patcher** (delta model, §11.4) with deltas at 0 (or adjust a character)
2. it recomputes the **main ARC2 checksum** (#1); the save is not touched
3. flash, verify the animations.

### Recipe F — Graphically replace a character with HORHOTCHI
1. open the dump in **tamasprite**
2. import HORHOTCHI's sprites (#531-536) into the target character's slots
3. tamasprite repacks and recomputes the ARC2 checksum for you
4. flash.

### Recipe G — Rename a character or item (text)
1. locate the **Strings** archive (Sky at `0x802260`), FR table = **index 2**
2. edit the text **in place** (respect the length)
3. recompute the checksum **Strings first, then Main** (#1, the order is crucial)
4. flash.

### Recipe H — Change a ghost's identity
1. find the ghost (scan, §12.2)
2. change its name (`+0x2C` and `+0x46`) and its id (`+0x0C` in Sky, `+0x10A` in Jade)
3. recompute the **ghost checksum** (#2)
4. flash.

### Recipe I — Add a character in an empty slot
1. copy an existing ghost into an empty slot (aligned `0x4000`, all `0xFF`) + ghost checksum (#2)
2. flash and **verify it appears** (confirms the "scan" model, §12.5).

### Recipe J — Change biome
1. flag at `0xD49000` (1/2/3/4) + version block checksum (#3)
2. **erase both save banks** (`0xEFE000`–`0xEFFFFF` ← `0xFF`)
3. flash (⚠️ you lose your progress).

---

<a name="en18"></a>
## 18. The Python toolbox (copy-paste ready)

```python
import struct

# ---------- basic reading ----------
def load(path): return bytearray(open(path, "rb").read())
def save(path, b): open(path, "wb").write(b)
def u8(b, o):  return b[o]
def u16(b, o): return struct.unpack_from("<H", b, o)[0]
def u32(b, o): return struct.unpack_from("<I", b, o)[0]
def s16(b, o): return struct.unpack_from("<h", b, o)[0]
def wu16(b, o, v): struct.pack_into("<H", b, o, v & 0xFFFF)
def wu32(b, o, v): struct.pack_into("<I", b, o, v & 0xFFFFFFFF)

# ---------- key addresses ----------
MAIN_ARC = 0x111000
VERSION  = 0xD49000
SAVE     = 0xEFE000
SAVE_BAK = 0xEFF000
GHOST_S  = 0xDEE000
GHOST_E  = 0xE46000

# ---------- ARC2 checksum (#1) ----------
def arc2_fix(b, base, total_len):
    s = sum(b[base+8 : base+total_len]) & 0xFFFFFFFF
    wu32(b, base+4, s)

# ---------- ghost checksum (#2) ----------
def ghost_fix(b, base):
    tlen = u32(b, base+0x10C); end = base + ((tlen+3) & ~3)
    s = 0
    for o in range(base+8, end, 4): s = (s + u32(b, o)) & 0xFFFFFFFF
    wu32(b, base+0, s); wu32(b, base+4, (-s) & 0xFFFFFFFF)

# ---------- version block checksum (#3) ----------
def version_fix(b):
    s = sum(b[:0xD49FF8]) & 0xFFFFFFFF
    V = (0xFFFFFC03 - s) & 0xFFFFFFFF
    wu32(b, 0xD49FF8, V); wu32(b, 0xD49FFC, (~V) & 0xFFFFFFFF)

# ---------- save checksum (#5) ----------
def crc16_rocksoft(data):
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if (crc & 1) else (crc >> 1)
    return crc & 0xFFFF

def save_fix(b, base=SAVE):
    crc = crc16_rocksoft(b[base+0x04 : base+0x1000])
    wu16(b, base+0x00, crc); wu16(b, base+0x02, (~crc) & 0xFFFF)

def clear_backup(b):
    for o in range(SAVE_BAK, SAVE_BAK+0x1000): b[o] = 0xFF

# ---------- example: French + max points ----------
if __name__ == "__main__":
    b = load("my_copy.bin")
    b[SAVE + 0x7B] = 6              # FR language
    wu16(b, SAVE + 0xB4, 65535)     # max Gotchi Points
    save_fix(b)                     # save checksum
    clear_backup(b)                 # clear the backup
    save("my_copy_modified.bin", b)
    print("OK")
```

---

<a name="en19"></a>
## 19. Reference tables

### 19.1 Characters (chara_id → name)
| ID | Name | | ID | Name |
|---|---|---|---|---|
| 1001 | BABYMARUTCHI | | 4041 | URUOTCHI |
| 2002 | LAND KID | | 4042 | TACHUTCHI |
| 2003 | WATER KID | | 4043 | SHARKTCHI |
| 2004 | SKY KID | | 4044 | ANKOTCHI |
| 2069 | FOREST KID | | 4045 | OTOTOTCHI |
| 3005-3016 | (teens) | | 4046 | KURARATCHI |
| 4017 | BBMARUTCHI | | 4047 | MENDAKOTCHI |
| 4018 | MEOWTCHI | | 4048 | AMEFURATCHI |
| 4019 | POCHITCHI | | 4049 | GUSOKUTCHI |
| 4020 | GUMAX | | 4050 | **HORHOTCHI** |
| 4021 | RATCHI | | 4051 | MONGATCHI |
| 4022 | MAMETCHI | | 4052 | EAGLETCHI |
| 4023 | MIMITCHI | | 4053 | BATCHI |
| 4024 | MOLMOTCHI | | 4054 | PAPILLOTCHI |
| 4025 | SHEEPTCHI | | 4055 | KABUTOTCHI |
| 4026 | SEBIRETCHI | | 4056 | TENTOTCHI |
| 4027 | LEOPATCHI | | 4057 | HATCHITCHI |
| 4028 | ELIZARDOTCHI | | 4058 | KUCHIPATCHI |
| 4029 | HEAVYTCHI | | 4059 | BATATCHI |
| 4030 | FURAWATCHI | | 4060 | PEACOTCHI |
| 4031 | TUSTUSTCHI | | 4061 | KIWITCHI |
| 4032 | POTSUNENTCHI | | 4062 | GEMTCHI |
| 4033 | SHIGEMI-SAN | | 4063 | ORETATCHI |
| 4034 | IRUKATCHI | | 4064 | ISHIKOROTCHI |
| 4035 | KAMETCHI | | 4065 | MAGMATCHI |
| 4036 | BEAVERTCHI | | 4066 | CHODRACOTCHI |
| 4037 | KUJIRATCHI | | 4067 | MERMARINTCHI |
| 4038 | AXOLOPATCHI | | 4068 | YAYACORNTCHI |
| 4039 | IMORITCHI | | 4074-4090 | (Forest/Jade) |
| 4040 | KAWAZUTCHI | | 4800-4803 | (lab items) |

Biomes: **Earth 4017-4033**, **Water 4034-4049**, **Sky 4050-4065**, specials 4066-4068, **Forest/Jade 4074-4090**.

### 19.2 Save offsets (relative to `0xEFE000`)
| Offset | Type | Field |
|---|---|---|
| +0x00 | u16 | CRC-16 |
| +0x02 | u16 | CRC complement |
| +0x1C…+0x26 | u16 ×6 | year, month, day, hour, minute, second |
| +0x64 | u32 | device UID |
| +0x68 | text | planet name (≤12 chars) |
| +0x7B | u8 | language (4=EN,5=DE,6=FR,7=ES,8=IT) |
| +0xA8 | u16 | number of days |
| +0xB4 | u16 | Gotchi Points |
| +0x108 | u16 | chara_id |
| +0x10A | u16 | eye_chara_id |
| +0x10C | u16 | age timer |
| +0x120 | u8 | hunger (max 6) |
| +0x121 | u8 | happiness (max 20) |

### 19.3 Key firmware addresses
| Address | What |
|---|---|
| `0x0` | header / load table (`SONIXDEV`) |
| `0x1000`–`0x10FFF` | PRAM code (encrypted) |
| `0x11000`–`0x10FFFF` | XIP code (plaintext) |
| `0x111000` | main ARC2 archive |
| `0x126ACA` | character table (Sky) |
| `0x127690` | character table (Jade) |
| `0x167C70` | Sky adults composite definitions |
| `0x802260` | Strings archive (Sky) |
| `0x9BA6C` | code table (109 × 9 b) |
| `0xD49000` | biome flag |
| `0xD49FF8` / `0xD49FFC` | version block checksum / complement |
| `0xDEE000`–`0xE45FFF` | ghosts |
| `0xEFE000` / `0xEFF000` | main save / backup |

### 19.4 Checksum recap
| # | What | Where | Formula | Verified at boot? |
|---|---|---|---|---|
| 1 | ARC2 | archive+0x04 | sum of bytes [+0x08 : end] | yes (assets) |
| 2 | Ghost | ghost+0x00/+0x04 | sum of 32-bit words; w0+w4=0 | yes (scan) |
| 3 | Version block | 0xD49FF8/0xD49FFC | 0xFFFFFC03 − sum of bytes(0..0xD49FF8) | **no** |
| 4 | PRAM CRC32 | load table+0x24 | CRC32 (poly 0xEDB88320) | yes (if encrypted) |
| 5 | Save | 0xEFE000+0x00/+0x02 | CRC-16 Rocksoft over [+0x04 : +0x1000] | **yes** |
| 6 | Screenshot | sprite+0x00/+0x04 | sum of words; sum+comp=0xFFFFFFFF | yes |
| 7 | TCP chunk | network header | CRC-16 Rocksoft (0x8005) | yes (network) |

### 19.5 Test pads (solderless access)
- **SWD:** `P0.13=SWCLK`, `P0.14=SWDIO`, `P0.12=SWO`.
- **UART:** `TP35=P0.2 TXD1`, `TP37=P0.3 RXD1`; `TP48=P0.1 RXD0`, `P0.0=TXD0`.
- **SPI flash:** `TP24=CS`, `TP26=CLK`, `TP27=MISO`, `TP28=MOSI`, `TP30=D2`, `TP31=D3`.
- **Buttons:** `TP34=dial`, `TP36=A`, `TP38=B`, `TP39=C`. **Encoder:** `TP32=P2.0`, `TP33=P2.1`.
- **Power/Reset:** VCC `TP12`/`TP22`; GND `TP29`/`TP46`/`TP49`; RST `TP21`/`TP25(SW1)`/`TP45`; VBAT `TP1`; VREG 3V3 `TP2`.

### 19.6 SPI commands (MX25L12835F)
READ `0x03` · Page Program `0x02` · Write Enable `0x06` · Read Status `0x05` (bit0=WIP) · Sector Erase 4K `0x20` · Block Erase 64K `0xD8` · Chip Erase `0xC7` · Write Status `0x01`.

---

<a name="en20"></a>
## 20. Glossary for the complete beginner

- **Address / offset** — the number of a byte in the flash (written in hex). "save+0x7B" = 123 bytes after the start of the save.
- **Archive (ARC2)** — a homemade container that groups images/texts/data, like a `.zip`. Can contain others.
- **ASCII** — the standard way of encoding letters in computing (A=65…). Here texts use a **different** encoding (16-bit codes, §10.6).
- **Bit / byte** — bit = 0 or 1; byte = 8 bits = a number from 0 to 255.
- **Boot / startup** — the moment the console turns on and loads its firmware.
- **Checksum** — a "control total" that detects modifications/corruption (§7).
- **CRC / CRC-16 / CRC32** — families of checksums based on binary division math. "Rocksoft" is a precise set of CRC-16 settings.
- **Dump** — a complete copy of the chip in a `.bin` file.
- **Firmware** — the embedded software (program + data) of the console.
- **Flash (flash chip)** — the non-volatile memory that keeps everything, even when off. **Flashing** = writing to it.
- **Hexadecimal (hex)** — base 16 (0-9 then A-F), prefixed `0x`. A byte = 2 hex digits.
- **Little-endian** — the SNC7330's byte order: low-order first (`0x1234` → `34 12`).
- **Patch / patching** — a modification / modifying the `.bin`.
- **PRAM** — the **encrypted** code zone (`0x1000`-`0x10FFF`). We almost never touch it.
- **Reverse engineering** — examining how a system works to understand/modify it.
- **Sprite** — a small image (body, eyes, mouth, object…).
- **SPI** — the serial protocol (4 wires) through which the programmer talks to the flash.
- **SWD** — the live debugging mode of ARM chips (2 wires).
- **u8 / u16 / u32 / s16** — a number over 1/2/4 bytes; `s` = signed (can be negative).
- **XIP** — *eXecute In Place*: the **plaintext** code zone (`0x11000`+) executed directly from the flash.

---

<a name="en21"></a>
## 21. Troubleshooting and safety

### 21.1 "The console won't start anymore / black screen"
- **Re-flash your original dump.** This is the solution to 99% of problems. As long as the chip responds to the programmer, nothing is permanent.
- Check that you did **Erase before Write** and that **Verify** passed.

### 21.2 "My save modification doesn't apply"
- You probably forgot to **recompute the save checksum (#5)** or to **clear the backup bank**. Without that, the console rejects your save (or loads the old backup). Redo both.

### 21.3 "I modified an image/text and the game crashes or displays garbage"
- ARC2 checksum **not recomputed**, or **wrong order** (Strings must be recomputed **before** Main). Start over in the right order (§7.3).

### 21.4 "The eyes/mouth are badly placed after a sprite change"
- Normal: the **positions** are in the composite definitions (§11), not in the sprites. Use the **relative patcher** (delta).

### 21.5 "Reading/writing fails randomly"
- Bad clip/pogo pin contact (the most frequent), or unstable power. Reclean, reposition, make sure you're at **3.3 V**. Verify the dump is indeed **16,777,216 bytes**.

### 21.6 Golden rules to never forget
1. **Always start from a copy of a recent dump of YOUR console.**
2. **Keep the original intact** as a safety net.
3. **A risky change = test it on ONE case first.**
4. **After each modification, recompute the right checksum** (and for the save, clear the backup).
5. **3.3 V**, never 5 V.

---

<a name="en22"></a>
## 22. How all of this was discovered (the detective's method)

This section is different from the others: it doesn't tell you *what* to do, but *how* everything above was **found and deduced**. It's the most useful part in the long run, because it teaches you to **crack yourself** what isn't yet documented.

> 🟢 **For everyone** — Reverse engineering is like a police investigation. You don't "crack" a safe by force: you **observe clues**, **form a hypothesis**, **test it**, and **start over** until everything fits. None of the steps below required genius — just method and patience.

### 22.1 The general philosophy
Everything rests on a simple loop, repeated dozens of times:
1. **Observe** (look at the bytes, compare files).
2. **Formulate a falsifiable hypothesis** ("I bet this byte is the language").
3. **Test** (modify, recompute, flash, look at the console).
4. **Keep or discard** the hypothesis based on the result, then start over.

The investigator's golden rule: **what the documentation says is not necessarily what the hardware does.** We always verify on the real console (§22.8 gives a spectacular example).

### 22.2 The queen technique: comparing two dumps (the "diff")
This is **the most powerful** and simplest tool. The principle:
1. you make a dump of the console **before** an action,
2. you do **a single** action on the console (feed the character, change the language, earn points…),
3. you make a dump **after**,
4. you **compare** the two files byte by byte: **only the bytes related to this action change**.

> 🟢 **For everyone** — If you feed your Tamagotchi then compare the two dumps, the byte that changes is (very likely) the hunger counter. This is exactly how the **hunger (`save+0x120`)** and **happiness (`save+0x121`)** fields were located: a targeted action, a diff, and the culprit byte jumps out.

> 🔵 **Technical detail** — A minimal diff in Python:
> ```python
> a = open("before.bin","rb").read()
> b = open("after.bin","rb").read()
> for i in range(len(a)):
>     if a[i] != b[i]:
>         print(f"0x{i:X}: {a[i]:02X} -> {b[i]:02X}")
> ```
> Tip: if too many bytes change (the clock advances, for example), **narrow the window** to the save zone (`0xEFE000`–`0xF00000`) and ignore the date fields. The **language (`+0x7B`)**, **points (`+0xB4`)**, **date (`+0x1C`…)**, **chara_id (`+0x108`)** fields were all confirmed this way: you change the value in the game, you diff, you link the offset to its meaning.

### 22.3 How we crack a checksum
Three checksums, three different methods — it's instructive.

**(a) The ARC2 checksum: recognizing a simple sum.**
The archive structure came from GMMan's public research (the checksum field is at `+0x04`). What remained was to find *how* it's computed. We tested the simplest hypothesis — **a sum of all bytes** — on an intact archive: the computed total landed exactly on the stored value. Hypothesis confirmed, and **reproducible** on other archives. *Lesson: always test the dumbest explanation first (sum), before assuming something complicated (CRC).*

**(b) The version block checksum: the complete mathematical investigation.**
This is the textbook case. The approach, step by step:
1. **Compare the binaries of the 4 biomes** (Earth/Water/Sky/Jade), block of 4 KB by 4 KB. Striking result: between Earth, Water and Sky, **a single block differs** (`0xD49000`). *Minimal differences reveal what commands behavior.*
2. **Recognize a pattern**: at `0xD49FF8` and `0xD49FFC`, two values are **complementary** (`V` and `~V`, such that `V XOR ~V = 0xFFFFFFFF`). Almost certain sign of a checksum + its complement.
3. **Mathematical hypothesis**: by changing **one** byte of the firmware, we observe that `V` **decreases by 1**. So it's not a CRC (which would "explode"), but an **additive sum**. We then test: *"does `V + sum_of_bytes(of a range) = a constant?"* We try several ranges → **HIT**: `V + sum(0 .. 0xD49FF8) = 0xFFFFFC03`.
4. **Validate on several data points**: the formula holds across the 4 firmwares.
5. **Forge a proof**: we transform a Water firmware into a Sky firmware **byte by byte** → the console accepts it. Definitive proof.

**(c) The save checksum: searching for CRC parameters ("RevEng").**
This one **is** a real CRC, and the diff/sum aren't enough. The standard method to crack an unknown CRC:
1. **gather several known pairs** (a data block + the checksum stored next to it) — here, several valid save banks;
2. **search for the CRC parameters** (width, polynomial, initial value, input/output reflection, final XOR) that **reproduce** these pairs. There are dedicated tools (the famous **CRC RevEng**) that automatically sweep the parameter space.
3. Result: a **CRC-16 "Rocksoft"** (reflected polynomial `0xA001`, init `0x0000`, input/output reflected, no final XOR), computed over `[save+0x04 : save+0x1000]`, exactly reproduces the value stored at `save+0x00`. *Confirmed by recomputing the same value already present in intact saves.*

> 🟢 **For everyone** — Remember the hierarchy: **(1)** try a **sum** (the most common); **(2)** if the value has a **complement** next to it, it's definitely a checksum; **(3)** if the sum doesn't work and it "explodes" when you change a byte, it's a **CRC** → RevEng tool with known pairs.

### 22.4 How we understood the encryption
The PRAM code (`0x1000`-`0x10FFF`) is encrypted. We didn't "crack" it blindly: the Sonix scheme was **already publicly documented** by GMMan (repo `snc73xx-firmware-encryption`). The real work was to **verify** that we applied it correctly, thanks to two **oracles** (known truths that say "it's good"):
- the **load table** (at the start of the flash) contains `CRC_CHK_SUM = 0x3745D94A`, which is the **CRC32 of the code once decrypted**. If our decryption gives this CRC32, it's a win;
- the decrypted code must begin with a **valid ARM vector table** (a plausible stack pointer `SP` and a Reset vector in Thumb). We obtained `SP = 0x1801EE38` — consistent.

> 🟢 **For everyone** — An "oracle" is a known-in-advance answer that tells you whether you're right. Here: "the CRC32 of the result must equal `0x3745D94A`". As long as you don't land on it, your decryption is wrong; when you land on it, you know it's right. We also did the **reverse path** (re-encrypting) and verified that we **landed back on the original file** bit for bit — the ultimate proof that we master both directions.

### 22.5 How we found the sprites and the `+0x04` trap
1. **Visual inspection with tamasprite**: by scrolling through the sprites by index, we see that for an adult, **6 consecutive images** form a body, eyes, mouth, then the same in small. Hence the rule "one character = 6 sprites".
2. **The trap**: it was tempting to believe that the `+0x04` field of the character table (577 for HORHOTCHI) **was** the sprite index. We tested → **failure**: copying `sprite[586]` gave the **eyes of BATATCHI**, not a body. So the `+0x04` value is **not** the displayed index.
3. **The right track, validated on hardware**: copying the **6 sprites 531-536** (spotted by tamasprite) into the slots of another adult → **correct body** on the console. It was the **hardware test** that decided between the two hypotheses.

> 🟢 **For everyone** — Moral: **a field that looks like an index isn't necessarily one.** We only trust what is **confirmed** (here by tamasprite + flashing on the console).

### 22.6 How we located the eye/mouth positions (`0x167C70`)
This is the most recent investigation, in several chained deductions:
1. **Symptom**: after copying the sprites, **the bodies are good but the eyes/mouth remain badly placed**. Logical conclusion: the **position** is not in the sprite, it's **elsewhere**.
2. **Community clue**: GMMan's documentation on ghosts mentions **"composite definitions"** — literally *"where to place the sprites when drawing the character"* — of size `0x16` bytes, stored "as instances".
3. **Targeted search in the dump**: while exploring the *Data* file of the archive, we land at **`0x167C70`** on a **readable** sequence of `sprite_id + ox + oy` where the `oy` are `-33`, `-32`… — exactly the expected vertical positions. (These bytes are visible in the dump; it's only **Ghidra** that didn't see them, because this zone is not loaded into the code.)
4. **Structural confirmation**: each adult has **exactly 112 layers**, in the **same order** for all — too regular to be a coincidence. And the `oy` **vary slightly from one frame to another** (`-33`, `-35`, `-37`…), which corresponds to the **animation frames** (blinking, looking up/down).
5. **Validation by computation**: we verified that applying the **delta model** with offsets at 0 produces a firmware **identical byte for byte** to the "full copy of HORHOTCHI" method (same ARC2 checksum, `0x32B91617`). Two independent paths giving the same result = proof of consistency.

> 🟢 **For everyone** — The chain of reasoning: *"the bodies are good but not the eyes"* ⇒ *"the position is elsewhere"* ⇒ *"the docs mention composite definitions"* ⇒ *"let's look for a position table"* ⇒ *"here it is, and its regularity (112 layers, animation variations) confirms it's really it"*. Each link follows from the previous one.

### 22.7 How we deduced how ghosts work
1. **The signature**: while scanning the dump, we notice blocks where the first two words **cancel out** (`w0 + w4 = 0`). It's the signature of a ghost checksum — it serves to **spot them without a list**.
2. **The scan beat the hard-coded addresses**: by replacing fixed addresses with a dynamic scan, we **discovered 2 ghosts** that the old method missed. *Lesson: a signature scan is more robust than a list of frozen addresses.*
3. **The "add/remove" deduction** (recent): to add a character, we needed to know how the console counts its ghosts. We verified that empty slots are **all `0xFF`**, and above all that there is **no counter** in the save — proof: a dump with 7 ghosts has the same value (`0`) at the suspected spot as a dump… that doesn't depend on it. **So the console probably enumerates by scanning.** We then **simulated** an addition (the scan goes from 16 to 17 ghosts) and a removal (back to 16). *Remains to be confirmed on hardware* — that's the next check.

> 🟢 **For everyone** — To prove "there's no ghost counter", we compared several consoles: if a number somewhere **doesn't follow** the real number of ghosts, then that number isn't the counter. It's reasoning by **elimination**.

### 22.8 The decisive role of hardware validation
> ⭐ **The most telling example.** The documentation claimed that the version block checksum (`0xD49FF8`) was a **startup safeguard** ("firmware rejected if invalid"). But by looking at a **real dump** of the console, we found that **its `0xD49FF8` checksum was invalid… and the console worked perfectly.** Then an edited firmware, also with this invalid checksum, **booted** on the hardware. Conclusion: **this checksum is NOT verified at boot.** The documentation was wrong on this point.

> 🟢 **For everyone** — This is THE central lesson: **the hardware always has the last word.** A seductive hypothesis ("this checksum must be verified") can be false. We only knew it by **looking at reality** rather than trusting the text. That's why, throughout this guide, we insist on **testing on the console**, and preferably **on a single case first**.

### 22.9 The detective's tools (and when each is useful)
| Tool | What it's for | When to use it |
|---|---|---|
| **Dump diff** | spot which byte changes after an action | locate a save field (language, points, hunger…) |
| **Hex editor** (HxD/ImHex) | "see" the bytes, spot patterns (complement, headers) | manual inspection, structure recognition |
| **tamasprite** | display/replace sprites by index | understand the appearance, do the 6-sprite mapping |
| **CRC RevEng** | recover a CRC's parameters from known pairs | crack a checksum that isn't a simple sum |
| **Python** | test a checksum/structure hypothesis en masse | validate a formula across several files, forge a proof |
| **Ghidra** | read the engine code (disassembly) | start from a **text string** and trace the code |
| **SWD** (live debug) | read/write memory live, single-step | the puzzles static analysis doesn't solve (computed-addressing tables) |
| **The hardware** | the final arbiter | **always**, to confirm a hypothesis |
| **Public research** (GMMan) | the starting base (formats, encryption, pins) | before reinventing the wheel — we start from what exists |

> 🟢 **For everyone — why Ghidra didn't solve everything.** Ghidra reads the **code**, but the **data tables** (like the positions at `0x167C70`) are stored **too far** in the flash to be loaded with the code, and the program accesses them by **computation** (and not by a hard-coded address). As a result, Ghidra doesn't "see" the link. This is exactly the kind of case where **dump diffing** and **live debug (SWD)** are far more efficient than code analysis.

### 22.10 The transferable lessons (to take everywhere)
1. **Diff first**: the minimal differences between two files reveal what matters.
2. **Simplest hypothesis first**: a **sum** before a CRC; a literal meaning before a complicated indirection.
3. **A complement next to a value = a checksum** almost for sure.
4. **Forge a proof**: if your formula lets you transform a file into another **valid** one, you're right.
5. **Validate on several data points**, not just one.
6. **The hardware has the last word**: the docs can be wrong (cf. `0xD49FF8`).
7. **Test risky changes on ONE case** before generalizing.
8. **A field that looks like an index isn't necessarily one** (the `+0x04` trap).
9. **A signature scan** is more robust than a list of frozen addresses.
10. **Start from existing public research**, then verify it yourself.

> 🟢 **In one sentence** — This entire guide was built by **observing, hypothesizing, testing, and believing the hardware rather than certainties**. It's a method you can apply to any device, not just the Tamagotchi.

---

> **End of guide.** You now have the complete chain: *read the chip → understand the memory map → modify the right zone → recompute the right checksum → rewrite the chip → verify on the console.* Everything else is just variation on this theme. Happy hacking! 🎮
