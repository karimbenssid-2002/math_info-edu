import subprocess
subprocess.check_call(["python", "-m", "pip", "install", "playwright"])
subprocess.check_call(["python", "-m", "playwright", "install", "chromium"])
