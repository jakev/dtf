# Android Device Testing Framework ("dtf")
# Copyright 2013-2015 Jake Valletta (@jake_valletta)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Python helper for using `adb`"""


from __future__ import absolute_import
from __future__ import print_function
import os
import os.path
import tempfile
import shutil
from subprocess import Popen, PIPE

from dtf.properties import get_prop
from dtf.constants import DTF_CLIENT

ADB_BINARY = "adb"

STATUS_DEVICE = 'device'
STATUS_OFFLINE = 'offline'
STATUS_BOOTLOADER = 'bootloader'

MODE_USB = 'usb'
MODE_WIFI = 'wifi'


def get_mode_serial():

    """Return the serial dependent on the mode"""

    if get_prop('Client', 'mode') == MODE_USB:
        return get_prop("Info", "serial")
    else:
        return ("%s:%s" % (get_prop('Client', 'ip-addr'),
                           get_prop('Client', 'port')))


# pylint:disable=too-many-public-methods
class DtfAdb(object):

    """Python wrapper class for `adb`"""

    serial = ''
    pre_1_0_36 = False
    no_serial = False
    stdout = None
    stderr = None
    returncode = ''

    def __init__(self, no_serial=False):

        """Object initialization"""

        self.no_serial = no_serial

        if not self.no_serial:

            self.serial = get_mode_serial()

        # Determine if we are the new version of adb
        self.pre_1_0_36 = self.__is_old_adb_version()

    def __is_old_adb_version(self):

        """Determine if adb is the new version"""

        self.__run_command("")

        try:
            version_line = self.get_errors()[0]
            version = version_line.split()[-1]
            split_version = version.split(".")

            if split_version[0] == "1" and split_version[1] == "0":
                if int(split_version[2]) < 36:
                    return True

            return False

        except IndexError:
            return False

    def __run_command(self, in_cmd):

        """Internal function to run `adb` command"""

        if self.no_serial:
            cmd = ("%s %s" % (ADB_BINARY, in_cmd)).split(' ')
        else:
            cmd = ("%s -s %s %s"
                   % (ADB_BINARY, self.serial, in_cmd)).split(' ')

        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False)

        tmp_out = proc.stdout.read().replace("\r", '')
        tmp_err = proc.stderr.read().replace("\r", '')

        self.stdout = tmp_out.split("\n")
        self.stderr = tmp_err.split("\n")

        proc.terminate()

    def get_output(self):

        """Read output stream"""

        return self.stdout

    def get_errors(self):

        """Read error stream"""

        return self.stderr

    def shell_command(self, cmd):

        """Execute a shell command on device"""

        self.__run_command("shell %s" % cmd)

    def wait_for_device(self):

        """Block until device is found"""

        self.__run_command("wait-for-device")

    def get_devices(self):

        """List all connected devices"""

        self.__run_command("devices")

        device_list = list()

        output = self.get_output()

        # Remove the "List of devices..."
        output.pop(0)

        # ...Also the two '' at the end.
        output.pop()
        output.pop()

        if len(output) == 0:
            return device_list

        for device in output:

            try:
                serial, status = device.split('\t')
            except ValueError:
                continue

            device_list.append({'serial': serial, 'status': status})

        return device_list

    def pull(self, file_name, local="./"):

        """Pull file off device"""

        if self.pre_1_0_36:
            self.__run_command("pull %s %s" % (file_name, local))

        else:
            self.__run_command("pull %s %s" % (file_name, local))

    def pull_dir(self, dir_name, local="./"):

        """Pull a directory off device"""

        if self.pre_1_0_36:
            self.__run_command("pull %s %s" % (dir_name, local))

        else:
            temp_pull = tempfile.mkdtemp()
            base = os.path.basename(dir_name.rstrip("/"))

            self.__run_command("pull %s %s" % (dir_name, temp_pull))
            full_tmp = "%s/%s" % (temp_pull, base)

            shutil.copytree(full_tmp, local)
            shutil.rmtree(temp_pull)

    def push(self, local_file_name, upload_path):

        """Push a file to a device"""

        self.__run_command("push %s %s" % (local_file_name, upload_path))

    def run_as(self, user, cmd):

        """Run as a user"""

        self.shell_command("run-as %s %s" % (user, cmd))

    def busybox(self, cmd):

        """Execute a busybox command on device"""

        busybox = get_prop("Info", "busybox")
        self.shell_command("run-as %s %s %s" % (DTF_CLIENT, busybox, cmd))

    def is_file(self, file_name):

        """Check if a file exists on device"""

        self.shell_command("ls %s" % file_name)

        return bool(self.stdout[0] == file_name)

    def is_dir(self, dir_name):

        """Check if a directory exists on device"""

        self.shell_command("ls -ld %s" % dir_name)

        line = [x for x in self.stdout if x][0]

        if line[-26:] == " No such file or directory":
            return False
        elif line[0] == 'd':
            return True
        else:
            return False

    def install(self, apk_path):

        """Install an APK on a device"""

        self.__run_command("install %s" % apk_path)

    def uninstall(self, app_name):

        """Uninstall an application on a device"""

        self.__run_command("uninstall %s" % app_name)

    def is_installed(self, app_name):

        """Check if an application is installed on device"""

        self.shell_command("pm list packages %s" % app_name)

        if self.get_output() == ['']:
            return 0
        else:
            return 1

    def add_forward(self, local, remote):

        """Add an adb forward rule"""

        forward_string = "forward %s %s" % (local, remote)

        self.__run_command(forward_string)

    def remove_forward(self, local):

        """Remove a adb forward rule"""

        remove_string = "forward --remove %s" % local

        self.__run_command(remove_string)

    def kill_server(self):

        """Kill the adb daemon"""

        self.__run_command("kill-server")

    def start_server(self):

        """Start the adb daemon"""

        self.__run_command("start-server")

    def usb(self):

        """Restart device in USB mode"""

        self.__run_command("usb")

    def tcpip(self, port):

        """Restart device in TCP/IP mode"""

        self.__run_command("tcpip %s" % port)

    def connect(self, ip_addr, port):

        """Connect to IP/port"""

        self.__run_command("connect %s:%s" % (ip_addr, port))

        # Any news is bad news.
        if self.get_output() != ['']:
            return None

        print('returning whatever')
        return 0
