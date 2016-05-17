# Based on x0rnns's checkplayers(https://github.com/x0rnn/minqlx-plugins/blob/master/checkplayers.py)
# Completely rewritten to use scan_iter instead of keys.
# http://redis.io/commands/scan
#
# LICENSE PREAMBLE GOES HERE

"""
BETA
TODO: DOC
TODO: Check if there is no banned/silenced etc players instead of returing empty table.
"""

import minqlx
import minqlx.database
from operator import itemgetter
import re
import time

PLAYER_KEY = "minqlx:players:{}"


class checkplayers(minqlx.Plugin):
    database = minqlx.database.Redis

    def __init__(self):
        super().__init__()
        self.add_command("permissions", self.cmd_permissions, 4)
        self.add_command("silenced", self.cmd_silenced, 4)
        self.add_command("banned", self.cmd_banned, 4)
        self.add_command("leaverbanned", self.cmd_leaver_banned, 4)
        self.add_command("leaverwarned", self.cmd_leaver_warned, 4)

    @minqlx.thread
    def cmd_permissions(self, player, msg, channel):
        players = []
        for key in self.db.scan_iter("minqlx:players:*:permission"):
            steam_id = key.split(":")[2]
            permission = self.db[key]
            name = self.player_name(steam_id)
            players.append(dict(name=name, steam_id=steam_id, permission=permission))

        output = ["^5Owner: ^2{} Name: ^7{}".format(minqlx.owner(), self.player_name(minqlx.owner())),
                  "{:^24} | {:^17} | {}".format("Name", "Steam ID", "Permission")]
        for p in sorted(players, key=itemgetter("permission"), reverse=True):
            output.append("{name:24} | {steam_id:17} | {permission}".format(**p))
        tell_large_output(player, output)

    @minqlx.thread
    def cmd_silenced(self, player, msg, channel):
        output = ["{:^24} | {:^17} | {:^19} | {}".format("Name", "Steam ID", "Expires", "Reason")]

        for key in self.db.scan_iter("minqlx:players:*:silences"):
            steam_id = key.split(":")[2]
            silenced = self.plugins["silence"].is_silenced(steam_id)
            if silenced:
                expires, score, reason = silenced
                name = self.player_name(steam_id)
                output.append("{:24} | {:17} | {} | {}".format(name, steam_id, expires, reason))
        tell_large_output(player, output)

    @minqlx.thread
    def cmd_banned(self, player, msg, channel):
        output = ["{:^24} | {:^17} | {:^19} | {}".format("Name", "Steam ID", "Expires", "Reason")]

        for key in self.db.scan_iter("minqlx:players:*:bans"):
            steam_id = key.split(":")[2]
            banned = self.plugins["ban"].is_banned(steam_id)
            if banned:
                expires, reason = banned
                name = self.player_name(steam_id)
                output.append("{:24} | {:17} | {} | {}".format(name, steam_id, expires, reason))
        tell_large_output(player, output)

    @minqlx.thread
    def cmd_leaver_banned(self, player, msg, channel):
        if not self.get_cvar("qlx_leaverBan", bool):
            player.tell("Leaver ban is not enabled.")
        else:
            output = self.leavers("ban")
            tell_large_output(player, output)

    @minqlx.thread
    def cmd_leaver_warned(self, player, msg, channel):
        if not self.get_cvar("qlx_leaverBan", bool):
            player.tell("Leaver ban is not enabled.")
        else:
            player.tell("!leaverwarned is not implemented yet")

    def leavers(self, action):
        players = []

        for key in self.db.scan_iter("minqlx:players:*:games_left"):
            steam_id = key.split(":")[2]
            status = self.plugins["ban"].leave_status(steam_id)
            if status and status[0] == action:
                action, ratio = status
                name = self.player_name(steam_id)
                left = self.db[key]
                try:
                    completed = self.db[PLAYER_KEY.format(steam_id) + ":games_completed"]
                except KeyError:
                    completed = 0

                players.append(dict(name=name, steam_id=steam_id, left=left, completed=completed, ratio=ratio))

        output = ["^5{:^24} | {:^17} | {} | {} | {}".format("Name", "Steam ID", "Left", "Completed", "Ratio")]
        for p in sorted(players, key=itemgetter("ratio", "left"), reverse=True):
            output.append("{name:24} | {steam_id:17} | ^1{left:4} ^7| ^2{completed:9} ^7| {ratio:>3.2}".format(**p))

        return output

    def player_name(self, steam_id):
        """Returns the latest name a player has used."""
        try:
            name = self.db.lindex(PLAYER_KEY.format(steam_id), 0)
            if not name:
                raise KeyError
            name = re.sub(r"\^[0-9]", "", name)  # remove colour tags
        except KeyError:
            name = steam_id
        return name


def tell_large_output(player, output):
    """Tells large output in small portions, as not to disconnected the player."""
    for count, line in enumerate(output, start=1):
        if count % 30 == 0:  # decrease if someone getting disconnected
            time.sleep(0.4)  # increase if changing previous line does not help
            player.tell(output[0])
        player.tell(line)
