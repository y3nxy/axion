````md
# ⚡ AXION SHELL

this readme contains everything you need to get this thing running and understand what kind of digital creature you just unleashed

---

## 🚀 WHAT THIS IS

a python-powered terminal shell that:
- predicts your commands like it’s reading your mind
- autocompletes files, folders, and commands
- runs like a mini OS inside a script
- remembers your vibe and history
- lowkey feels like zsh got a cybernetic upgrade

---

## 🧠 FEATURES

- command autocomplete (tab magic)
- ghost suggestions (right arrow accept energy)
- file system navigation baked in
- custom command runner
- persistent user identity
- startup scripting via `config.ix`
- clean ANSI colored UI

---

## 📦 INSTALL

```bash
pip install -r requirements.txt
````

---

## ▶️ RUN IT

```bash
python axion.py
```

---

## ⌨️ COMMANDS

### files & folders

* ls
* cd <dir>
* cat <file>
* mkdir <dir>
* rm <path>
* cp <src> <dest>
* mv / rname
* mfile <file>

### system stuff

* time
* clear
* whoami
* myname <name>
* refresh
* exit / quit

### execution

* python <file>

---

## ⚙️ CONFIG MAGIC

`config.ix` runs automatically on launch

put commands inside like:

```
ls
cd test
```

and it just does them instantly like it’s obeying your past self

---

## 📁 STRUCTURE

```
axion.py
config.ix
requirements.txt
```

---

## 🧩 REQUIREMENTS

```
prompt_toolkit>=3.0.0
pyreadline3; sys_platform == "win32"
```

---

## ⚠️ NOTES

* windows needs pyreadline3 or autocomplete breaks
* linux/mac just works naturally
* best experience in modern terminal apps

---
