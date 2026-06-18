> **📌 Note de recentrage — résumé produit par IA**
>
> Ce document rassemble en un seul endroit tout ce qui a été découvert, déduit et validé jusqu'ici sur la Tamagotchi Paradise (carte mémoire, checksums, sprites, ghosts, biomes, save, langue, outils, et la démarche d'enquête). Il me sert de point de référence unique pour continuer le travail de reverse engineering.
>
> Il existe en **deux versions dans ce fichier** : d'abord la version **française** (ci-dessous), puis une **traduction anglaise intégrale** dans une section dédiée à la fin, pour documenter aussi en anglais.

---

# 🛠️ Le Guide Complet : Hacker la Tamagotchi Paradise de A à Z

> **Pour qui ?** Ce guide est écrit pour deux personnes à la fois :
> - **Le débutant total** 🟢 — qui n'a jamais ouvert un éditeur hexadécimal de sa vie. Chaque mot compliqué est expliqué la première fois qu'il apparaît.
> - **Le développeur** 🔵 — qui veut les adresses exactes, les formules, et le code prêt à copier.
>
> Lis-le dans l'ordre la première fois. Ensuite, sers-toi des tables de référence (§19) et du glossaire (§20) comme d'un dictionnaire.
>
> **Règle d'or absolue, à lire avant tout le reste :** tu travailles **toujours sur une COPIE** d'un dump récent de ta propre console. Tu ne modifies jamais l'original. Si quelque chose tourne mal, tu re-flashes l'original et tout revient comme avant. Avec ça, **tu ne peux pas casser ta console de façon permanente** tant que la puce elle-même répond.

---

## 📑 Sommaire

