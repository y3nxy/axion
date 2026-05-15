import os
import sys
import shutil
import subprocess
import datetime
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import NestedCompleter, PathCompleter
from prompt_toolkit.formatted_text import ANSI

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# --- ROOT INITIALIZATION ---
AXION_BASE_STR = r"desktop"  # AXION_ROOT_WATCHED

if AXION_BASE_STR == "UNDEFINED":
    print("\033[0;32m[First Time Setup]\033[0m")
    choice = input("Enter full path for Axion file system: ").strip()

    if not choice:
        choice = str(Path.home() / "Documents" / "axion-files")

    AXION_BASE = Path(choice).resolve()

    if not AXION_BASE.exists():
        AXION_BASE.mkdir(parents=True)

    try:
        script_path = Path(__file__).resolve()
        content = script_path.read_text(encoding="utf-8")

        new_content = content.replace(
            'AXION_BASE_STR = r"desktop"  # AXION_ROOT_WATCHED',
            f'AXION_BASE_STR = r"{choice}"  # AXION_ROOT_WATCHED'
        )

        script_path.write_text(new_content, encoding="utf-8")
        print(f"File system planted at: {choice}")

    except Exception as e:
        print(f"Error saving path: {e}")

else:
    AXION_BASE = Path(AXION_BASE_STR)

CUSTOM_USER = "user"  # THIS_LINE_IS_WATCHED
current_working_dir = AXION_BASE

ANSI_RED = "\033[38;2;128;0;0m"
ANSI_LINK_RED = "\033[38;2;165;1;4m"
ANSI_GREEN = "\033[0;32m"
ANSI_BLUE = "\033[38;2;41;110;180m"
ANSI_RESET = "\033[0m"

