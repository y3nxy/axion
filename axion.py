import os
import sys
import shutil
import subprocess
import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# --- ROOT INITIALIZATION ---
# If the path is "UNDEFINED", it triggers the setup prompt once.
AXION_BASE_STR = "UNDEFINED" # AXION_ROOT_WATCHED

if AXION_BASE_STR == "UNDEFINED":
    print("\033[0;32m[First Time Setup]\033[0m")
    choice = input("Enter the full path where you want to plant the Axion file system: ").strip()
    if not choice:
        choice = str(Path.home() / "Documents" / "axion-files")
    
    AXION_BASE = Path(choice).resolve()
    if not AXION_BASE.exists():
        AXION_BASE.mkdir(parents=True)
    
    # Self-modify the script to save the path permanently
    try:
        script_path = Path(__file__).resolve()
        content = script_path.read_text(encoding='utf-8')
        new_content = content.replace('AXION_BASE_STR = "UNDEFINED" # AXION_ROOT_WATCHED', f'AXION_BASE_STR = r"{choice}" # AXION_ROOT_WATCHED')
        script_path.write_text(new_content, encoding='utf-8')
        print(f"File system planted at: {choice}")
    except Exception as e:
        print(f"Error saving path: {e}")
else:
    AXION_BASE = Path(AXION_BASE_STR)

CUSTOM_USER = "user" # THIS_LINE_IS_WATCHED

current_working_dir = AXION_BASE

ANSI_RED = "\033[38;2;128;0;0m"
ANSI_LINK_RED = "\033[38;2;165;1;4m"
ANSI_GREEN = "\033[0;32m"
ANSI_DARK_GREEN = "\033[38;2;0;100;0m"
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

def update_self_username(new_name):
    try:
        script_path = Path(__file__).resolve()
        with open(script_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        with open(script_path, 'w', encoding='utf-8') as f:
            for line in lines:
                if line.strip().startswith('CUSTOM_USER = "') and "# THIS_LINE_IS_WATCHED" in line:
                    f.write(f'CUSTOM_USER = "{new_name}" # THIS_LINE_IS_WATCHED\n')
                else:
                    f.write(line)
    except Exception as e: 
        print(f"Error updating name: {e}")

def restart_script():
    os.system('clear' if os.name == 'posix' else 'cls')
    os.execv(sys.executable, [sys.executable] + sys.argv)

def get_prompt():
    try:
        path_str = str(current_working_dir.relative_to(AXION_BASE)).replace("\\", "/")
        display_user = CUSTOM_USER if path_str == "." else f"{CUSTOM_USER}/{path_str}"
    except: display_user = f"{CUSTOM_USER}{current_working_dir}"
    return f"{ANSI_GREEN}@{display_user} ➜ /{ANSI_RESET} "

def ls():
    try:
        for item in sorted(os.listdir(current_working_dir)):
            p = current_working_dir / item
            print(f"{ANSI_BLUE}{item}{ANSI_RESET}" if p.is_dir() else item)
    except Exception as e: print(f"error: {e}")

def cd(path_str):
    global current_working_dir
    try:
        if path_str == "/": current_working_dir = AXION_BASE; return
        t = (current_working_dir / path_str).resolve()
        if AXION_BASE in t.parents or t == AXION_BASE:
            if t.is_dir(): current_working_dir = t
            else: print("error: Not a directory")
        else: print("error: Access denied")
    except Exception as e: print(f"error: {e}")

def python_exec(args):
    try:
        if not args: return
        f = (current_working_dir / args[0]).resolve()
        if not f.exists(): print(f"error: {args[0]} not found"); return
        subprocess.run([sys.executable, str(f)] + args[1:])
    except Exception as e: print(f"error: {e}")

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
    print("  time               - print exact time and date")
    print("  whoami             - print current user")
    print("  myname <user>      - change display user (permanent)")
    print("  refresh            - restart terminal")
    print("  clear              - clear screen")
    print("  help               - show this help")
    print("  exit, quit         - exit shell")

def run_line(line):
    global CUSTOM_USER
    for cmd in [c.strip().split() for c in line.split("&")]:
        if not cmd: continue
        c = cmd[0]
        if c == "ls": ls()
        elif c == "cd": cd(cmd[1]) if len(cmd) > 1 else cd("/")
        elif c == "mv" or c == "rname": 
            if len(cmd) > 2: shutil.move(str(current_working_dir/cmd[1]), str(current_working_dir/cmd[2]))
        elif c == "cp":
            if len(cmd) > 2:
                s, d = current_working_dir/cmd[1], current_working_dir/cmd[2]
                shutil.copytree(s, d) if s.is_dir() else shutil.copy2(s, d)
        elif c == "cat": print((current_working_dir/cmd[1]).read_text(encoding="utf-8")) if len(cmd) > 1 else None
        elif c == "mkdir": (current_working_dir/cmd[1]).mkdir(parents=True, exist_ok=True) if len(cmd) > 1 else None
        elif c == "mfile": (current_working_dir/cmd[1]).touch() if len(cmd) > 1 else None
        elif c == "notepad": subprocess.Popen(["notepad.exe", str(current_working_dir/cmd[1])]) if len(cmd) > 1 else None
        elif c == "rm": 
            if len(cmd) > 1:
                t = current_working_dir/cmd[1]
                shutil.rmtree(t) if t.is_dir() else t.unlink()
        elif c == "python": python_exec(cmd[1:])
        elif c == "time": print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        elif c == "whoami": print(CUSTOM_USER)
        elif c == "refresh": restart_script()
        elif c == "help": show_help()
        elif c == "myname":
            if len(cmd) > 1: 
                CUSTOM_USER = cmd[1]
                update_self_username(CUSTOM_USER)
        elif c == "clear": os.system('clear' if os.name == 'posix' else 'cls')
        elif c in ["exit", "quit"]: raise SystemExit
        else: print(f"unknown command: {c}")

def shell():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"{ANSI_RED}{BANNER}{ANSI_RESET}")
    print(f"{ANSI_LINK_RED}Axion File Manager linked to: {AXION_BASE}{ANSI_RESET}")

    # Ensure config.ix exists
    config_file = AXION_BASE / "config.ix"
    if not config_file.exists():
        config_file.touch()

    # Silent auto-run from config.ix
    try:
        auto_commands = [l.strip() for l in config_file.read_text(encoding="utf-8").splitlines() if l.strip()]
        for cmd_line in auto_commands:
            with open(os.devnull, 'w') as fnull:
                old_stdout = sys.stdout
                sys.stdout = fnull
                try:
                    run_line(cmd_line)
                finally:
                    sys.stdout = old_stdout
    except:
        pass

    while True:
        try:
            line = input(get_prompt()).strip()
            if line: run_line(line)
        except (EOFError, KeyboardInterrupt, SystemExit): break

if __name__ == "__main__":
    shell()
