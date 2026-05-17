import os
import sys
import shutil
import subprocess
import datetime
import shlex
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import ANSI

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

repo_root = Path(__file__).resolve().parent
AXION_BASE = repo_root / "axion-file"

if not AXION_BASE.exists():
    AXION_BASE.mkdir(parents=True, exist_ok=True)

SETTINGS_DIR = AXION_BASE / "settings"
SETTINGS_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = SETTINGS_DIR / "config.ix"
if not CONFIG_FILE.exists():
    CONFIG_FILE.write_text("", encoding="utf-8")

USERNAME_FILE = SETTINGS_DIR / "username.ix"
if not USERNAME_FILE.exists():
    USERNAME_FILE.write_text("user", encoding="utf-8")

SHORTCUTS_FILE = SETTINGS_DIR / "shortcuts.ix"
if not SHORTCUTS_FILE.exists():
    SHORTCUTS_FILE.write_text("", encoding="utf-8")

try:
    CUSTOM_USER = USERNAME_FILE.read_text(encoding="utf-8").strip()
    if not CUSTOM_USER:
        CUSTOM_USER = "user"
except Exception:
    CUSTOM_USER = "user"

current_working_dir = AXION_BASE

ANSI_RED = "\033[38;2;128;0;0m"
ANSI_LINK_RED = "\033[38;2;165;1;4m"
ANSI_GREEN = "\033[0;32m"
ANSI_BLUE = "\033[38;2;41;110;180m"
ANSI_DARK_BLUE = "\033[38;2;0;0;139m"
ANSI_PURPLE = "\033[38;2;125;83;222m"
ANSI_RESET = "\033[0m"

BANNER = r""".----------------------------------------------------------------.
| █████╗ ██╗  ██╗██╗ ██████╗ ███╗   ██╗         █████╗   ██████╗ |
|██╔══██╗╚██╗██╔╝██║██╔═══██╗████╗  ██║        ██╔═══██╗██╔════╝ |
|███████║ ╚███╔╝ ██║██║   ██║██╔██╗ ██║ █████╗ ██║   ██║███████║ |
|██╔══██║ ██╔██╗ ██║██║   ██║██║╚██╗██║ ╚════- ██║   ██║╚════██║ |
|██║  ██║██╔╝ ██╗██║╚██████╔╝██║ ╚████║        ╚██████╔╝███████║ |
|╚═╝  ╚═╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝         ╚═════╝ ╚══════╝ |
'----------------------------------------------------------------'"""

def load_shortcuts():
    shortcuts = {}
    if SHORTCUTS_FILE.exists():
        for line in SHORTCUTS_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                alias, _, target = line.partition("=")
                shortcuts[alias.strip()] = target.strip()
    return shortcuts

def save_shortcut(alias, target):
    shortcuts = load_shortcuts()
    shortcuts[alias] = target
    lines = [f"{k}={v}" for k, v in shortcuts.items()]
    SHORTCUTS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

def remove_shortcut(alias):
    shortcuts = load_shortcuts()
    if alias in shortcuts:
        del shortcuts[alias]
        lines = [f"{k}={v}" for k, v in shortcuts.items()]
        if lines:
            SHORTCUTS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
        else:
            SHORTCUTS_FILE.write_text("", encoding="utf-8")
        return True
    return False

def show_help():
    print("Available commands:")
    print("  ls                        - list files (use 'ls scut' to list aliases)")
    print("  cd <dir>                  - change directory")
    print("  mv <src> <dest>           - move/rename")
    print("  rname <src> <dest>        - rename")
    print("  cp <src> <dest>           - copy")
    print("  cat <file>                - show contents")
    print("  mkdir <dir>               - create directory")
    print("  rm <path>                 - remove file/dir")
    print("  mfile <file>              - create empty file")
    print("  notepad <file>            - edit file in Notepad")
    print("  newline <file> <txt>      - append text with a new line")
    print("  newup <file> <txt>        - append text directly without new line")
    print("  rplace <file> <txt>       - clear file and replace with new text")
    print("  empty <file>              - clear all contents of a file")
    print("  delline <file> <ln>       - delete a specific line and collapse the gap")
    print("  rpline <file> <ln> <txt>  - replace a specific line with new text")
    print("  scut <alias> <cmd>        - map a custom command shortcut alias")
    print("  rmscut <alias>            - remove an existing command shortcut alias")
    print("  python <args>             - run python")
    print("  time                      - print date/time")
    print("  whoami                    - show user")
    print("  myname <user>             - change username")
    print("  clear                     - clear screen")
    print("  help                      - show this help")
    print("  exit / quit               - exit shell")

