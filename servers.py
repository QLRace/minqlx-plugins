# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Adds !servers command which shows status of servers.
This plugin depends on python-valve which you can install with
sudo python3.5 -m pip install python-valve
"""

import minqlx
import socket
import valve.source.a2s as a2s


class servers(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.add_command("servers", self.cmd_servers)

        # Example value "108.61.190.53:27960, 108.61.190.53:27961, il.qlrace.com:27960"
        self.set_cvar_once("qlx_servers", "")
        self.set_cvar_once("qlx_serversShowInChat", "0")

    def cmd_servers(self, player, msg, channel):
        """If `qlx_servers` is set then it outputs status of servers.
        Outputs to chat if `qlx_serversShowInChat` is 1, otherwise it will
        output to the player who called the command only."""
        servers = self.get_cvar("qlx_servers", list)
        if not servers:
            self.logger.warning("qlx_servers is not set")
            player.tell("qlx_servers is not set")
            return minqlx.RET_STOP_ALL

        if not self.get_cvar("qlx_serversShowInChat", bool):
            self.get_servers(servers, minqlx.TellChannel(player))
            return minqlx.RET_STOP_ALL

        self.get_servers(servers, channel)

    @minqlx.thread
    def get_servers(self, servers, channel):
        """Gets and outputs info for all servers in `qlx_servers`."""
        output = "{} | {} | {}\n".format("IP".center(21), "sv_hostname".center(40), "Player Count")
        for server in servers:
            hostname, player_count = self.get_server_info(server)
            if player_count[0].isdigit():
                players = [int(n) for n in player_count.split("/")]
                if players[0] == players[1]:
                    player_count = "^3{}".format(player_count)
                else:
                    player_count = "^2{}".format(player_count)
            output += "{:21} | {:40} | {}^7\n".format(server, hostname, player_count)

        channel.reply(output)

    @staticmethod
    def get_server_info(server):
        """Gets server info using python-valve."""
        # set port to 27960 if no port
        address = (server.split(":") + [27960])[:2]
        try:
            address[1] = int(address[1])
            server = a2s.ServerQuerier(address)
            info = server.get_info()
            return info['server_name'], "{player_count}/{max_players}".format(**info)
        except ValueError:
            return "Error: Invalid port", "^1..."
        except socket.gaierror:
            return "Error: Invalid/nonexistent address", "^1..."
        except a2s.NoResponseError:
            return "Error: Timed out", "^1..."