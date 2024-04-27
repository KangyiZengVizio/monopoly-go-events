# have to introduce a mechnisim to reload to cron tab
import subprocess
import time
def activate_cron():
    execute = subprocess.Popen(["echo", "\033:wq\n"], stdout=subprocess.PIPE)
    activate = subprocess.Popen(["crontab", "-e"], stdin=execute.stdout)
    # Wait for crontab to save
    time.sleep(5)
    activate.kill()

if __name__ == "__main__":
    activate_cron()