def update_self_username(new_name):
    try:
        USERNAME_FILE.write_text(new_name, encoding="utf-8")
    except Exception as e:
        print(f"Error updating username file: {e}")

def restart_script():
    os.system("cls" if os.name == "nt" else "clear")
    os.execv(sys.executable, [sys.executable] + sys.argv)

def get_prompt():
    global CUSTOM_USER
    try:
        CUSTOM_USER = USERNAME_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        CUSTOM_USER = "user"

    try:
        path_str = str(current_working_dir.relative_to(AXION_BASE)).replace("\\", "/")
        display_user = CUSTOM_USER if path_str == "." else f"{CUSTOM_USER}/{path_str}"
    except Exception:
        display_user = f"{CUSTOM_USER}{current_working_dir}"

    return f"{ANSI_GREEN}@{display_user} ➜ /{ANSI_RESET} "

def resolve_path(path_str: str) -> Path:
    if path_str == "/":
        return AXION_BASE

    target = (current_working_dir / path_str).resolve()

    if AXION_BASE in target.parents or target == AXION_BASE:
        return target
    else:
        raise PermissionError("Access denied: Cannot leave root sandbox.")

def ls():
    try:
        for item in sorted(os.listdir(current_working_dir)):
            p = current_working_dir / item
            if item == "settings":
                print(f"{ANSI_PURPLE}{item}{ANSI_RESET}")
            elif p.is_dir():
                print(f"{ANSI_BLUE}{item}{ANSI_RESET}")
            elif item in ["config.ix", "username.ix", "shortcuts.ix"]:
                print(f"{ANSI_DARK_BLUE}{item}{ANSI_RESET}")
            else:
                print(item)
    except Exception as e:
        print(f"error: {e}")

def ls_scut():
    shortcuts = load_shortcuts()
    if not shortcuts:
        print("No command aliases found.")
        return
    print("Active Command Aliases:")
    for alias, target in shortcuts.items():
        print(f"  {alias} -> {target}")

def cd(path_str):
    global current_working_dir
    try:
        t = resolve_path(path_str)
        if t.is_dir():
            current_working_dir = t
        else:
            print("error: Not a directory")
    except PermissionError as pe:
        print(f"error: {pe}")
    except Exception as e:
        print(f"error: {e}")

def python_exec(args):
    if not args:
        return
    try:
        f = resolve_path(args[0])
        if not f.exists():
            print(f"error: {args[0]} not found")
            return
        subprocess.run([sys.executable, str(f)] + args[1:])
    except Exception as e:
        print(f"error: {e}")