0. [Comment lire ce guide](#0)
1. [C'est quoi, au juste ?](#1)
2. [Les notions de base absolues](#2) — bit, octet, hexadécimal, adresse, little-endian
3. [Le matériel et le branchement](#3)
4. [Étape 1 — Lire la puce (faire un « dump »)](#4)
5. [Étape 2 — Ce qu'il y a dans le fichier .bin](#5) — la carte mémoire
6. [Le chiffrement (et pourquoi tu n'en as presque jamais besoin)](#6)
7. [Les checksums — le cœur du hacking](#7)
8. [Étape 3 — Modifier la sauvegarde (save)](#8)
9. [Les personnages : identité, stades, biome](#9)
10. [Les sprites et l'apparence](#10)
11. [Les positions yeux/bouche (animations)](#11)
12. [Les ghosts (les persos « fantômes »)](#12)
13. [Le système de biome](#13)
14. [Les codes d'unlock](#14)
15. [Étape 4 — Réécrire la puce (« flasher »)](#15)
16. [Outils avancés : Ghidra et SWD](#16)
17. [Recettes pratiques (« je veux faire X »)](#17)
18. [La boîte à outils Python](#18)
19. [Tables de référence](#19)
20. [Glossaire pour débutant total](#20)
21. [Dépannage et sécurité](#21)
22. [Comment tout ça a été découvert](#22) — la démarche du détective

---

<a name="0"></a>
## 0. Comment lire ce guide

Tout au long du document, tu verras deux types d'encadrés :

> 🟢 **Pour tous** — l'explication simple, en français courant, sans supposer que tu connais quoi que ce soit.

> 🔵 **Détail technique** — les valeurs exactes, adresses, formules et code. Si tu débutes, tu peux sauter ces encadrés au premier passage et y revenir plus tard.

Les blocs de code (sur fond gris) sont en **Python** la plupart du temps. Python est un langage de programmation très lisible ; même sans le connaître, tu comprendras souvent ce qu'il fait en lisant les commentaires (les lignes qui commencent par `#`).

---

<a name="1"></a>
## 1. C'est quoi, au juste ?

### La console
La **Tamagotchi Paradise** est un petit animal de compagnie virtuel sorti récemment. À l'intérieur, il y a :
- un **microcontrôleur** (le « cerveau ») : un **Sonix SNC7330**. C'est une puce de la famille **ARM Cortex-M** (le même genre de cœur que dans des milliards d'objets connectés). Il exécute des instructions au format **Thumb** (une variante compacte du langage machine ARM) ;
- une **puce de mémoire flash** : une **MX25L12835F**. C'est là que tout est stocké : le programme, les images, ta sauvegarde. Elle fait **16 mégaoctets** (on verra plus bas ce que ça veut dire exactement).

> 🟢 **Pour tous** — Imagine la console comme un mini-ordinateur. Le « cerveau » (SNC7330) lit ses instructions et ses images depuis un « disque dur » (la flash MX25L12835F). Hacker la console = **lire ce disque dur, le modifier, puis le réécrire**.

### Ce que « hacker » veut dire ici
On ne « pirate » rien d'illégal : c'est **TON** jouet, et on fait du **reverse engineering** — c'est-à-dire qu'on examine comment il fonctionne pour le **modifier à notre goût**. Concrètement, tu pourras :
- changer la **langue** de la console,
- renommer ta planète et tes objets,
- te donner des **Gotchi Points**, changer la **date**, la **faim**, le **bonheur**,
- **changer l'apparence** des personnages (leur donner le corps/les yeux/la bouche d'un autre),
- **ajouter ou supprimer** des persos « fantômes » (ghosts),
- changer le **biome** (Ciel, Terre, Eau, Jade).

### Le vocabulaire de départ
- **Firmware** : le logiciel embarqué dans la console (le programme + les données). C'est l'ensemble de ce qu'il y a sur la flash.
- **Dump** : une **copie exacte** du contenu de la flash, enregistrée dans un fichier sur ton PC (un fichier `.bin`). « Faire un dump » = lire la puce et sauvegarder son contenu.
- **Flasher** : l'opération inverse — **écrire** un fichier `.bin` sur la puce.
- **Patcher** : modifier le fichier `.bin` (sur ton PC) avant de le re-flasher. Un « patch » est une modification.

---

<a name="2"></a>
## 2. Les notions de base absolues

Cette section est **fondamentale** si tu débutes. Prends 10 minutes ; après, tout le reste coule de source.

### 2.1 Bit et octet
- Un **bit** est la plus petite information possible : `0` ou `1`.
- Un **octet** (en anglais *byte*) = **8 bits** groupés. Un octet peut représenter un nombre de **0 à 255** (256 valeurs possibles).

Ta flash de 16 mégaoctets contient donc **16 millions d'octets** environ — chacun étant un petit nombre entre 0 et 255.

### 2.2 L'hexadécimal (la base 16)
Les humains comptent en base 10 (chiffres 0 à 9). Les informaticiens écrivent souvent les octets en **hexadécimal** (base 16) parce que c'est plus pratique. En hexa, les « chiffres » vont de 0 à 15, mais comme on n'a pas de symbole pour 10–15, on utilise les lettres **A à F** :

| Décimal | 0 | 1 | … | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|
| Hexa | 0 | 1 | … | 9 | A | B | C | D | E | F |

- On préfixe l'hexa par **`0x`** pour le distinguer. Ainsi `0x0A` = 10, `0xFF` = 255, `0x10` = 16.
- **Un octet s'écrit avec exactement 2 chiffres hexa** (de `0x00` à `0xFF`). C'est pour ça qu'on voit des suites comme `13 02 03 06` : ce sont 4 octets.

> 🟢 **Pour tous** — Retiens juste : `0xFF` = 255 = « octet tout à 1 » = la valeur maximale d'un octet. Une zone « pleine de FF » est une zone **vierge** (effacée).

### 2.3 Adresse et offset
La flash, c'est une longue rangée de 16 millions de casiers, numérotés à partir de 0. Le numéro d'un casier s'appelle son **adresse** (ou **offset**, c'est synonyme ici). On l'écrit en hexa.

- L'adresse `0x0` = le tout premier octet.
- L'adresse `0xEFE000` = l'octet numéro 15 720 448 (c'est là que commence ta sauvegarde, on le verra).

Quand on dit « le champ langue est à **save+0x7B** », ça veut dire : « pars du début de la save, avance de `0x7B` (= 123) octets, et lis là ».

### 2.4 Lire un nombre sur plusieurs octets : u8, u16, u32
Un seul octet ne va que jusqu'à 255. Pour stocker de plus grands nombres, on en combine plusieurs :
- **u8** = *unsigned 8-bit* = 1 octet (0 à 255).
- **u16** = *unsigned 16-bit* = 2 octets (0 à 65 535).
- **u32** = *unsigned 32-bit* = 4 octets (0 à ~4,2 milliards).

Le **`s`** au lieu du **`u`** (ex. **s16**) veut dire **signé** : le nombre peut être négatif (utile pour des positions à l'écran, ex. `oy = -33`).

### 2.5 Little-endian (TRÈS important)
Quand un nombre tient sur plusieurs octets, dans quel ordre les range-t-on ? Le SNC7330 utilise le **little-endian** : **l'octet le moins important est écrit en premier**.

Exemple concret. Le nombre **`0x1234`** (u16) est stocké en mémoire comme : `34 12` (l'octet de poids faible `0x34` d'abord, puis `0x12`).

Autre exemple, un u32 : **`0x3745D94A`** est stocké comme `4A D9 45 37`.

> 🟢 **Pour tous** — Si tu vois `4A D9 45 37` dans un éditeur et que tu veux le « vrai » nombre, tu **inverses l'ordre des octets** : `37 45 D9 4A` → `0x3745D94A`. C'est la cause d'erreur n°1 des débutants. Tous les outils de ce guide gèrent ça pour toi, mais il faut le savoir pour lire un dump à la main.

> 🔵 **Détail technique** — En Python, le module `struct` lit le little-endian avec le préfixe `<` :
> ```python
> import struct
> def u16(b, o): return struct.unpack_from("<H", b, o)[0]   # H = u16
> def u32(b, o): return struct.unpack_from("<I", b, o)[0]   # I = u32
> def s16(b, o): return struct.unpack_from("<h", b, o)[0]   # h = s16 (signé)
> # b = le contenu du fichier (bytes), o = l'offset où lire
> ```

### 2.6 Qu'est-ce qu'un éditeur hexadécimal ?
C'est un logiciel qui affiche un fichier **octet par octet** en hexa, dans une grille. Chaque ligne montre une adresse, puis 16 octets, puis leur version « texte ». C'est l'outil de base pour regarder un dump.
- Exemples gratuits : **HxD** (Windows, très simple), **ImHex** (multi-plateforme, plus avancé), **010 Editor** (payant, puissant).
- Dans ce guide, on fera la plupart des modifications avec des **petits programmes Python** ou des **éditeurs web** déjà préparés — plus sûrs et plus rapides qu'à la main. Mais savoir ouvrir un dump dans HxD pour « voir » est précieux.

### 2.7 Qu'est-ce qu'un checksum ? (aperçu)
Un **checksum** (« somme de contrôle ») est un petit nombre calculé à partir d'un bloc de données, qui sert à **vérifier que les données ne sont pas corrompues**. Si tu modifies un octet sans recalculer le checksum, la console peut détecter l'incohérence et **refuser** les données.

> 🟢 **Pour tous** — Pense au checksum comme au « total » au bas d'un ticket de caisse. Si tu changes un prix sans changer le total, ça ne colle plus. Quand on modifie le firmware, il faut souvent **recalculer le total**. C'est tout le sujet de la §7, et c'est le secret du hacking propre.

---

<a name="3"></a>
## 3. Le matériel et le branchement

### 3.1 Ce dont tu as besoin
1. **Un programmateur SPI.** C'est le boîtier qui parle à la puce flash. Tu utilises un **CH347** (excellent, rapide). Une alternative connue est le **CH341A** (moins cher, plus lent, 3,3 V impératif).
2. **Le logiciel Asprogrammer** (de *nofeletru*, aussi appelé *UsbAsp-flash*). C'est l'interface sur ton PC qui pilote le CH347.
3. **De quoi te connecter à la puce.** Deux cas :
   - la puce est sur un support ou tu l'as dessoudée → un **adaptateur SOIC8/clip** ;
   - tu veux éviter de souder → une **pince SOIC « clip »** qui se pince sur la puce, ou des **pogo pins** (petites pointes à ressort) sur les **test pads** de la carte (voir §19.5).

> 🟢 **Pour tous** — Le programmateur est un traducteur entre ton PC (USB) et la puce (protocole SPI). Asprogrammer est l'application qui lui dit « lis » ou « écris ». La pince/les pogo pins sont juste le moyen physique de toucher les bonnes pattes de la puce.

### 3.2 La puce : MX25L12835F
- **Capacité : 128 Mbit = 16 Mo = `0x1000000` octets.** (128 Mbit ÷ 8 = 16 Mo.)
- **Type : flash SPI.** SPI = un protocole de communication série simple à 4 fils.
- **Organisation interne :** la mémoire est lue octet par octet, mais **l'écriture se fait par pages de 256 octets** et **l'effacement par secteurs de 4 Ko** (0x1000 octets). On ne peut pas réécrire un octet « par-dessus » un autre : il faut **effacer** d'abord (effacer met tout à `0xFF`), puis **programmer**.
- Variantes équivalentes que tu peux croiser : **MX25L12833F**, **KH25L12833FM2I-10G** (Macronix). Même taille, même comportement.

> 🔵 **Détail technique — commandes SPI du MX25L** (utiles si tu écris un script `.pas`, §15) :
> | Commande | Octet | Rôle |
> |---|---|---|
> | READ | `0x03` | lire des données |
> | Page Program | `0x02` | écrire une page (256 o) |
> | Write Enable (WREN) | `0x06` | autoriser l'écriture (obligatoire avant chaque écriture/effacement) |
> | Read Status Register | `0x05` | lire l'état ; **bit 0 = WIP** (Write In Progress) |
> | Sector Erase 4K | `0x20` | effacer un secteur de 4 Ko |
> | Block Erase 64K | `0xD8` | effacer un bloc de 64 Ko |
> | Chip Erase | `0xC7` | effacer **toute** la puce |
> | Write Status Register | `0x01` | écrire le registre d'état (déverrouillage) |

### 3.3 Précautions physiques
- **Toujours 3,3 V**, jamais 5 V (tu grillerais la puce). Les CH347/CH341A ont un sélecteur ou une version 3,3 V.
- Bien aligner la **patte 1** de la puce avec la patte 1 de la pince (un point ou un repère marque la patte 1).
- Si la console est allumée pendant que tu te connectes en pince, il peut y avoir des conflits ; idéalement la puce est lue hors tension du SNC7330 (ou tu maintiens la console en reset — voir test pads RST §19.5).

---

<a name="4"></a>
## 4. Étape 1 — Lire la puce (faire un « dump »)

C'est la toute première manipulation, et la plus importante : **récupérer une copie de ta console**.

### 4.1 La procédure dans Asprogrammer
1. Branche le CH347 en USB, connecte la pince/pogo pins sur la puce.
2. Ouvre **Asprogrammer**.
3. En haut, choisis le **type de programmateur** : `CH347`.
4. Clique sur **Detect** (ou l'icône de détection de puce). Asprogrammer doit reconnaître une **MX25L12835F** (ou équivalent). Si elle n'est pas auto-détectée, sélectionne-la manuellement dans la liste Macronix (taille 128 Mbit).
5. Clique sur **Read IC** (lire la puce). La lecture des 16 Mo prend de quelques secondes à une minute selon le programmateur.
6. **File → Save** : enregistre le résultat en `.bin`. **Nomme-le clairement et datant**, par exemple `ma_console_ciel_2026-06-17.bin`.

> 🟢 **Pour tous** — « Read IC » copie la puce vers la fenêtre d'Asprogrammer (un éditeur hexa intégré). « Save » écrit cette copie dans un fichier sur ton PC. Ce fichier `.bin` **EST** ton dump.

### 4.2 La règle d'or (encore)
- **Garde ce dump original intact, à part, pour toujours.** C'est ton filet de sécurité : si une modification rate, tu re-flashes ce fichier et la console revient exactement à l'état d'avant.
- **Tu travailles toujours sur une COPIE** de ce fichier, jamais sur l'original.
- Quand tu fais une modification importante (changer le perso actif, le biome…), refais d'abord un dump frais : il contient ta progression la plus récente.

### 4.3 Vérifier que le dump est bon
Un dump valide fait **exactement 16 777 216 octets** (16 Mo). Si la taille est différente, la lecture a échoué (mauvais contact de la pince le plus souvent) → recommence.

> 🔵 **Détail technique** — Vérification rapide en Python :
> ```python
> data = open("ma_console_ciel_2026-06-17.bin", "rb").read()
> print(len(data), "octets")          # doit afficher 16777216
> print(hex(len(data)))               # doit afficher 0x1000000
> # Petit test de cohérence : le tout début contient la "load table"
> print(data[0:8])                    # doit contenir b"SONIXDEV"
> ```
> Si `data[0:8]` vaut bien `b'SONIXDEV'`, ton dump commence correctement.

---

<a name="5"></a>
## 5. Étape 2 — Ce qu'il y a dans le fichier .bin (la carte mémoire)

Le dump de 16 Mo n'est pas un bloc informe : il est **découpé en zones**, chacune avec un rôle. Voici la carte complète. Ne la mémorise pas — reviens-y comme à un plan de métro.

### 5.1 La carte mémoire complète

| Plage d'adresses | Taille | Zone | À quoi ça sert |
|---|---|---|---|
| `0x0` – `0xFFF` | 4 Ko | **En-tête firmware** | informations de démarrage (bootrom) |
| `0x1000` – `0x10FFF` | 64 Ko | **Firmware PRAM** | **code chiffré** (AES-256), §6 |
| `0x11000` – `0x10FFFF` | ~1 Mo | **Code XIP** | le programme principal, **en clair** |
| `0x110000` – `0x110FFF` | 4 Ko | **DPD firmware** | données persistantes du bootrom |
| `0x111000` – `0x8286C3` | ~8 Mo | **Assets** | images, textes, données de jeu (archive « ARC2 ») |
| `0x8286C4` – `0xD48FFF` | ~5 Mo | **Inutilisé** | rempli de `0xFF` |
| `0xD49000` – `0xD49FFF` | 4 Ko | **Bloc Version** ⭐ | le **flag biome** + checksum, §13 |
| `0xD4A000` – `0xD4DFFF` | 16 Ko | **DL items staging** | objets téléchargés en attente |
| `0xD4E000` – `0xDEDFFF` | 640 Ko | **DL items stockés** | objets « lab » (40 slots de `0x4000`) |
| `0xDEE000` – `0xE45FFF` | 376 Ko | **Ghost data** ⭐ | les persos « fantômes », §12 |
| `0xE46000` – `0xE65FFF` | 128 Ko | **Ghost réception** | ghosts reçus d'autres consoles |
| `0xE66000` – `0xE85FFF` | 128 Ko | **Ghost export** | données à partager |
| `0xE86000` – `0xEFDFFF` | 472 Ko | **Screenshots amis** | captures de la communauté |
| `0xEFE000` – `0xEFEFFF` | 4 Ko | **Save principale** ⭐ | **ta sauvegarde**, §8 |
| `0xEFF000` – `0xEFFFFF` | 4 Ko | **Save backup** | copie de secours de la save |
| `0xF00000` – `0xFFFFFF` | 1 Mo | **Réservé** | |

Les ⭐ sont les zones que tu modifieras le plus souvent.

> 🟢 **Pour tous** — Trois grandes familles à retenir :
> 1. **Le programme** (`0x1000` à ~`0x110000`) : le « moteur » du jeu. On y touche rarement (et la partie `0x1000`-`0x10FFF` est chiffrée).
> 2. **Les assets** (`0x111000` à ~`0x828000`) : toutes les **images** et **textes**. C'est là qu'on change les apparences et les noms.
> 3. **Les données utilisateur** (à partir de `0xD49000`) : **biome, ghosts, et ta sauvegarde**. C'est là qu'on change ta progression.

### 5.2 Les archives « ARC2 »
Les assets sont rangés dans un format d'archive maison appelé **ARC2** (un peu comme un fichier `.zip`, mais simple). Une archive ARC2 peut **en contenir d'autres** (comme des dossiers imbriqués).

> 🔵 **Détail technique — structure d'une archive ARC2**
> - **En-tête, 16 octets :**
>   - `+0x00` : signature `"ARC2"` (en hexa `0x32435241`)
>   - `+0x04` : **checksum** (somme des octets de `+0x08` jusqu'à la fin) — voir §7
>   - `+0x08` : `length` = (taille totale de l'archive − 16)
>   - `+0x0C` : `num_files` = nombre de fichiers dans l'archive
> - **Puis une table d'entrées, 16 octets chacune :**
>   - `+0x00` : flags (0 = pas de compression)
>   - `+0x04` : `offset` (relatif au début de l'archive)
>   - `+0x08` : `compressed_length`
>   - `+0x0C` : `uncompressed_length`
> - L'archive **principale** est à `0x111000`. Elle contient 3 fichiers : **Data** (données de jeu), **Sprites** (images), **Strings** (textes, qui est elle-même une archive de **9 tables de langues**).
>
> ```python
> ARC2 = 0x32435241
> def arc2_files(b, base):
>     assert u32(b, base) == ARC2, "pas une archive ARC2"
>     n = u32(b, base+12); out = []
>     for i in range(n):
>         e = base + 16 + i*16
>         out.append({"flags": u32(b,e), "offset": base+u32(b,e+4),
>                     "clen": u32(b,e+8), "ulen": u32(b,e+12)})
>     return out
> ```

Tu n'as pas besoin de comprendre ça en détail pour utiliser les outils tout faits. Mais c'est utile de savoir que « modifier une image » = « modifier un octet **dans** une archive », et que ça impliquera de **recalculer le checksum de l'archive** (§7).

---

<a name="6"></a>
## 6. Le chiffrement (et pourquoi tu n'en as presque jamais besoin)

### 6.1 La bonne nouvelle d'abord
Sur les 16 Mo de la flash, **une seule petite zone est chiffrée** : le **Firmware PRAM** (`0x1000` à `0x10FFF`, soit 64 Ko). **Tout le reste est en clair** (lisible directement) : le code XIP, les assets (images, textes), les ghosts, et **ta sauvegarde**.

> 🟢 **Pour tous** — « Chiffré » veut dire brouillé avec une clé secrète : illisible sans la clé. « En clair » veut dire lisible tel quel. Comme **99 % de ce que tu vas modifier est en clair** (images, textes, save, biome, ghosts), **tu n'auras presque jamais à toucher au chiffrement.** Tu peux survoler cette section et y revenir si un jour tu veux modifier le code du moteur lui-même.

### 6.2 Ce que c'est, pour les curieux
Le chiffrement utilise **AES-256 en mode CBC**, selon un schéma propre à Sonix (la marque du microcontrôleur). Les détails ont été entièrement compris et vérifiés.

> 🔵 **Détail technique — schéma de chiffrement Sonix V3 (SNC7330)**
> - **Load table** au tout début du flash (`0x0`, 512 octets). Champs observés : `MARK="SONIXDEV"`, `TABLE_VERSION=0x5A5A0033` (V3), `LOAD_CFG=0x13` (chiffré + vérif CRC), `ADDR_USERCODE=0x60001000`, `SIZE_USERCODE=0x10000`, `CRC_CHK_SUM=0x3745D94A` (le CRC32 du code **déchiffré**), et **`AES_KEY` (32 octets) entièrement à ZÉRO** à l'offset `0x28` (valeur par défaut du SNC7330).
> - **Device key = `0x5aaf34fb`** (un fusible interne de 32 bits). C'est la **seule vraie clé secrète**. Elle sert uniquement à dériver le « vecteur d'initialisation » (IV) du CBC.
> - **Le périphérique AES travaille en ordre d'octets INVERSÉ** pour les clés/IV/blocs. L'algorithme :
>   1. *IV material* = `AES_KEY[0:16]` XOR device_key (mot par mot). Clé nulle ⇒ `[DK, DK, DK, DK]`.
>   2. *IV dérivée* = AES-ECB-encrypt(IV material, clé = `AES_KEY[16:32]`), en sémantique inversée.
>   3. *CBC (V3)* : par bloc, on déchiffre puis on XOR avec l'IV ; le bloc chiffré devient l'IV suivant ; **l'IV est remise à l'IV dérivée tous les `0x1000` octets**.
> - **Vérification :** le CRC32 du code déchiffré vaut bien `0x3745D94A`, et la « vector table » ARM est valide (SP = `0x1801EE38`, Reset = `0x000002F5` en Thumb). Le code PRAM s'exécute dans la région `0x18000000` (SRAM).
> - **Pipeline déchiffrer → patcher → re-chiffrer vérifié à 100 %** (re-chiffrer reproduit l'original bit pour bit). Référence : `github.com/GMMan/snc73xx-firmware-encryption` et `sonix-boot-decrypter`.

### 6.3 La leçon pratique
> ⚠️ **À retenir absolument :** pour éditer des **assets**, du **XIP**, la **save**, les **ghosts** ou le **biome**, tu n'as **JAMAIS** besoin de déchiffrer/re-chiffrer quoi que ce soit. Le chiffrement ne concerne que les 64 Ko du PRAM. C'est confirmé empiriquement sur les vraies consoles.

---

<a name="7"></a>
## 7. Les checksums — le cœur du hacking

C'est **la** section à comprendre. Une fois que tu maîtrises les checksums, modifier la console devient mécanique.

### 7.1 Le principe (rappel approfondi)
Quand le firmware range un bloc de données important, il calcule un **petit nombre résumé** (le checksum) à partir de ce bloc, et le range juste à côté. Plus tard, il **recalcule** et **compare** : si ça ne correspond pas, les données sont considérées corrompues.

> 🟢 **Pour tous** — Donc si tu modifies un octet « à la main » sans recalculer le checksum, deux choses peuvent arriver :
> - soit la console **rejette** la modification (pour la save, par exemple, elle recrée une partie neuve),
> - soit, si ce checksum-là n'est **pas vérifié au démarrage** (c'est le cas de certains), ça passe quand même.
>
> Le secret du hacking propre : **après chaque modification, recalcule le bon checksum.** Tous les outils de ce guide le font automatiquement. Cette section t'explique lesquels existent et comment ils se calculent, pour que tu comprennes ce qui se passe.

### 7.2 Les 7 checksums de la console

Voici le tableau de synthèse. Chaque ligne est détaillée juste après.

| # | Quoi | Où est-il stocké | Comment on le calcule | Statut |
|---|---|---|---|---|
| 1 | **ARC2** (archives) | `+0x04` de l'archive | somme des **octets** de `+0x08` à la fin | ✅ cracké |
| 2 | **Ghost** | `+0x00` et `+0x04` du ghost | somme des **mots 32 bits** ; `w0 + w4 = 0` | ✅ cracké |
| 3 | **Bloc version** | `0xD49FF8` et `0xD49FFC` | `V = 0xFFFFFC03 − (somme des octets de 0 à 0xD49FF8)` | ✅ cracké (non vérifié au boot) |
| 4 | **Code PRAM (CRC32)** | load table `+0x24` | CRC32 standard du code déchiffré | ✅ cracké |
| 5 | **Save** | `0xEFE000`, octets 0-3 | **CRC-16 Rocksoft** sur `[+0x04 : +0x1000]` | ✅ **cracké** |
| 6 | **Screenshot** | `+0x00` / `+0x04` du sprite | somme des mots 32 bits ; `somme + complément = 0xFFFFFFFF` | ✅ cracké |
| 7 | **Chunk TCP** | en-tête du paquet réseau | CRC-16 Rocksoft (poly `0x8005`) | ✅ cracké |

> 🟢 **Pour tous** — En pratique, pour 95 % de tes hacks, tu n'utiliseras que **trois** d'entre eux : le **#1 (ARC2)** quand tu touches aux images/textes, le **#2 (ghost)** quand tu touches aux fantômes, et le **#5 (save)** quand tu touches à ta sauvegarde.

### 7.3 Checksum #1 — ARC2 (archives d'images et de textes)
**Quand l'utiliser :** dès que tu modifies un octet **à l'intérieur** d'une archive (sprite, texte, données de jeu).

**Formule :** une simple **somme de tous les octets** depuis `archive + 0x08` jusqu'à la fin de l'archive, rangée en u32 (little-endian) à `archive + 0x04`.

```python
def arc2_fix_checksum(b, base, total_len):   # total_len = taille de l'archive entière
    s = sum(b[base+8 : base+total_len]) & 0xFFFFFFFF
    struct.pack_into("<I", b, base+4, s)
```

> ⚠️ **Règle d'or de l'ordre (leçon durement apprise) :** les archives sont **imbriquées** (l'archive *Strings* est rangée DANS l'archive *Principale*). Si tu modifies un texte, tu dois recalculer le checksum de **Strings d'abord**, PUIS celui de la **Principale**. L'inverse corrompt tout. Règle générale : **toujours l'archive interne avant l'archive externe.**

### 7.4 Checksum #2 — Ghost
**Quand l'utiliser :** quand tu modifies, ajoutes ou supprimes un ghost (§12).

**Formule :** `w0` (à `+0x00`) = somme de tous les **mots de 32 bits** depuis `+0x08` jusqu'à la fin de l'enregistrement. `w4` (à `+0x04`) = l'opposé de `w0`, de sorte que **`w0 + w4 = 0`**. Cette propriété sert aussi de **signature** pour repérer les ghosts dans le dump.

```python
def ghost_fix_checksum(b, base):
    tlen = u32(b, base+0x10C)            # longueur de l'enregistrement
    end  = base + ((tlen + 3) & ~3)      # arrondi au multiple de 4
    s = 0
    for o in range(base+8, end, 4):
        s = (s + u32(b, o)) & 0xFFFFFFFF
    struct.pack_into("<I", b, base+0,  s)
    struct.pack_into("<I", b, base+4, (-s) & 0xFFFFFFFF)
```

### 7.5 Checksum #3 — Bloc version
**Quand l'utiliser :** quand tu changes le **biome** (§13). Par sécurité seulement.

**Formule :** `V = (0xFFFFFC03 − somme_des_octets(de 0 à 0xD49FF8)) modulo 2³²`. On range `V` à `0xD49FF8` et son complément binaire `~V` à `0xD49FFC` (invariant : `V XOR ~V = 0xFFFFFFFF`).

```python
def calc_version_checksum(data):
    MAGIC, END = 0xFFFFFC03, 0xD49FF8
    s = sum(data[:END]) & 0xFFFFFFFF
    V = (MAGIC - s) & 0xFFFFFFFF
    return V, (~V) & 0xFFFFFFFF
```

> ⭐ **Découverte importante :** ce checksum **n'est PAS vérifié au démarrage.** On l'a prouvé : une console réelle dont ce checksum est *invalide* **fonctionne quand même**, et un firmware édité avec ce checksum invalide **a démarré**. Donc pour les éditions d'assets/save/ghosts, **tu n'as pas besoin de le recalculer**. On le recalcule uniquement par prudence lors d'un changement de biome.

### 7.6 Checksum #5 — Save (ta sauvegarde) ✅ cracké
**Quand l'utiliser :** **à chaque fois** que tu modifies ta sauvegarde (langue, points, perso, date, faim, bonheur…). Contrairement au #3, **celui-ci EST vérifié** : une save au mauvais checksum est rejetée (la console recrée une partie neuve).

**Algorithme : CRC-16 « Rocksoft ».** C'est un CRC sur 16 bits avec ces paramètres précis :
- polynôme **`0xA001`** (forme « reflétée » du standard `0x8005`),
- valeur initiale **`0x0000`**,
- entrée et sortie **reflétées** (*refin = refout = true*),
- pas de XOR final (*xorout = 0*).

On le calcule sur les octets **`[save+0x04 : save+0x1000]`** (tout le contenu de la banque save **sauf** les 4 premiers octets qui contiennent justement le checksum). On range le résultat en u16 (little-endian) à **`save+0x00`**, et son complément à **`save+0x02`**.

```python
def crc16_rocksoft(data):
    crc = 0x0000
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if (crc & 1) else (crc >> 1)
    return crc & 0xFFFF

def save_fix_checksum(b, save_base):                 # save_base = 0xEFE000 ou 0xEFF000
    crc = crc16_rocksoft(b[save_base+0x04 : save_base+0x1000])
    struct.pack_into("<H", b, save_base+0x00, crc)
    struct.pack_into("<H", b, save_base+0x02, (~crc) & 0xFFFF)
```

### 7.7 Les checksums #4, #6, #7 (pour mémoire)
- **#4 — CRC32 du code PRAM** (poly `0xEDB88320`, le CRC32 standard) : seulement si tu modifies le code chiffré du moteur. Rare.
- **#6 — Screenshot** : somme des mots 32 bits d'un sprite de capture, avec `somme + complément = 0xFFFFFFFF`. Seulement pour bidouiller les captures d'écran communautaires.
- **#7 — Chunk TCP** : CRC-16 Rocksoft (poly `0x8005`) sur les paquets réseau, utile uniquement pour la communication entre consoles (protocole avancé, hors de ce guide).

---

<a name="8"></a>
## 8. Étape 3 — Modifier la sauvegarde (save)

Voilà la partie la plus gratifiante pour débuter : changer ta progression. C'est là qu'on donne des points, qu'on change la langue, etc.

### 8.1 Les deux banques (principale + backup)
La sauvegarde existe en **double** :
- **banque principale** à `0xEFE000` (4 Ko),
- **banque backup** (secours) à `0xEFF000` (4 Ko).

La console choisit une banque **valide** (au bon checksum) pour charger ta partie.

> 🟢 **Pour tous — la règle pour que ta modif « prenne » :** modifie la **banque principale**, recalcule son checksum (#5), puis **remplis la banque backup de `0xFF`** (zone vierge). Ainsi la console n'a qu'une seule save valide — la tienne — et l'utilise à coup sûr. Si tu laisses un vieux backup valide, la console pourrait charger l'ancien à la place.

> 🔵 **Détail technique** — En pratique l'outil : (1) écrit les nouvelles valeurs dans `0xEFE000`, (2) appelle `save_fix_checksum(b, 0xEFE000)`, (3) remplit `0xEFF000`–`0xEFFFFF` de `0xFF`. C'est le comportement validé sur matériel (le bug « backup » des premières versions venait de l'oubli de cette étape).
> ```python
> for o in range(0xEFF000, 0xF00000):   # vider la banque backup
>     b[o] = 0xFF
> ```

### 8.2 La carte de la save (offsets relatifs au début de la banque)

| Offset | Type | Champ | Notes |
|---|---|---|---|
| `+0x00` | u16 | **CRC-16** | le checksum #5 |
| `+0x02` | u16 | **Complément du CRC** | `~CRC` |
| `+0x1C` | u16 | **Année** | date de la console |
| `+0x1E` | u16 | **Mois** | |
| `+0x20` | u16 | **Jour** | |
| `+0x22` | u16 | **Heure** | |
| `+0x24` | u16 | **Minute** | |
| `+0x26` | u16 | **Seconde** | |
| `+0x64` | u32 | **UID de l'appareil** | identifiant unique |
| `+0x68` | texte | **Nom de la planète** | codes 16 bits, max 12 caractères (§10.5 pour l'encodage) |
| `+0x7B` | u8 | **Langue** | **4=EN, 5=DE, 6=FR, 7=ES, 8=IT** |
| `+0xA8` | u16 | **Nombre de jours** | âge de la partie en jours |
| `+0xB4` | u16 | **Gotchi Points** | max 65535 |
| `+0x108` | u16 | **chara_id** (perso actif) | l'identité du perso vivant (§9) |
| `+0x10A` | u16 | **eye_chara_id** | l'identité des yeux |
| `+0x10C` | u16 | **Timer d'âge** | progression vers le stade suivant |
| `+0x120` | u8 | **Faim (« miam »)** | max 6 |
| `+0x121` | u8 | **Bonheur (humeur)** | max 20 |

> 🟢 **Pour tous** — Exemple : pour passer la console en **français**, tu mets l'octet à `save+0x7B` à la valeur **6**. Pour te donner le **maximum de Gotchi Points**, tu écris **65535** (`0xFFFF`) en u16 à `save+0xB4`. À chaque fois, tu **recalcules le checksum #5** et tu **vides le backup**, sinon ça ne « prend » pas.

### 8.3 Exemple complet de bout en bout (changer la langue en français)
```python
import struct
SAVE = 0xEFE000
b = bytearray(open("ma_copie.bin", "rb").read())   # on travaille sur une COPIE

# 1) modifier le champ langue (FR = 6)
b[SAVE + 0x7B] = 6

# 2) recalculer le checksum de la save principale
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

# 3) vider la banque backup
for o in range(0xEFF000, 0xF00000):
    b[o] = 0xFF

# 4) enregistrer le résultat (fichier à flasher)
open("ma_copie_FR.bin", "wb").write(b)
print("OK — flashe ma_copie_FR.bin")
```

> 🔵 **Note importante (mise à jour vs anciennes notes)** — Le checksum de la save **était** considéré comme « non résolu » dans d'anciens documents. Il est désormais **cracké** (CRC-16 Rocksoft, ci-dessus) et vérifié. Cela débloque **toutes** les modifications de save : perso actif, date, points, faim, bonheur, langue, nom de planète. Tu n'as plus besoin de SWD ni de Ghidra pour ça.


---

<a name="9"></a>
## 9. Les personnages : identité, stades, biome

### 9.1 Le `chara_id`
Chaque personnage du jeu a un **identifiant numérique** unique, le `chara_id`. C'est lui qui dit « ce perso est HORHOTCHI » ou « ce perso est un bébé ». Quelques exemples :

| chara_id | Nom | Stade / biome |
|---|---|---|
| 1001 | BABYMARUTCHI | bébé |
| 2004 | SKY KID | enfant (Ciel) |
| 3016 | ROCKY YOUNG | ado (Ciel) |
| 4050 | **HORHOTCHI** | adulte (Ciel) |
| 4058 | KUCHIPATCHI | adulte (Ciel) |
| 4065 | MAGMATCHI | adulte (Ciel) |
| 4022 | MAMETCHI | adulte (Terre) |
| 4041 | URUOTCHI | adulte (Eau) |

> 🔵 **Détail technique — plages d'IDs par biome :** bébé `1001` ; enfants `2002`-`2004`, `2069` ; ados `3005`-`3016` et `3070`-`3073` ; **Terre `4017`-`4033`** ; **Eau `4034`-`4049`** ; **Ciel `4050`-`4065`** ; spéciaux `4066`-`4068` ; **Forest/Jade `4074`-`4090`** ; objets lab `4800`-`4803`. La liste complète est en §19.1.

### 9.2 Les stades de vie
Un Tamagotchi évolue : **œuf → bébé → enfant → ado → adulte**. Le stade est lié à la fois au `chara_id` (un bébé a un id de bébé) et à un **timer d'âge** dans la save (`save+0x10C`). Forcer un stade demande de changer le `chara_id` **et** de réinitialiser ce timer — c'est une manip avancée.

### 9.3 La chaîne alimentaire (qui devient quoi)
Dans chaque biome, il y a **16 personnages**, organisés en **4 chaînes de 4** (selon la nourriture que tu donnes). Par exemple, dans le Ciel : la chaîne « poulet » mène à HORHOTCHI, la chaîne « maïs » à KUCHIPATCHI, etc.

> 🔵 **Détail technique** — Dans la table des personnages (§10.4), le champ `+0x08` encode l'appartenance à une chaîne (`0x12D`-`0x130` pour le Ciel). Le champ `+0x0E` encode le biome (1=Terre, 2=Eau, 3=Ciel). **Attention :** le champ `+0x04` de ce record est un **piège** — ce n'est PAS l'index du sprite affiché (voir §10.3).

---

<a name="10"></a>
## 10. Les sprites et l'apparence

### 10.1 Qu'est-ce qu'un sprite ?
Un **sprite** est une petite image (un dessin) utilisée par le jeu : le corps d'un perso, ses yeux, sa bouche, un objet… Toutes les images du jeu sont des sprites, rangés dans le **paquet Sprites** de l'archive principale.

> 🔵 **Détail technique** — Le paquet Sprites du Ciel contient **1449 sprites**. Il commence par une **table d'offsets** (un annuaire qui dit où est chaque sprite), suivie des données. Chaque sprite a un **en-tête de 24 octets** puis ses pixels.
> ```python
> MAIN = 0x111000
> # entrées 16o à MAIN+16 (file0=Data), +32 (file1=Sprites), +48 (file2=Strings)
> f1_off = u32(b, MAIN+32+4)          # offset du paquet Sprites
> SPK = MAIN + f1_off
> nspr = u32(b, SPK) // 4             # nombre de sprites = premier offset / 4
> offs = [u32(b, SPK + i*4) for i in range(nspr)]   # la table d'offsets
> ```
> En-tête d'un sprite (24 o) : `+0x00` data_length(u32), `+0x04` flags, `+0x05` bpp (0=1, 1=2, 2=4, 3=8 bits/pixel), `+0x06` num_sprites(u16), `+0x08` largeur, `+0x09` hauteur, `+0x0A` offset_x(s8), `+0x0B` offset_y(s8), `+0x0C` image_w, `+0x0D` image_h, puis palette et pixels. Les pixels peuvent être **compressés en RLE** (flag `0x20`) et/ou **XORés avec `0x53`** (flag `0x80`).

### 10.2 La découverte clé : un perso = 6 sprites
Un personnage adulte n'est **pas un seul dessin** : il est composé de **6 sprites consécutifs** :
1. corps (grande taille, 64×64)
2. yeux (grande taille, 64×32)
3. bouche (grande taille, 64×32)
4. corps (petite taille, 32×32)
5. yeux (petite taille, 32×16)
6. bouche (petite taille, 32×16)

La « grande » version sert à l'affichage normal, la « petite » à certaines scènes (menus, mini-vues).

> 🔵 **Détail technique — HORHOTCHI (référence) :** sprites **#531** (corps 64×64), **#532** (yeux 64×32), **#533** (bouche 64×32), **#534** (corps petit 32×32), **#535** (yeux petit 32×16), **#536** (bouche petite 32×16).

### 10.3 ⚠️ LE PIÈGE n°1 à éviter
Dans la table des personnages, le champ `+0x04` ressemble à un index de sprite — **mais ce n'en est pas un.** Pour HORHOTCHI, `+0x04` vaut 577, alors que ses sprites affichés sont les **531-536**. Si tu te fies à `+0x04`, tu copies les mauvais sprites (par ex. `sprite[586]` qui sont les *yeux* de BATATCHI, pas un corps).

> 🟢 **Pour tous** — **Règle :** pour savoir quels sprites composent un perso, **utilise le mapping ci-dessous** (vérifié sur matériel avec l'outil **tamasprite**), jamais le champ `+0x04`.

> 🔵 **Détail technique — mapping des 16 adultes Ciel** (formule : `premier_sprite = 531 + (rang−33)×6`) :
> | Rang | ID | Nom | Sprites |
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

### 10.4 La table des personnages
> 🔵 **Détail technique** — Records de **30 octets** (`0x1E`), id en `+0x00`. **Ciel : à `0x126ACA`. Jade : à `0x127690`.** Champs : `+0x02` index global, `+0x04` (le piège), `+0x08` chaîne alimentaire, `+0x0E` biome. Les champs `+0x12`/`+0x14` ont été testés : ils **ne contrôlent PAS** le placement visuel.

### 10.5 Changer les sprites en pratique : tamasprite
Les sprites étant **compressés** et de **tailles différentes** d'un perso à l'autre, on ne peut pas simplement « copier-coller » les octets d'un sprite sur un autre dans le dump (les longueurs ne correspondent pas, ça casse l'archive). La bonne méthode :

- **tamasprite** : un outil web qui **affiche** chaque sprite par son index (#531, #549…) et permet de **réimporter** une image dans un slot. C'est l'outil idéal pour **remplacer graphiquement** un perso par un autre (par ex. donner le corps de HORHOTCHI à tous les adultes), parce qu'il **recompresse et repacke** l'archive correctement pour toi.

> 🟢 **Pour tous** — Donc pour **changer le dessin** d'un perso : tu passes par **tamasprite** (import d'image dans le bon slot). Pour changer **où** ses yeux/sa bouche se posent (sans changer le dessin), c'est une autre donnée — les « composite definitions » de la section suivante.

### 10.6 L'encodage des textes (charset)
Les noms (planète, objets, persos) ne sont pas en ASCII simple : chaque caractère est un **code de 16 bits**.

> 🔵 **Détail technique** — `0x131` = espace ; `0x132`-`0x13B` = chiffres 0-9 ; **lettres : `code = 0x00FD + valeur_ASCII`** (donc 'A' (0x41) → `0x013E`) ; accents : `0x197`=É, `0x196`=Ç, `0x199`=Ê, `0x1AA`=Ñ ; `0x178` = apostrophe.
> ```python
> def decode_char(ci):
>     if ci == 0: return None                       # fin de chaîne
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

> ⚠️ **Deux notions de « langue » à ne pas confondre :**
> - l'**index de table de langue dans l'archive Strings** : le **français = index 2** (pour renommer des textes) ;
> - l'**octet de langue du device** (`save+0x7B`) : **français = 6** (pour l'interface). Ce sont deux choses différentes.

---

<a name="11"></a>
## 11. Les positions yeux/bouche (animations) — les « composite definitions »

C'est le sujet le plus subtil, et une **bonne nouvelle** : il est désormais compris et éditable.

### 11.1 Le problème
Quand tu donnes le corps de HORHOTCHI à un autre perso (via les sprites), tu remarques que **les yeux et la bouche restent mal placés**. Pourquoi ? Parce que **la position** où poser chaque sprite n'est **pas** dans le sprite lui-même : elle est dans une donnée séparée appelée **« composite definition »** (définition de composition). En clair : *« où placer chaque morceau quand on dessine le perso »*.

### 11.2 Où ça vit
> 🔵 **Détail technique** — Les composite definitions des 16 adultes Ciel commencent à **`0x167C70`** dans le dump (c'est dans le fichier **Data** de l'archive principale, offset relatif `0x56C30`). **Ces octets sont lisibles directement dans le dump** (contrairement à ce que laissaient penser d'anciennes notes — c'est seulement **Ghidra** qui ne les « voit » pas, car cette zone n'est pas chargée dans le code XIP, §16).

### 11.3 La structure
> 🔵 **Détail technique**
> - Chaque adulte est décrit par **exactement 112 « couches »** (layers), dans le **même ordre** pour tous les persos.
> - Une couche fait : `sprite_id (u16)` + `packed (u16)` + `ox (s16)` + `oy (s16)` + un *trailer* de taille variable.
> - Les `oy` négatifs (ex. `-33` = `0xFFDF`, `-32` = `0xFFE0`) sont les **positions verticales** — c'est ce qui change d'un perso à l'autre.
> - **Rôle de chaque couche :** 0 = corps, 1 = yeux, 2 = bouche, 3 = corps petit, 4 = yeux petit, 5 = bouche petit.
> - **Sprites partagés à NE PAS remapper :** 204, 205, 206 (ombres/effets communs).
> - **Adresses de début de bloc** (16 adultes) :
>
> | Corps | Nom | Début du bloc |
> |---|---|---|
> | 531 | HORHOTCHI | `0x167C70` |
> | 537 | (rang 34) | `0x168354` |
> | 543 | (rang 35) | `0x168A38` |
> | 549 | (rang 36) | `0x16911C` |
> | 555 | (rang 37) | `0x169802` |
> | 561 | (rang 38) | `0x169EE8` |
> | 567 | (rang 39) | `0x16A5CC` |
> | 573 | (rang 40) | `0x16ACB2` |
> | 579 | (rang 41) | `0x16B396` |
> | 585 | (rang 42) | `0x16BA7A` |
> | 591 | (rang 43) | `0x16C15E` |
> | 597 | (rang 44) | `0x16C842` |
> | 603 | (rang 45) | `0x16CF28` |
> | 609 | (rang 46) | `0x16D60C` |
> | 615 | (rang 47) | `0x16DCF0` |
> | 621 | (rang 48) | `0x16E3D4` |

### 11.4 Le modèle « relatif » (delta) — la bonne façon de patcher
On veut que tous les adultes ressemblent à HORHOTCHI **et gardent ses animations**. Or les positions **varient légèrement d'une frame à l'autre** (le corps respire, les yeux clignent : `oy` passe de -33 à -35, etc.). Si on « aplatissait » tout à une seule valeur, on **détruirait les animations** (yeux figés).

La bonne méthode est donc **relative** :
> **Position finale d'une couche = position de HORHOTCHI pour cette couche + un décalage (delta) propre au perso.**
- delta **0** ⇒ le perso est **identique à HORHOTCHI** (positions ET animations préservées) ;
- delta **non nul** ⇒ on décale uniformément ce rôle (ex. yeux +2) **sans casser** l'animation.

> 🟢 **Pour tous** — Concrètement, on prend l'animation complète de HORHOTCHI comme **gabarit** pour tout le monde. Si tu veux qu'un perso ait les yeux 2 pixels plus bas, tu mets un delta de +2 sur ses yeux — et ça s'applique à toutes les frames sans abîmer le mouvement.

> 🔵 **Détail technique** — Après avoir réécrit les `oy`/`ox` des couches, **recalcule le checksum ARC2 de l'archive principale** (§7.3). C'est le seul checksum impacté ; la save n'est pas touchée. Le `patcher_offsets_relatif.py` (fourni dans tes outils) lit la base HORHOTCHI **en mémoire d'abord** (pour qu'un delta sur HORHOTCHI ne corrompe pas la base des autres), applique base+delta à chaque couche, puis recalcule l'ARC2.

---

<a name="12"></a>
## 12. Les ghosts (les persos « fantômes »)

### 12.1 C'est quoi ?
Les **ghosts** sont des enregistrements de personnages stockés dans une zone dédiée — en gros, les persos que tu as rencontrés/collectés, plus le perso actif. Ils occupent la zone **`0xDEE000`–`0xE45FFF`**.

### 12.2 Comment on les repère (scan par signature)
La console (et nos outils) **scannent** la zone à la recherche d'enregistrements valides, reconnus par leur **signature de checksum** (le #2 : `w0 + w4 == 0`). Pas besoin d'une liste : un slot contient un ghost s'il a un checksum cohérent.

> 🔵 **Détail technique — scan des ghosts**
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

### 12.3 La structure d'un ghost
> 🔵 **Détail technique** — `+0x00` w0 (checksum), `+0x04` w4 (complément), `+0x08` flags (type), `+0x0C` **character_id (u16)**, `+0x0E` eye_character_id, `+0x10` couleur, `+0x10C` **total_length (u32)**, **nom embarqué à `+0x2C` et `+0x46`** (codes 16 bits, §10.6).
> - **Ciel :** `+0x0C` = le vrai character_id.
> - **Jade :** `+0x0C` = marqueur de stade (4017 pour tous les adultes) ; la vraie identité est à **`+0x10A`** ; le **nom embarqué** reste fiable.

### 12.4 Disposition des slots
> 🔵 **Détail technique** — La zone est découpée en slots de `0x2000`, mais un ghost occupe en pratique **`0x4000`** (16 Ko) — donc les ghosts tombent sur les slots **pairs** (0, 2, 4…). Un slot **vide** est **entièrement à `0xFF`** (flash vierge). Le **slot 0** (`0xDEE000`) est le **perso actif** : on ne le supprime pas. Numéro de slot = `(adresse − 0xDEE000) / 0x2000`.

### 12.5 Ajouter / supprimer un ghost
On a vérifié deux choses essentielles : (a) les slots vides sont à `0xFF`, et (b) **il n'y a pas de compteur de ghosts** dans la save à maintenir. Le modèle qui en découle :
- **Ajouter un perso** = **copier l'enregistrement complet** d'un ghost existant dans un slot vide (aligné sur `0x4000`), puis **recalculer son checksum #2**. Un re-scan le détecte alors comme un ghost de plus.
- **Supprimer un perso** = **remplir son slot de `0xFF`**.

> 🟢 **Pour tous** — Ça suppose que la console **scanne** les slots (très probable, vu qu'aucun compteur n'existe). **À confirmer par un test matériel** : ajoute UN ghost, flashe, regarde s'il apparaît. Si oui, le mécanisme est validé et tu peux ajouter/supprimer librement. L'éditeur de ghosts fourni fait tout ça (copie + checksum + protection du slot 0).

> 🔵 **Détail technique — ajout d'un ghost**
> ```python
> def add_ghost(b, empty_base, src_base):       # empty_base aligné sur 0x4000, tout 0xFF
>     tlen = u32(b, src_base+0x10C); rec = (tlen + 3) & ~3
>     b[empty_base:empty_base+rec] = b[src_base:src_base+rec]
>     ghost_fix_checksum(b, empty_base)         # cf. §7.4
> def remove_ghost(b, base):
>     for o in range(base, base+0x4000):
>         b[o] = 0xFF
> ```

---

<a name="13"></a>
## 13. Le système de biome

### 13.1 Les deux niveaux (à bien comprendre)
Le biome (Terre / Eau / Ciel / Jade) est géré à **deux endroits** :
1. **Un flag dans le firmware**, à `0xD49000` (un u32 : **1=Terre, 2=Eau, 3=Ciel, 4=Jade**). Ce flag n'est lu **qu'une seule fois** : à la **création d'une partie neuve**.
2. **Ta sauvegarde**, qui une fois créée devient le **maître** : tant qu'une save valide existe, le biome vient d'elle et le flag est **ignoré**.

### 13.2 Comment changer de biome (procédure validée)
Puisque la save prime, il faut **deux actions obligatoires** :
1. **modifier le flag** à `0xD49000` vers le biome voulu (et **recalculer le checksum #3** du bloc version, par sécurité — §7.5),
2. **effacer la save** : remplir `0xEFE000`–`0xEFFFFF` de `0xFF`.

Résultat : au démarrage, la save étant vide/invalide, la console **relit le flag**, en déduit le nouveau biome, et **crée une partie neuve** dessus.

> 🟢 **Pour tous** — En clair : changer de biome = **« je dis quel biome je veux (flag) ET j'efface ma partie pour forcer une nouvelle partie dans ce biome ».** Tu **perds ta progression** au passage (c'est inévitable, le biome est lié à la partie).

> 🔵 **Détail technique** — Terre/Eau/Ciel partagent **exactement le même firmware** (0 octet de différence dans code+assets) ; seuls les ~11 octets du bloc version diffèrent. **Jade**, lui, a un firmware **différent** (~10 % d'assets et de code différents). Les valeurs de config associées : Terre/Eau/Ciel → `f4=0x0001`, `f6=0x0004` (à `0xD49FF4`/`0xD49FF6`) ; Jade → `f4=0x0002`, `f6=0x0000`.

```python
import struct
VER = 0xD49000
b = bytearray(open("ma_copie.bin","rb").read())
struct.pack_into("<I", b, VER, 3)            # 3 = Ciel (1=Terre, 2=Eau, 4=Jade)
# (recalcul du checksum bloc version, §7.5)
MAGIC, END = 0xFFFFFC03, 0xD49FF8
s = sum(b[:END]) & 0xFFFFFFFF
V = (MAGIC - s) & 0xFFFFFFFF
struct.pack_into("<I", b, 0xD49FF8, V)
struct.pack_into("<I", b, 0xD49FFC, (~V) & 0xFFFFFFFF)
# effacer les deux banques de save
for o in range(0xEFE000, 0xF00000): b[o] = 0xFF
open("ma_copie_ciel.bin","wb").write(b)
```

---

<a name="14"></a>
## 14. Les codes d'unlock

Le jeu accepte des **codes** (saisis dans le menu, ou via QR/boutique) pour débloquer des contenus.

> 🔵 **Détail technique** — La table principale de codes est à **`0x9BA6C`** : **109 codes**, **9 octets chacun**, en **ASCII brut**. **Aucun checksum** (c'est dans le XIP en clair, et le checksum #3 n'est pas vérifié au boot). Une **2e table** alphanumérique est à `0x9BE41` (codes QR/boutique probables). Tu peux donc lire/éditer ces codes directement, sans recalcul.


---

<a name="15"></a>
## 15. Étape 4 — Réécrire la puce (« flasher »)

Une fois ton `.bin` modifié, il faut l'**écrire** sur la puce.

### 15.1 La procédure simple dans Asprogrammer
1. Branche le programmateur et la pince/pogo pins (comme pour la lecture).
2. Ouvre Asprogrammer, choisis `CH347`, fais **Detect**.
3. **File → Open** : ouvre ton `.bin` modifié (il se charge dans l'éditeur d'Asprogrammer).
4. **Unprotect / Unlock** si la puce est protégée en écriture.
5. **Erase IC** : efface la puce (la met à `0xFF`). *Obligatoire avant d'écrire*, car on ne peut pas écrire « par-dessus ».
6. **Program IC** (écrire) : Asprogrammer écrit ton fichier.
7. **Verify** : il relit et compare pour confirmer que l'écriture est correcte.

> 🟢 **Pour tous** — L'ordre est toujours : **Unlock → Erase → Write → Verify.** Si « Verify » est OK, ta modification est en place : rebranche la console et observe. Si quelque chose cloche, **re-flashe ton dump original** (le filet de sécurité).

> ⚠️ Asprogrammer **n'a pas de ligne de commande** : pas d'automatisation possible, tout se fait par clics dans l'interface. (Une automatisation par simulation de clics serait fragile.)

### 15.2 Pour aller plus loin : un script `.pas`
Asprogrammer sait exécuter des **scripts Pascal** (`.pas`) qui définissent ce que font les boutons Unlock/Erase/Write/Verify pour ta puce précise.

> 🔵 **Détail technique** — Un script `tamagotchi_paradise.pas` définit :
> - `{$unlock}` : Write Enable (`0x06`) + Write Status Register (`0x01 0x00`) pour déverrouiller.
> - `{$erase}` : Write Enable + Chip Erase (`0xC7`) + attente de la fin (poll du bit WIP via Read Status `0x05`).
> - `{$write}` : boucle par pages de 256 octets — Write Enable + Page Program (`0x02`) + adresse sur 3 octets + données (`SPIWriteFromEditor`).
> - `{$verify}` : lecture (`0x03`) + comparaison avec l'éditeur.
>
> À placer dans le dossier `scripts\` d'Asprogrammer. Usage : ouvrir le `.bin`, sélectionner le script, cliquer Unlock → Erase → Write → Verify.

### 15.3 Combien de temps / quels risques ?
- Effacer + écrire 16 Mo prend généralement **moins d'une minute** avec un CH347.
- **Le pire risque** est une écriture interrompue (pince qui bouge, USB débranché) → la puce est dans un état incohérent. **Solution : recommencer (Erase + Write).** Tant que la puce répond au programmateur, **rien n'est définitif** : tu peux toujours re-flasher l'original.

---

<a name="16"></a>
## 16. Outils avancés : Ghidra et SWD

Tu n'en as **pas besoin** pour les hacks courants (save, sprites, ghosts, biome). Ils servent quand tu veux **comprendre le code du moteur** lui-même.

### 16.1 Ghidra (analyse du code)
**Ghidra** est un outil gratuit (de la NSA) qui **désassemble** et **décompile** du code machine : il transforme les octets du programme en quelque chose de lisible.

> 🔵 **Détail technique — charger le code XIP dans Ghidra**
> 1. Extraire le XIP : les octets `flash[0x11000:0x110000]` (1 044 480 octets).
>    ```python
>    open("code_XIP.bin","wb").write(open("dump.bin","rb").read()[0x11000:0x110000])
>    ```
> 2. Dans Ghidra : importer en **Raw Binary**, **Language = `ARM:LE:32:Cortex`**, **Base Address = `0x60011000`**. À l'analyse, cocher *ARM Aggressive Instruction Finder*.
> 3. Correspondance d'adresses : `adresse_exec = 0x60011000 + (offset_flash − 0x11000)`.
>
> **Limite majeure :** les **assets** (au-delà de `0x110000`, donc tout ce qui est sprites/textes/tables comme `0x167C70`) **ne sont PAS** dans le XIP — Ghidra ne les voit pas. De plus, le code accède aux assets par **adressage calculé** (registre + offset), donc **pas de référence croisée directe**. Conclusion : Ghidra est excellent pour **partir d'une chaîne de texte** et tracer le code qui l'utilise ; **inadapté** pour une table de données. Pour ces tables, le **SWD** (ci-dessous) est bien plus efficace.

### 16.2 SWD (debug en direct)
**SWD** (*Serial Wire Debug*) est le mode de **débogage** des puces ARM : avec **2 fils** (SWDIO + SWCLK), on peut **lire/écrire la mémoire et les registres en direct**, poser des **breakpoints**, exécuter **pas à pas**.

> 🟢 **Pour tous** — C'est comme mettre la console « en pause » pour regarder ce qu'elle fait, instant par instant. Idéal pour résoudre les mystères qui restent (par ex. « quelle adresse lit-elle exactement pour placer les yeux ? »).

> 🔵 **Détail technique**
> - **Pins SWD** (sur les test pads, sans soudure) : `SWCLK = P0.13`, `SWDIO = P0.14`, `SWO = P0.12`. Plus GND et RST (voir §19.5).
> - **Matériel :** un **ST-Link V2** (~15 €) ou un **Raspberry Pi Pico** en *picoprobe* (~5 €), + une **pince à pogo pins** (~10 €). Pas de soudure grâce aux test pads.
> - **Logiciel :** OpenOCD + GDB, ou pyOCD.
> - Rappel : le bootrom **active SWD par défaut** s'il n'y a pas de firmware valide. Un patch (`..._no_crypt_with_swd.ips`) peut le réactiver de force et désactiver la vérif de chiffrement.

---

<a name="17"></a>
## 17. Recettes pratiques (« je veux faire X »)

Chaque recette suit le même squelette : **(0) pars d'une copie d'un dump frais → (1) modifie → (2) recalcule le bon checksum → (3) gère le backup si c'est la save → (4) flashe → (5) vérifie sur la console.**

### Recette A — Passer la console en français
1. `b[0xEFE000 + 0x7B] = 6`
2. recalcule le **checksum save** (#5) sur la banque principale
3. **vide la banque backup** (`0xEFF000`–`0xEFFFFF` ← `0xFF`)
4. flashe, vérifie.

### Recette B — Donner le maximum de Gotchi Points
1. `struct.pack_into("<H", b, 0xEFE000 + 0xB4, 65535)`
2. checksum save (#5) + vider le backup
3. flashe.

### Recette C — Changer la date
1. écris année/mois/jour/heure/minute/seconde en u16 à `0xEFE000 + 0x1C…0x26`
2. checksum save (#5) + vider le backup
3. flashe.

### Recette D — Renommer la planète
1. encode le nom en codes 16 bits (§10.6) et écris-le à `0xEFE000 + 0x68` (max 12 caractères, termine par `0x0000`)
2. checksum save (#5) + vider le backup
3. flashe.

### Recette E — Unifier les positions des adultes Ciel sur HORHOTCHI
1. utilise le **patcher relatif** (modèle delta, §11.4) avec des deltas à 0 (ou ajuste un perso)
2. il recalcule le **checksum ARC2 principal** (#1) ; la save n'est pas touchée
3. flashe, vérifie les animations.

### Recette F — Remplacer graphiquement un perso par HORHOTCHI
1. ouvre le dump dans **tamasprite**
2. importe les sprites de HORHOTCHI (#531-536) dans les slots du perso cible
3. tamasprite repacke et recalcule le checksum ARC2 pour toi
4. flashe.

### Recette G — Renommer un perso ou un objet (texte)
1. localise l'archive **Strings** (Ciel à `0x802260`), table FR = **index 2**
2. édite le texte **en place** (respecte la longueur)
3. recalcule le checksum **Strings d'abord, puis Principale** (#1, l'ordre est crucial)
4. flashe.

### Recette H — Changer l'identité d'un ghost
1. trouve le ghost (scan, §12.2)
2. change son nom (`+0x2C` et `+0x46`) et son id (`+0x0C` en Ciel, `+0x10A` en Jade)
3. recalcule le **checksum ghost** (#2)
4. flashe.

### Recette I — Ajouter un perso dans un slot vide
1. copie un ghost existant dans un slot vide (aligné `0x4000`, tout `0xFF`) + checksum ghost (#2)
2. flashe et **vérifie qu'il apparaît** (confirme le modèle « scan », §12.5).

### Recette J — Changer de biome
1. flag à `0xD49000` (1/2/3/4) + checksum bloc version (#3)
2. **efface les deux banques de save** (`0xEFE000`–`0xEFFFFF` ← `0xFF`)
3. flashe (⚠️ tu perds ta progression).

---

<a name="18"></a>
## 18. La boîte à outils Python (à copier-coller)

```python
import struct

# ---------- lecture de base ----------
def load(path): return bytearray(open(path, "rb").read())
def save(path, b): open(path, "wb").write(b)
def u8(b, o):  return b[o]
def u16(b, o): return struct.unpack_from("<H", b, o)[0]
def u32(b, o): return struct.unpack_from("<I", b, o)[0]
def s16(b, o): return struct.unpack_from("<h", b, o)[0]
def wu16(b, o, v): struct.pack_into("<H", b, o, v & 0xFFFF)
def wu32(b, o, v): struct.pack_into("<I", b, o, v & 0xFFFFFFFF)

# ---------- adresses clés ----------
MAIN_ARC = 0x111000
VERSION  = 0xD49000
SAVE     = 0xEFE000
SAVE_BAK = 0xEFF000
GHOST_S  = 0xDEE000
GHOST_E  = 0xE46000

# ---------- checksum ARC2 (#1) ----------
def arc2_fix(b, base, total_len):
    s = sum(b[base+8 : base+total_len]) & 0xFFFFFFFF
    wu32(b, base+4, s)

# ---------- checksum ghost (#2) ----------
def ghost_fix(b, base):
    tlen = u32(b, base+0x10C); end = base + ((tlen+3) & ~3)
    s = 0
    for o in range(base+8, end, 4): s = (s + u32(b, o)) & 0xFFFFFFFF
    wu32(b, base+0, s); wu32(b, base+4, (-s) & 0xFFFFFFFF)

# ---------- checksum bloc version (#3) ----------
def version_fix(b):
    s = sum(b[:0xD49FF8]) & 0xFFFFFFFF
    V = (0xFFFFFC03 - s) & 0xFFFFFFFF
    wu32(b, 0xD49FF8, V); wu32(b, 0xD49FFC, (~V) & 0xFFFFFFFF)

# ---------- checksum save (#5) ----------
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

# ---------- exemple : français + max points ----------
if __name__ == "__main__":
    b = load("ma_copie.bin")
    b[SAVE + 0x7B] = 6              # langue FR
    wu16(b, SAVE + 0xB4, 65535)     # Gotchi Points max
    save_fix(b)                     # checksum save
    clear_backup(b)                 # vider le backup
    save("ma_copie_modifiee.bin", b)
    print("OK")
```

---

<a name="19"></a>
## 19. Tables de référence

### 19.1 Personnages (chara_id → nom)
| ID | Nom | | ID | Nom |
|---|---|---|---|---|
| 1001 | BABYMARUTCHI | | 4041 | URUOTCHI |
| 2002 | LAND KID | | 4042 | TACHUTCHI |
| 2003 | WATER KID | | 4043 | SHARKTCHI |
| 2004 | SKY KID | | 4044 | ANKOTCHI |
| 2069 | FOREST KID | | 4045 | OTOTOTCHI |
| 3005-3016 | (ados) | | 4046 | KURARATCHI |
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
| 4040 | KAWAZUTCHI | | 4800-4803 | (objets lab) |

Biomes : **Terre 4017-4033**, **Eau 4034-4049**, **Ciel 4050-4065**, spéciaux 4066-4068, **Forest/Jade 4074-4090**.

### 19.2 Offsets de la save (relatifs à `0xEFE000`)
| Offset | Type | Champ |
|---|---|---|
| +0x00 | u16 | CRC-16 |
| +0x02 | u16 | complément CRC |
| +0x1C…+0x26 | u16 ×6 | année, mois, jour, heure, minute, seconde |
| +0x64 | u32 | UID appareil |
| +0x68 | texte | nom de planète (≤12 car.) |
| +0x7B | u8 | langue (4=EN,5=DE,6=FR,7=ES,8=IT) |
| +0xA8 | u16 | nombre de jours |
| +0xB4 | u16 | Gotchi Points |
| +0x108 | u16 | chara_id |
| +0x10A | u16 | eye_chara_id |
| +0x10C | u16 | timer d'âge |
| +0x120 | u8 | faim (max 6) |
| +0x121 | u8 | bonheur (max 20) |

### 19.3 Adresses clés du firmware
| Adresse | Quoi |
|---|---|
| `0x0` | en-tête / load table (`SONIXDEV`) |
| `0x1000`–`0x10FFF` | code PRAM (chiffré) |
| `0x11000`–`0x10FFFF` | code XIP (en clair) |
| `0x111000` | archive principale ARC2 |
| `0x126ACA` | table des persos (Ciel) |
| `0x127690` | table des persos (Jade) |
| `0x167C70` | composite definitions adultes Ciel |
| `0x802260` | archive Strings (Ciel) |
| `0x9BA6C` | table de codes (109 × 9 o) |
| `0xD49000` | flag biome |
| `0xD49FF8` / `0xD49FFC` | checksum bloc version / complément |
| `0xDEE000`–`0xE45FFF` | ghosts |
| `0xEFE000` / `0xEFF000` | save principale / backup |

### 19.4 Récapitulatif des checksums
| # | Quoi | Où | Formule | Vérifié au boot ? |
|---|---|---|---|---|
| 1 | ARC2 | archive+0x04 | somme octets [+0x08 : fin] | oui (assets) |
| 2 | Ghost | ghost+0x00/+0x04 | somme mots 32 bits ; w0+w4=0 | oui (scan) |
| 3 | Bloc version | 0xD49FF8/0xD49FFC | 0xFFFFFC03 − somme octets(0..0xD49FF8) | **non** |
| 4 | CRC32 PRAM | load table+0x24 | CRC32 (poly 0xEDB88320) | oui (si chiffré) |
| 5 | Save | 0xEFE000+0x00/+0x02 | CRC-16 Rocksoft sur [+0x04 : +0x1000] | **oui** |
| 6 | Screenshot | sprite+0x00/+0x04 | somme mots ; somme+comp=0xFFFFFFFF | oui |
| 7 | Chunk TCP | en-tête réseau | CRC-16 Rocksoft (0x8005) | oui (réseau) |

### 19.5 Test pads (accès sans soudure)
- **SWD :** `P0.13=SWCLK`, `P0.14=SWDIO`, `P0.12=SWO`.
- **UART :** `TP35=P0.2 TXD1`, `TP37=P0.3 RXD1` ; `TP48=P0.1 RXD0`, `P0.0=TXD0`.
- **Flash SPI :** `TP24=CS`, `TP26=CLK`, `TP27=MISO`, `TP28=MOSI`, `TP30=D2`, `TP31=D3`.
- **Boutons :** `TP34=dial`, `TP36=A`, `TP38=B`, `TP39=C`. **Encodeur :** `TP32=P2.0`, `TP33=P2.1`.
- **Alim/Reset :** VCC `TP12`/`TP22` ; GND `TP29`/`TP46`/`TP49` ; RST `TP21`/`TP25(SW1)`/`TP45` ; VBAT `TP1` ; VREG 3V3 `TP2`.

### 19.6 Commandes SPI (MX25L12835F)
READ `0x03` · Page Program `0x02` · Write Enable `0x06` · Read Status `0x05` (bit0=WIP) · Sector Erase 4K `0x20` · Block Erase 64K `0xD8` · Chip Erase `0xC7` · Write Status `0x01`.

---

<a name="20"></a>
## 20. Glossaire pour débutant total

- **Adresse / offset** — le numéro d'un octet dans la flash (écrit en hexa). « save+0x7B » = 123 octets après le début de la save.
- **Archive (ARC2)** — un conteneur maison qui regroupe images/textes/données, comme un `.zip`. Peut en contenir d'autres.
- **ASCII** — la façon standard de coder les lettres en informatique (A=65…). Ici les textes utilisent un encodage **différent** (codes 16 bits, §10.6).
- **Bit / octet** — bit = 0 ou 1 ; octet = 8 bits = un nombre de 0 à 255.
- **Boot / démarrage** — le moment où la console s'allume et charge son firmware.
- **Checksum** — un « total de contrôle » qui détecte les modifications/corruptions (§7).
- **CRC / CRC-16 / CRC32** — des familles de checksums basées sur des maths de division binaire. « Rocksoft » est un jeu de réglages précis du CRC-16.
- **Dump** — une copie complète de la puce dans un fichier `.bin`.
- **Firmware** — le logiciel embarqué (programme + données) de la console.
- **Flash (puce flash)** — la mémoire non-volatile qui garde tout, même éteinte. **Flasher** = y écrire.
- **Hexadécimal (hexa)** — la base 16 (0-9 puis A-F), préfixée `0x`. Un octet = 2 chiffres hexa.
- **Little-endian** — l'ordre d'octets du SNC7330 : poids faible d'abord (`0x1234` → `34 12`).
- **Patch / patcher** — une modification / modifier le `.bin`.
- **PRAM** — la zone de code **chiffrée** (`0x1000`-`0x10FFF`). On n'y touche presque jamais.
- **Reverse engineering** — examiner comment un système marche pour le comprendre/modifier.
- **Sprite** — une petite image (corps, yeux, bouche, objet…).
- **SPI** — le protocole série (4 fils) par lequel le programmateur parle à la flash.
- **SWD** — le mode de débogage en direct des puces ARM (2 fils).
- **u8 / u16 / u32 / s16** — un nombre sur 1/2/4 octets ; `s` = signé (peut être négatif).
- **XIP** — *eXecute In Place* : la zone de code **en clair** (`0x11000`+) exécutée directement depuis la flash.

---

<a name="21"></a>
## 21. Dépannage et sécurité

### 21.1 « La console ne démarre plus / écran noir »
- **Re-flashe ton dump original.** C'est la solution à 99 % des problèmes. Tant que la puce répond au programmateur, rien n'est définitif.
- Vérifie que tu as bien fait **Erase avant Write** et que **Verify** est passé.

### 21.2 « Ma modification de save ne s'applique pas »
- Tu as probablement oublié de **recalculer le checksum save (#5)** ou de **vider la banque backup**. Sans ça, la console rejette ta save (ou charge l'ancien backup). Refais les deux.

### 21.3 « J'ai modifié une image/un texte et le jeu plante ou affiche n'importe quoi »
- Checksum **ARC2** non recalculé, ou **mauvais ordre** (Strings doit être recalculé **avant** Principale). Recommence dans le bon ordre (§7.3).

### 21.4 « Les yeux/la bouche sont mal placés après un changement de sprite »
- Normal : les **positions** sont dans les composite definitions (§11), pas dans les sprites. Utilise le **patcher relatif** (delta).

### 21.5 « La lecture/écriture échoue de façon aléatoire »
- Mauvais contact de la pince/pogo pins (le plus fréquent), ou alimentation instable. Renettoie, repositionne, assure-toi d'être en **3,3 V**. Vérifie que le dump fait bien **16 777 216 octets**.

### 21.6 Règles d'or à ne jamais oublier
1. **Toujours partir d'une copie d'un dump récent de TA console.**
2. **Garde l'original intact** comme filet de sécurité.
3. **Un changement risqué = teste-le sur UN seul cas d'abord.**
4. **Après chaque modif, recalcule le bon checksum** (et pour la save, vide le backup).
5. **3,3 V**, jamais 5 V.

---

<a name="22"></a>
## 22. Comment tout ça a été découvert (la démarche du détective)

Cette section est différente des autres : elle ne te dit pas *quoi* faire, mais *comment* tout ce qui précède a été **trouvé et déduit**. C'est la partie la plus utile sur le long terme, parce qu'elle t'apprend à **craquer toi-même** ce qui n'est pas encore documenté.

> 🟢 **Pour tous** — Le reverse engineering ressemble à une enquête policière. On ne « casse » pas un coffre-fort par la force : on **observe des indices**, on **forme une hypothèse**, on la **teste**, et on **recommence** jusqu'à ce que tout colle. Aucune étape ci-dessous n'a demandé de génie — juste de la méthode et de la patience.

### 22.1 La philosophie générale
Tout repose sur une boucle simple, répétée des dizaines de fois :
1. **Observer** (regarder les octets, comparer des fichiers).
2. **Formuler une hypothèse falsifiable** (« je parie que cet octet, c'est la langue »).
3. **Tester** (modifier, recalculer, flasher, regarder la console).
4. **Garder ou jeter** l'hypothèse selon le résultat, puis recommencer.

La règle d'or de l'enquêteur : **ce que dit la doc n'est pas forcément ce que fait le matériel.** On vérifie toujours sur la vraie console (§22.8 en donne un exemple spectaculaire).

### 22.2 La technique reine : comparer deux dumps (le « diff »)
C'est **l'outil le plus puissant** et le plus simple. Le principe :
1. tu fais un dump de la console **avant** une action,
2. tu fais **une seule** action sur la console (nourrir le perso, changer la langue, gagner des points…),
3. tu refais un dump **après**,
4. tu **compares** les deux fichiers octet par octet : **seuls les octets liés à cette action changent**.

> 🟢 **Pour tous** — Si tu nourris ton Tamagotchi puis que tu compares les deux dumps, l'octet qui change est (très probablement) le compteur de faim. C'est exactement comme ça que les champs **faim (`save+0x120`)** et **bonheur (`save+0x121`)** ont été localisés : une action ciblée, un diff, et l'octet coupable saute aux yeux.

> 🔵 **Détail technique** — Un diff minimal en Python :
> ```python
> a = open("avant.bin","rb").read()
> b = open("apres.bin","rb").read()
> for i in range(len(a)):
>     if a[i] != b[i]:
>         print(f"0x{i:X}: {a[i]:02X} -> {b[i]:02X}")
> ```
> Astuce : si trop d'octets changent (l'horloge avance, par exemple), **réduis la fenêtre** à la zone save (`0xEFE000`–`0xF00000`) et ignore les champs date. Les champs **langue (`+0x7B`)**, **points (`+0xB4`)**, **date (`+0x1C`…)**, **chara_id (`+0x108`)** ont tous été confirmés ainsi : on change la valeur dans le jeu, on diff, on relie l'offset au sens.

### 22.3 Comment on craque un checksum
Trois checksums, trois méthodes différentes — c'est instructif.

**(a) Le checksum ARC2 : reconnaître une somme simple.**
La structure des archives venait de la recherche publique de GMMan (le champ checksum est à `+0x04`). Restait à trouver *comment* il est calculé. On a testé l'hypothèse la plus simple — **une somme de tous les octets** — sur une archive intacte : le total calculé tombait pile sur la valeur stockée. Hypothèse confirmée, et **reproductible** sur d'autres archives. *Leçon : teste toujours l'explication la plus bête d'abord (somme), avant de supposer un truc compliqué (CRC).*

**(b) Le checksum du bloc version : l'enquête mathématique complète.**
C'est le cas d'école. La démarche, étape par étape :
1. **Comparer les binaires des 4 biomes** (Terre/Eau/Ciel/Jade), bloc de 4 Ko par 4 Ko. Résultat frappant : entre Terre, Eau et Ciel, **un seul bloc diffère** (`0xD49000`). *Les différences minimales révèlent ce qui commande le comportement.*
2. **Reconnaître un motif** : à `0xD49FF8` et `0xD49FFC`, deux valeurs sont **complémentaires** (`V` et `~V`, telles que `V XOR ~V = 0xFFFFFFFF`). Signe quasi certain d'un checksum + son complément.
3. **Hypothèse mathématique** : en changeant **un** octet du firmware, on observe que `V` **diminue de 1**. Donc ce n'est pas un CRC (qui « exploserait »), mais une **somme additive**. On teste alors : *« est-ce que `V + somme_des_octets(d'une plage) = une constante ? »* On essaie plusieurs plages → **HIT** : `V + somme(0 .. 0xD49FF8) = 0xFFFFFC03`.
4. **Valider sur plusieurs données** : la formule tient sur les 4 firmwares. 
5. **Forger une preuve** : on transforme un firmware Eau en firmware Ciel **octet pour octet** → la console l'accepte. Preuve définitive.

**(c) Le checksum de la save : la recherche de paramètres CRC (« RevEng »).**
Celui-là **est** un vrai CRC, et le diff/la somme ne suffisent pas. La méthode standard pour craquer un CRC inconnu :
1. **rassembler plusieurs paires connues** (un bloc de données + le checksum stocké à côté) — ici, plusieurs banques de save valides ;
2. **chercher les paramètres** du CRC (largeur, polynôme, valeur initiale, réflexion d'entrée/sortie, XOR final) qui **reproduisent** ces paires. Il existe des outils dédiés (le célèbre **CRC RevEng**) qui balaient automatiquement l'espace des paramètres.
3. Résultat : un **CRC-16 « Rocksoft »** (polynôme `0xA001` reflété, init `0x0000`, entrée/sortie reflétées, pas de XOR final), calculé sur `[save+0x04 : save+0x1000]`, reproduit exactement la valeur stockée à `save+0x00`. *Confirmé en recalculant la même valeur que celle déjà présente dans des saves intactes.*

> 🟢 **Pour tous** — Retiens la hiérarchie : **(1)** essaie une **somme** (le plus courant) ; **(2)** si la valeur a un **complément** à côté, c'est un checksum à coup sûr ; **(3)** si la somme ne marche pas et que ça « explose » quand tu changes un octet, c'est un **CRC** → outil RevEng avec des paires connues.

### 22.4 Comment on a compris le chiffrement
Le code PRAM (`0x1000`-`0x10FFF`) est chiffré. On ne l'a pas « cassé » à l'aveugle : le schéma Sonix était **déjà documenté publiquement** par GMMan (dépôt `snc73xx-firmware-encryption`). Le vrai travail a été de **vérifier** qu'on l'appliquait correctement, grâce à deux **oracles** (des vérités connues qui disent « c'est bon ») :
- la **load table** (au début du flash) contient `CRC_CHK_SUM = 0x3745D94A`, qui est le **CRC32 du code une fois déchiffré**. Si notre déchiffrement donne ce CRC32, c'est gagné ;
- le code déchiffré doit commencer par une **vector table ARM valide** (un pointeur de pile `SP` plausible et un vecteur Reset en Thumb). On a obtenu `SP = 0x1801EE38` — cohérent.

> 🟢 **Pour tous** — Un « oracle », c'est une réponse connue d'avance qui te dit si tu as bon. Ici : « le CRC32 du résultat doit valoir `0x3745D94A` ». Tant que tu ne tombes pas dessus, ton déchiffrement est faux ; quand tu tombes dessus, tu sais que c'est juste. On a aussi fait le **chemin inverse** (re-chiffrer) et vérifié qu'on **retombait sur le fichier d'origine** bit pour bit — la preuve ultime qu'on maîtrise les deux sens.

### 22.5 Comment on a trouvé les sprites et le piège `+0x04`
1. **Inspection visuelle avec tamasprite** : en faisant défiler les sprites par index, on voit que pour un adulte, **6 images consécutives** forment un corps, des yeux, une bouche, puis les mêmes en petit. D'où la règle « un perso = 6 sprites ».
2. **Le piège** : il était tentant de croire que le champ `+0x04` de la table des persos (577 pour HORHOTCHI) **était** l'index du sprite. On a testé → **échec** : copier `sprite[586]` donnait les **yeux de BATATCHI**, pas un corps. La valeur `+0x04` n'est donc **pas** l'index affiché.
3. **La bonne piste, validée sur matériel** : copier les **6 sprites 531-536** (repérés par tamasprite) dans les slots d'un autre adulte → **corps correct** sur la console. C'est le **test matériel** qui a tranché entre les deux hypothèses.

> 🟢 **Pour tous** — Morale : **un champ qui ressemble à un index n'en est pas forcément un.** On ne fait confiance qu'à ce qui est **confirmé** (ici par tamasprite + flash sur la console).

### 22.6 Comment on a localisé les positions yeux/bouche (`0x167C70`)
C'est l'enquête la plus récente, en plusieurs déductions enchaînées :
1. **Symptôme** : après avoir copié les sprites, **les corps sont bons mais les yeux/bouche restent mal placés**. Conclusion logique : la **position** n'est pas dans le sprite, elle est **ailleurs**.
2. **Indice de la communauté** : la doc de GMMan sur les ghosts mentionne des **« composite definitions »** — littéralement *« où placer les sprites quand on dessine le personnage »* — d'une taille de `0x16` octets, stockées « sous forme d'instances ».
3. **Recherche ciblée dans le dump** : en explorant le fichier *Data* de l'archive, on tombe à **`0x167C70`** sur une suite **lisible** de `sprite_id + ox + oy` où les `oy` valent `-33`, `-32`… — exactement les positions verticales attendues. (Ces octets sont visibles dans le dump ; c'est seulement **Ghidra** qui ne les voyait pas, parce que cette zone n'est pas chargée dans le code.)
4. **Confirmation structurelle** : chaque adulte a **exactement 112 couches**, dans le **même ordre** pour tous — trop régulier pour être un hasard. Et les `oy` **varient légèrement d'une frame à l'autre** (`-33`, `-35`, `-37`…), ce qui correspond aux **frames d'animation** (cligner, regarder en haut/bas).
5. **Validation par le calcul** : on a vérifié qu'appliquer le **modèle delta** avec des décalages à 0 produit un firmware **identique octet pour octet** à la méthode « copie complète de HORHOTCHI » (même checksum ARC2, `0x32B91617`). Deux chemins indépendants qui donnent le même résultat = preuve de cohérence.

> 🟢 **Pour tous** — La chaîne de raisonnement : *« les corps sont bons mais pas les yeux »* ⇒ *« la position est ailleurs »* ⇒ *« la doc parle de composite definitions »* ⇒ *« cherchons une table de positions »* ⇒ *« la voilà, et sa régularité (112 couches, variations d'animation) confirme que c'est bien ça »*. Chaque maillon découle du précédent.

### 22.7 Comment on a déduit le fonctionnement des ghosts
1. **La signature** : en scannant le dump, on remarque des blocs où les deux premiers mots se **compensent** (`w0 + w4 = 0`). C'est la signature d'un checksum ghost — elle sert à les **repérer sans liste**.
2. **Le scan a battu les adresses codées en dur** : en remplaçant des adresses fixes par un scan dynamique, on a **découvert 2 ghosts** que l'ancienne méthode ratait. *Leçon : un scan par signature est plus robuste qu'une liste d'adresses figées.*
3. **La déduction « ajout/suppression »** (récente) : pour ajouter un perso, fallait savoir comment la console compte ses ghosts. On a vérifié que les slots vides sont **tout à `0xFF`**, et surtout qu'il **n'existe pas de compteur** dans la save — preuve : un dump avec 7 ghosts a la même valeur (`0`) à l'endroit suspecté qu'un dump… qui n'en dépend pas. **Donc la console énumère probablement par scan.** On a alors **simulé** un ajout (le scan passe de 16 à 17 ghosts) et une suppression (retour à 16). *Reste à confirmer sur matériel* — c'est la prochaine vérif.

> 🟢 **Pour tous** — Pour prouver qu'« il n'y a pas de compteur de ghosts », on a comparé plusieurs consoles : si un nombre quelque part **ne suit pas** le nombre réel de ghosts, alors ce nombre n'est pas le compteur. C'est un raisonnement par **élimination**.

### 22.8 Le rôle décisif de la validation matérielle
> ⭐ **L'exemple le plus parlant.** La doc affirmait que le checksum du bloc version (`0xD49FF8`) était un **garde-fou de démarrage** (« firmware rejeté si invalide »). Mais en regardant un **vrai dump** de la console, on a constaté que **son checksum `0xD49FF8` était invalide… et que la console fonctionnait parfaitement.** Puis un firmware édité, lui aussi avec ce checksum invalide, **a démarré** sur le matériel. Conclusion : **ce checksum n'est PAS vérifié au boot.** La doc se trompait sur ce point.

> 🟢 **Pour tous** — C'est LA leçon centrale : **le matériel a toujours le dernier mot.** Une hypothèse séduisante (« ce checksum doit être vérifié ») peut être fausse. On ne l'a su qu'en **regardant la réalité** plutôt qu'en faisant confiance au texte. C'est pour ça que, partout dans ce guide, on insiste pour **tester sur la console**, et de préférence **sur un seul cas d'abord**.

### 22.9 Les outils du détective (et quand chacun sert)
| Outil | À quoi il sert | Quand l'utiliser |
|---|---|---|
| **Diff de dumps** | repérer quel octet change après une action | localiser un champ de save (langue, points, faim…) |
| **Éditeur hexa** (HxD/ImHex) | « voir » les octets, repérer des motifs (complément, en-têtes) | inspection manuelle, reconnaissance de structures |
| **tamasprite** | afficher/remplacer les sprites par index | comprendre l'apparence, faire le mapping des 6 sprites |
| **CRC RevEng** | retrouver les paramètres d'un CRC à partir de paires connues | craquer un checksum qui n'est pas une simple somme |
| **Python** | tester une hypothèse de checksum/structure en masse | valider une formule sur plusieurs fichiers, forger une preuve |
| **Ghidra** | lire le code du moteur (désassemblage) | partir d'une **chaîne de texte** et tracer le code |
| **SWD** (debug live) | lire/écrire la mémoire en direct, pas-à-pas | les énigmes que le statique ne résout pas (tables à adressage calculé) |
| **Le matériel** | l'arbitre final | **toujours**, pour confirmer une hypothèse |
| **Recherche publique** (GMMan) | la base de départ (formats, chiffrement, pins) | avant de réinventer la roue — on part de l'existant |

> 🟢 **Pour tous — pourquoi Ghidra n'a pas tout résolu.** Ghidra lit le **code**, mais les **tables de données** (comme les positions à `0x167C70`) sont rangées **trop loin** dans la flash pour être chargées avec le code, et le programme y accède par **calcul** (et non par une adresse écrite en dur). Du coup, Ghidra ne « voit » pas le lien. C'est exactement le genre de cas où le **diff de dumps** et le **debug live (SWD)** sont bien plus efficaces que l'analyse de code.

### 22.10 Les leçons transférables (à emporter partout)
1. **Diff d'abord** : les différences minimales entre deux fichiers révèlent ce qui compte.
2. **Hypothèse la plus simple d'abord** : une **somme** avant un CRC ; un sens littéral avant une indirection compliquée.
3. **Un complément à côté d'une valeur = un checksum** presque à coup sûr.
4. **Forge une preuve** : si ta formule permet de transformer un fichier en un autre **valide**, tu as raison.
5. **Valide sur plusieurs données**, pas une seule.
6. **Le matériel a le dernier mot** : la doc peut se tromper (cf. `0xD49FF8`).
7. **Teste les changements risqués sur UN seul cas** avant de généraliser.
8. **Un champ qui ressemble à un index n'en est pas forcément un** (piège `+0x04`).
9. **Un scan par signature** est plus robuste qu'une liste d'adresses figées.
10. **Pars de la recherche publique** existante, puis vérifie-la toi-même.

> 🟢 **En une phrase** — Tout ce guide a été construit en **observant, supposant, testant, et en croyant le matériel plutôt que les certitudes**. C'est une méthode que tu peux appliquer à n'importe quel appareil, pas seulement à la Tamagotchi.


---

> **Fin du guide.** Tu as maintenant la chaîne complète : *lire la puce → comprendre la carte mémoire → modifier la bonne zone → recalculer le bon checksum → réécrire la puce → vérifier sur la console.* Tout le reste n'est que variation sur ce thème. Bon hacking ! 🎮