BANNER = r""".----------------------------------------------------------------.
| █████╗ ██╗  ██╗██╗ ██████╗ ███╗   ██╗         █████╗   ██████╗ |
|██╔══██╗╚██╗██╔╝██║██╔═══██╗████╗  ██║        ██╔═══██╗██╔════╝ |
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

# --- COMPLETER (commands + files) ---
def completer(text, state):
    buffer = readline_buffer.get("")

    try:
        parts = buffer.split()

        if len(parts) <= 1:
            matches = [c for c in COMMANDS if c.startswith(text)]
        else:
            matches = [
                p.name + ("/" if p.is_dir() else "")
                for p in current_working_dir.iterdir()
                if p.name.startswith(text)
            ]

        return matches[state]

    except:
        return None

def update_self_username(new_name):
    try:
        script_path = Path(__file__).resolve()
        lines = script_path.read_text(encoding="utf-8").splitlines(True)

        with script_path.open("w", encoding="utf-8") as f:
            for line in lines:
                if line.strip().startswith('CUSTOM_USER = "') and "# THIS_LINE_IS_WATCHED" in line:
                    f.write(f'CUSTOM_USER = "{new_name}"  # THIS_LINE_IS_WATCHED\n')
                else:
                    f.write(line)
    except Exception as e:
        print(f"Error updating name: {e}")

def restart_script():
    os.system("cls" if os.name == "nt" else "clear")
    os.execv(sys.executable, [sys.executable] + sys.argv)

def get_prompt():
    try:
        path_str = str(current_working_dir.relative_to(AXION_BASE)).replace("\\", "/")
        display_user = CUSTOM_USER if path_str == "." else f"{CUSTOM_USER}/{path_str}"
    except:
        display_user = f"{CUSTOM_USER}{current_working_dir}"

    return f"{ANSI_GREEN}@{display_user} ➜ /{ANSI_RESET} "

def ls():
    for item in sorted(os.listdir(current_working_dir)):
        p = current_working_dir / item
        print(f"{ANSI_BLUE}{item}{ANSI_RESET}" if p.is_dir() else item)

def cd(path_str):
    global current_working_dir

    if path_str == "/":
        current_working_dir = AXION_BASE
        return

    t = (current_working_dir / path_str).resolve()

    if AXION_BASE in t.parents or t == AXION_BASE:
        if t.is_dir():
            current_working_dir = t
        else:
            print("error: Not a directory")
    else:
        print("error: Access denied")

def python_exec(args):
    if not args:
        return

    f = (current_working_dir / args[0]).resolve()

    if not f.exists():
        print(f"error: {args[0]} not found")
        return

    subprocess.run([sys.executable, str(f)] + args[1:])

def run_line(line):
    global CUSTOM_USER

    for cmd in [c.strip().split() for c in line.split("&")]:
        if not cmd:
            continue

        c = cmd[0]

        if c == "ls":
            ls()

        elif c == "cd":
            cd(cmd[1]) if len(cmd) > 1 else cd("/")

        elif c in ["mv", "rname"]:
            if len(cmd) > 2:
                shutil.move(str(current_working_dir/cmd[1]),
                            str(current_working_dir/cmd[2]))

        elif c == "cp":
            if len(cmd) > 2:
                s, d = current_working_dir/cmd[1], current_working_dir/cmd[2]
                shutil.copytree(s, d) if s.is_dir() else shutil.copy2(s, d)

        elif c == "cat":
            print((current_working_dir/cmd[1]).read_text(encoding="utf-8")) if len(cmd) > 1 else None

        elif c == "mkdir":
            (current_working_dir/cmd[1]).mkdir(parents=True, exist_ok=True) if len(cmd) > 1 else None

        elif c == "mfile":
            (current_working_dir/cmd[1]).touch() if len(cmd) > 1 else None

        elif c == "notepad":
            subprocess.Popen(["notepad.exe", str(current_working_dir/cmd[1])]) if len(cmd) > 1 else None

        elif c == "rm":
            if len(cmd) > 1:
                t = current_working_dir/cmd[1]
                shutil.rmtree(t) if t.is_dir() else t.unlink()

        elif c == "python":
            python_exec(cmd[1:])

        elif c == "time":
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        elif c == "whoami":
            print(CUSTOM_USER)

        elif c == "refresh":
            restart_script()

        elif c == "clear":
            os.system("cls" if os.name == "nt" else "clear")

        elif c == "myname":
            if len(cmd) > 1:
                CUSTOM_USER = cmd[1]
                update_self_username(CUSTOM_USER)

        elif c in ["exit", "quit"]:
            raise SystemExit

        else:
            print(f"unknown command: {c}")

def shell():
    os.system("cls" if os.name == "nt" else "clear")

    print(f"{ANSI_RED}{BANNER}{ANSI_RESET}")
    print(f"{ANSI_LINK_RED}All credits to @y3nxy in GitHub.{ANSI_RESET}")

    config_file = AXION_BASE / "config.ix"
    config_file.touch(exist_ok=True)

    # auto-run config
    try:
        for cmd_line in config_file.read_text(encoding="utf-8").splitlines():
            if cmd_line.strip():
                run_line(cmd_line)
    except:
        pass

    session = PromptSession(auto_suggest=AutoSuggestFromHistory())

    completer_obj = NestedCompleter.from_nested_dict({
        "ls": None,
        "cd": PathCompleter(),
        "mv": PathCompleter(),
        "rname": PathCompleter(),
        "cp": PathCompleter(),
        "cat": PathCompleter(),
        "mkdir": None,
        "rm": PathCompleter(),
        "mfile": None,
        "notepad": PathCompleter(),
        "python": PathCompleter(),
        "time": None,
        "whoami": None,
        "refresh": None,
        "help": None,
        "myname": None,
        "clear": None,
        "exit": None,
        "quit": None,
    })

    while True:
        try:
            line = session.prompt(
                ANSI(get_prompt()),
                completer=completer_obj,
                complete_while_typing=True
            ).strip()

            if line:
                run_line(line)

        except (EOFError, KeyboardInterrupt, SystemExit):
            break

if __name__ == "__main__":
    shell()
