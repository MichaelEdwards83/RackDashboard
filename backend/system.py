import subprocess
import os
from config import CONFIG

class SystemManager:
    @staticmethod
    def set_ntp_server(server: str):
        """
        Updates the NTP server in /etc/systemd/timesyncd.conf
        Requires root privileges (application should run as root or have sudoer access for this command)
        """
        # Security Note: Accepting arbitrary string input for subprocess is dangerous.
        # In a real production app, strict validation is required.
        # We will assume 'server' is a valid hostname/IP.
        
        try:
            # Very basic validation
            if ";" in server or "&" in server or "|" in server:
                return False, "Invalid characters in server address"

            conf_content = f"""
[Time]
NTP={server}
FallbackNTP=0.pool.ntp.org 1.pool.ntp.org 2.pool.ntp.org 3.pool.ntp.org
"""
            # We can't easily write to /etc/ directly if not root.
            # Strategy: Write to tmp file then sudo move it.
            tmp_path = "/tmp/timesyncd.conf.tmp"
            with open(tmp_path, "w") as f:
                f.write(conf_content)
            
            # Apply changes
            # 1. Move file
            subprocess.run(["sudo", "mv", tmp_path, "/etc/systemd/timesyncd.conf"], check=True)
            # 2. Restart service
            subprocess.run(["sudo", "systemctl", "restart", "systemd-timesyncd"], check=True)
            
            # Update config
            CONFIG.set("ntp_server", server)
            return True, "NTP configured successfully"
        except subprocess.CalledProcessError as e:
            return False, f"System command failed: {e}"
        except Exception as e:
            return False, f"Error: {e}"

    @staticmethod
    def get_system_time():
        return subprocess.getoutput("date")