def run_line(line):
    global CUSTOM_USER

    for parts in line.split("&"):
        raw_part = parts.strip()
        if not raw_part:
            continue

        try:
            cmd = shlex.split(raw_part)
        except Exception as e:
            print(f"lexical error: {e}")
            continue

        if not cmd:
            continue

        c = cmd[0]

        shortcuts = load_shortcuts()
        if c in shortcuts:
            alias_target = shortcuts[c]
            try:
                translated_cmd = shlex.split(alias_target) + cmd[1:]
                cmd = translated_cmd
                c = cmd[0]
            except Exception:
                pass

        try:
            if c == "ls":
                if len(cmd) > 1 and cmd[1] == "scut":
                    ls_scut()
                else:
                    ls()

            elif c == "cd":
                cd(cmd[1]) if len(cmd) > 1 else cd("/")

            elif c in ["mv", "rname"]:
                if len(cmd) > 2:
                    s = resolve_path(cmd[1])
                    d = resolve_path(cmd[2])
                    shutil.move(str(s), str(d))
                else:
                    print(f"error: {c} requires source and destination arguments")

            elif c == "cp":
                if len(cmd) > 2:
                    s = resolve_path(cmd[1])
                    d = resolve_path(cmd[2])
                    if s.is_dir():
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
                else:
                    print("error: cp requires source and destination arguments")

            elif c == "cat":
                if len(cmd) > 1:
                    f = resolve_path(cmd[1])
                    print(f.read_text(encoding="utf-8"))
                else:
                    print("error: cat requires a file target")

            elif c == "mkdir":
                if len(cmd) > 1:
                    d = resolve_path(cmd[1])
                    d.mkdir(parents=True, exist_ok=True)
                else:
                    print("error: mkdir requires a target name")

            elif c == "mfile":
                if len(cmd) > 1:
                    f = resolve_path(cmd[1])
                    f.touch()
                else:
                    print("error: mfile requires a filename")

            elif c == "notepad":
                if len(cmd) > 1:
                    f = resolve_path(cmd[1])
                    subprocess.Popen(["notepad.exe", str(f)]) if os.name == "nt" else print("error: Notepad is only available on Windows")
                else:
                    print("error: notepad requires a filename")

            elif c == "newline":
                if len(cmd) > 2:
                    f = resolve_path(cmd[1])
                    prefix_len = raw_part.find(cmd[1]) + len(cmd[1])
                    text_to_append = raw_part[prefix_len:].strip()

                    with open(f, "a", encoding="utf-8") as file_obj:
                        if f.exists() and f.stat().st_size > 0:
                            with open(f, "rb") as check_file:
                                check_file.seek(-1, os.SEEK_END)
                                last_char = check_file.read(1)

                            if last_char != b"\n":
                                file_obj.write("\n")

                        file_obj.write(text_to_append + "\n")
                else:
                    print("error: newline requires a filename and a text string")

            elif c == "newup":
                if len(cmd) > 2:
                    f = resolve_path(cmd[1])
                    prefix_len = raw_part.find(cmd[1]) + len(cmd[1])
                    text_to_append = raw_part[prefix_len:].strip()

                    with open(f, "a", encoding="utf-8") as file_obj:
                        file_obj.write(text_to_append)
                else:
                    print("error: newup requires a filename and a text string")

            elif c == "rplace":
                if len(cmd) > 1:
                    f = resolve_path(cmd[1])

                    if len(cmd) > 2:
                        prefix_len = raw_part.find(cmd[1]) + len(cmd[1])
                        text_to_write = raw_part[prefix_len:].strip()
                    else:
                        text_to_write = ""

                    with open(f, "w", encoding="utf-8") as file_obj:
                        file_obj.write(text_to_write)
                else:
                    print("error: rplace requires a filename argument")

            elif c == "empty":
                if len(cmd) > 1:
                    f = resolve_path(cmd[1])

                    with open(f, "w", encoding="utf-8") as file_obj:
                        pass
                else:
                    print("error: empty requires a filename target")

            elif c == "delline":
                if len(cmd) > 2:
                    f = resolve_path(cmd[1])

                    try:
                        line_idx = int(cmd[2]) - 1

                        if line_idx < 0:
                            print("error: Line number must be 1 or greater")
                            continue

                    except ValueError:
                        print("error: Line number must be an integer")
                        continue

                    if not f.exists():
                        print(f"error: {cmd[1]} not found")
                        continue

                    lines = f.read_text(encoding="utf-8").splitlines()

                    if line_idx < len(lines):
                        lines.pop(line_idx)

                        if lines:
                            f.write_text("\n".join(lines) + "\n", encoding="utf-8")
                        else:
                            f.write_text("", encoding="utf-8")
                    else:
                        print(f"error: File only has {len(lines)} lines. Line {cmd[2]} doesn't exist.")
                else:
                    print("error: delline requires a filename and a line number")

            elif c == "rpline":
                if len(cmd) > 3:
                    f = resolve_path(cmd[1])

                    try:
                        line_idx = int(cmd[2]) - 1

                        if line_idx < 0:
                            print("error: Line number must be 1 or greater")
                            continue

                    except ValueError:
                        print("error: Line number must be an integer")
                        continue

                    if not f.exists():
                        print(f"error: {cmd[1]} not found")
                        continue

                    lines = f.read_text(encoding="utf-8").splitlines()

                    if line_idx < len(lines):
                        line_num_str = cmd[2]
                        file_pos = raw_part.find(cmd[1])
                        search_start = file_pos + len(cmd[1])
                        line_num_pos = raw_part.find(line_num_str, search_start)
                        prefix_len = line_num_pos + len(line_num_str)
                        
                        new_text = raw_part[prefix_len:].strip()
                        lines[line_idx] = new_text

                        f.write_text("\n".join(lines) + "\n", encoding="utf-8")
                    else:
                        print(f"error: File only has {len(lines)} lines. Line {cmd[2]} doesn't exist.")
                else:
                    print("error: rpline requires a filename, line number, and text")

            elif c == "scut":
                if len(cmd) > 2:
                    alias_name = cmd[1]
                    alias_pos = raw_part.find(alias_name)
                    target_command = raw_part[alias_pos + len(alias_name):].strip()
                    
                    save_shortcut(alias_name, target_command)
                else:
                    print("error: scut requires an alias name and a target command mapping")

            elif c == "rmscut":
                if len(cmd) > 1:
                    alias_name = cmd[1]
                    if remove_shortcut(alias_name):
                        pass
                    else:
                        print(f"error: alias '{alias_name}' not found")
                else:
                    print("error: rmscut requires an alias name string")

            elif c == "rm":
                if len(cmd) > 1:
                    t = resolve_path(cmd[1])

                    if t.is_dir():
                        shutil.rmtree(t)
                    else:
                        t.unlink()
                else:
                    print("error: rm requires a target")

            elif c == "python":
                python_exec(cmd[1:])

            elif c == "time":
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            elif c == "whoami":
                try:
                    CUSTOM_USER = USERNAME_FILE.read_text(encoding="utf-8").strip()
                except Exception:
                    pass

                print(CUSTOM_USER)

            elif c == "refresh":
                restart_script()

            elif c == "clear":
                os.system("cls" if os.name == "nt" else "clear")

            elif c == "myname":
                if len(cmd) > 1:
                    CUSTOM_USER = cmd[1]
                    update_self_username(CUSTOM_USER)
                else:
                    print("error: myname requires a username string")

            elif c == "help":
                show_help()

            elif c in ["exit", "quit"]:
                raise SystemExit

            else:
                print(f"unknown command: {c}")

        except PermissionError as pe:
            print(f"security error: {pe}")
        except Exception as e:
            print(f"error processing command '{c}': {e}")

def shell():
    os.system("cls" if os.name == "nt" else "clear")

    print(f"{ANSI_RED}{BANNER}{ANSI_RESET}")
    print(f"{ANSI_LINK_RED}All credits to @y3nxy in GitHub.{ANSI_RESET}")

    try:
        for cmd_line in CONFIG_FILE.read_text(encoding="utf-8").splitlines():
            if cmd_line.strip() and not cmd_line.strip().startswith("#"):
                run_line(cmd_line)
    except Exception as e:
        print(f"Error loading config.ix: {e}")

    session = PromptSession(auto_suggest=AutoSuggestFromHistory())

    while True:
        try:
            line = session.prompt(
                ANSI(get_prompt())
            ).strip()

            if line:
                run_line(line)

        except (EOFError, KeyboardInterrupt, SystemExit):
            os.system("cls" if os.name == "nt" else "clear")
            break

if __name__ == "__main__":
    shell()
