# minqlx - A Quake Live server administrator bot.
# Copyright (C) 2015 Mino <mino@minomino.org>

# This file is part of minqlx.

# minqlx is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# minqlx is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with minqlx. If not, see <http://www.gnu.org/licenses/>.

"""
Modified version of Mino's workshop plugin which adds the workshop id
of the current workshop_extra map to self.game.workshop_items
See https://github.com/QLRace/server-settings/blob/master/download_workshop_extra.sh
"""

import minqlx

MAP_IDS = {
    "sand_blaster": 810639815, "r7_drz": 810640089, "daanstrafe03": 810885203, "r7_suburbs": 811243819,
    "r7_mixture": 811244172, "r7_yaq1": 811564197, "r7_yaq2": 811564197, "r7_yaq3": 811564197, "mu_nood": 811564505,
    "speedyctf": 812997654, "kairos_jackson": 812995502, "xt4zy_trythis": 816740916, "aurora_beamclimb": 815852629,
    "r7_endless": 817812429, "inder_xmas2": 817813328, "inder_stalker2": 817814056, "kairos_torture1": 818183735,
    "kairos_torture2": 818183735, "kairos_torture3": 818183735, "boris_torture2": 818183882, "mj_xlarve": 822361969,
    "focus": 823508068, "huntetris": 823510134, "mjc02_1": 823510484, "daanstrafe04": 824947114,
    "acrobat_metal": 827383271, "acrobat_bridges": 827383946, "daanstrafe05": 827528750, "climborama": 828179707,
    "getupthere": 828179998, "aa_oblige1": 829533653, "aa_skypads": 830005488, "daanstrafe06": 830352170,
    "aa_slope": 831020302, "aa_maze": 832001652, "daanstrafe07": 832923893, "aa_quake": 832209883,
    "pea_xweirdx": 850088922, "sdc_uk_01": 850731967, "pornstar_quickie3": 852060803, "timewaste": 852081302,
    "bumpyland": 852175366, "dfwc2014_2": 852839568, "pornvannestrafe1": 852978647, "dkr14": 853576545,
    "apo2": 853576826, "mlctf1beta": 728029244, "hexq3ctf1": 610686214, "ctf_orange": 728522755, "asteroid": 610695633,
    "pornstarghost2": 858065015, "airmaxjumps2": 865244047, "fuckjingles": 867670622, "dfwc04_1": 869329238,
    "hereannh_gocrazy_strafe": 869278650, "handfuck": 866866270, "alexjumps": 866539095
}


class workshop(minqlx.Plugin):
    def __init__(self):
        self.add_hook("map", self.handle_map)
        self.set_cvar_once("qlx_workshopReferences", "")

    def handle_map(self, map_name, factory):
        map_id = MAP_IDS.get(map_name.lower())
        if map_id:
            self.game.workshop_items += [map_id]

        self.game.workshop_items += minqlx.Plugin.get_cvar("qlx_workshopReferences", list)
