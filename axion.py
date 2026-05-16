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

AXION_BASE_STR = r"C:\\Users\\y3np3\\axion\\axion-file"  # AXION_ROOT_WATCH

if AXION_BASE_STR == "UNDEFINED":
    repo_root = Path(__file__).resolve().parent
    AXION_BASE = repo_root / "axion-file"
    
    if not AXION_BASE.exists():
        AXION_BASE.mkdir(parents=True, exist_ok=True)
    
    try:
        script_path = Path(__file__).resolve()
        content = script_path.read_text(encoding="utf-8")

        safe_path_str = str(AXION_BASE).replace("\\", "\\\\")

        new_content = content.replace(
            'AXION_BASE_STR = r"C:\\Users\\y3np3\\axion\\axion-file"  # AXION_ROOT_WATCH',
            f'AXION_BASE_STR = r"{safe_path_str}"  # AXION_ROOT_WATCH'
        )

        script_path.write_text(new_content, encoding="utf-8")
        print(f"\033[0;32m[First Time Setup]\033[0m")
        print(f"File system sandbox automatically isolated at: {AXION_BASE}")

    except Exception as e:
        print(f"Error saving path: {e}")
else:
    AXION_BASE = Path(AXION_BASE_STR).resolve()

SETTINGS_DIR = AXION_BASE / "settings"
SETTINGS_DIR.mkdir(exist_ok=True)

CONFIG_FILE = SETTINGS_DIR / "config.ix"
if not CONFIG_FILE.exists():
    CONFIG_FILE.write_text("# This file automatically executes Axion shell commands sequentially on startup.\n", encoding="utf-8")

USERNAME_FILE = SETTINGS_DIR / "username.ix"
if not USERNAME_FILE.exists():
    USERNAME_FILE.write_text("user", encoding="utf-8")

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
| █████╗ ██╗  ██╗██╗ ██████╗ ███╗   ██╗          █████╗   ██████╗ |
|██╔══██╗╚██╗██╔╝██║██╔═══██╗████╗  ██║         ██╔═══██╗██╔════╝ |
|███████║ ╚███╔╝ ██║██║   ██║██╔██╗ ██║ █████╗ ██║   ██║███████║ |
|██╔══██║ ██╔██╗ ██║██║   ██║██║╚██╗██║ ╚════- ██║   ██║╚════██║ |
|██║  ██║██╔╝ ██╗██║╚██████╔╝██║ ╚████║        ╚██████╔╝███████║ |
|╚═╝  ╚═╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝         ╚═════╝ ╚══════╝ |
'----------------------------------------------------------------'"""

COMMANDS = [
    "ls", "cd", "mv", "rname", "cp", "cat",
    "mkdir", "rm", "mfile", "notepad",
    "python", "time", "whoami", "refresh",
    "help", "myname", "clear", "exit", "quit"
]

def show_help():
    print("Available commands:")
    print("  ls                 - list files")
    print("  cd <dir>           - change directory")
    print("  mv <src> <dest>    - move/rename")
    print("  rname <src> <dest> - rename")
    print("  cp <src> <dest>    - copy")
    print("  cat <file>         - show contents")
    print("  mkdir <dir>        - create directory")
    print("  rm <path>          - remove file/dir")
    print("  mfile <file>       - create empty file")
    print("  notepad <file>     - edit file in Notepad")
    print("  python <args>      - run python")
    print("  time               - print date/time")
    print("  whoami             - show user")
    print("  myname <user>      - change username")
    print("  clear              - clear screen")
    print("  help               - show this help")
    print("  exit / quit        - exit shell")

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
            elif item in ["config.ix", "username.ix"]:
                print(f"{ANSI_DARK_BLUE}{item}{ANSI_RESET}")
            else:
                print(item)
    except Exception as e:
        print(f"error: {e}")

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
        if not parts.strip():
            continue
        
        try:
            cmd = shlex.split(parts)
        except Exception as e:
            print(f"lexical error: {e}")
            continue

        if not cmd:
            continue

        c = cmd[0]

        try:
            if c == "ls":
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
            # Clear everything completely before returning to the normal terminal layout
            os.system("cls" if os.name == "nt" else "clear")
            break

if __name__ == "__main__":
    shell()
