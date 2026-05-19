"""System related functions."""

import grp
import pwd
import sys

from . import utils


def create_user(name, home=None):
    """Create a new system user."""
    try:
        user_info = pwd.getpwnam(name)
    except KeyError:
        user_info = None
    else:
        extra_message = "."
        if home:
            extra_message = (
                " but the {} directory will be ensured.".format(home)
            )
        utils.printcolor(
            "User {} already exists, skipping creation{}".format(
                name, extra_message), utils.YELLOW)
    cmd = "useradd -m "
    if home:
        cmd += "-d {} ".format(home)
    if user_info is None:
        utils.exec_cmd("{} {}".format(cmd, name))
        user_info = pwd.getpwnam(name)
    if home:
        utils.mkdir_safe(home, 0o755, user_info.pw_uid, user_info.pw_gid)


def add_user_to_group(user, group):
    """Add system user to group."""
    try:
        pwd.getpwnam(user)
    except KeyError:
        print("User {} does not exist".format(user))
        sys.exit(1)
    try:
        grp.getgrnam(group)
    except KeyError:
        print("Group {} does not exist".format(group))
        sys.exit(1)
    utils.exec_cmd("usermod -a -G {} {}".format(group, user))


def enable_service(name):
    """Enable a service at startup."""
    utils.exec_cmd("systemctl enable {}".format(name))


def enable_and_start_service(name):
    """Enable a start a service."""
    enable_service(name)
    code, output = utils.exec_cmd("service {} status".format(name))
    action = "start" if code else "restart"
    utils.exec_cmd("service {} {}".format(name, action))


def restart_service(name):
    """Restart a service."""
    utils.exec_cmd("service {} restart".format(name))
