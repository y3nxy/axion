# 🧠 Axion File Manager

A lightweight, Python-based terminal file manager that simulates a mini shell environment inside a sandboxed directory.

---

## 🚀 Overview

**Axion File Manager** is a custom command-line interface (CLI) built in Python that allows users to manage files and directories safely within a restricted workspace.

* 📁 Sandboxed file system (`~/Documents/axion-files`)
* 🖥️ Custom shell experience
* ⚡ Built-in commands for file operations
* 🔒 Protection against directory escape
* 🧩 Extensible and hackable

---

## 📦 Features

### 🗂️ File Management

* Create, delete, move, copy files and directories
* View file contents
* Rename files

### 📁 Directory Navigation

* Change directories within sandbox
* Prevent access outside base directory

### 🐍 Python Execution

* Run Python scripts directly from the shell

### 👤 User Identity

* Custom username display
* Persistent username (stored in script)

### 🖥️ Shell Experience

* Command chaining using `&`
* Colored output for better readability
* Clear screen and refresh support

### ⏱️ Utilities

* Show current date and time
* Display current user

---

## 🛠️ Installation

```bash
git clone https://github.com/your-username/axion-file-manager.git
cd axion-file-manager
python main.py
```

---

## 📂 Default Workspace

All operations are restricted to:

```
~/Documents/axion-files
```

This ensures safe file handling without affecting your system.

---

## 📜 Available Commands

| Command              | Description                 |
| -------------------- | --------------------------- |
| `ls`                 | List files and directories  |
| `cd <dir>`           | Change directory            |
| `cd /`               | Go to root workspace        |
| `mv <src> <dest>`    | Move file/directory         |
| `rname <src> <dest>` | Rename file                 |
| `cp <src> <dest>`    | Copy file/directory         |
| `cat <file>`         | Show file contents          |
| `mkdir <dir>`        | Create directory            |
| `mfile <file>`       | Create empty file           |
| `rm <path>`          | Remove file/directory       |
| `notepad <file>`     | Open file in Notepad        |
| `python <file>`      | Run Python script           |
| `time`               | Show current date & time    |
| `whoami`             | Show current username       |
| `myname <name>`      | Change username permanently |
| `clear`              | Clear terminal              |
| `refresh`            | Restart shell               |
| `help`               | Show help menu              |
| `exit` / `quit`      | Exit program                |

---

## 🔗 Command Chaining

Run multiple commands in one line using `&`:

```bash
mkdir test & cd test & mfile hello.txt
```

---

## 🔒 Security

* Prevents navigation outside sandbox directory
* Uses path validation to restrict access
* Safe environment for experimentation

---

## 🎨 UI Features

* Colored directory output
* Custom prompt:

  ```
  @user ➜ /
  ```
* ASCII banner on startup

---

## ⚠️ Limitations

* `notepad` command is Windows-only
* No confirmation prompt for `rm` (use carefully)
* Basic error handling
* No tab completion or history

---

## 💡 Future Improvements

* Cross-platform editor support
* Command history & autocomplete
* Safer delete (confirmation prompts)
* Plugin system
* GUI version

---

## 🤝 Contributing

Feel free to fork this project and submit pull requests to improve functionality.

---

## 📄 License

MIT License

---

## 👨‍💻 Author

Developed as a custom Python shell environment experiment.
