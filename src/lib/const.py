#!/usr/bin/env python
# -*- coding: utf-8 -*-

# gmbox, Google music box.
# Copyright (C) 2009, gmbox team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

VERSION = '0.2.3'
songlists = {
    u'华语新歌':('chinese_new_songs_cn',100),
    u'欧美新歌':('ea_new_songs_cn',100),
    u'华语热歌':('chinese_songs_cn',200),
    u'欧美热歌':('ea_songs_cn',200),
    u'日韩热歌':('jk_songs_cn',200),
    u'流行热歌':('pop_songs_cn',100),
    u'摇滚热歌':('rock_songs_cn',100),
    u'嘻哈热歌':('hip-hop_songs_cn',100),
    u'影视热歌':('soundtrack_songs_cn',100),
    u'民族热歌':('ethnic_songs_cn',100),
    u'拉丁热歌':('latin_songs_cn',100),
    u'R&B热歌':('rnb_songs_cn',100),
    u'乡村热歌':('country_songs_cn',100),
    u'民谣热歌':('folk_songs_cn',100),
    u'灵歌热歌':('soul_songs_cn',100),
    u'轻音乐热歌':('easy-listening_songs_cn',100),
    u'爵士蓝调热歌':('jnb_songs_cn',100)
    }
albums_lists = {
    u'华语最新专辑':('chinese_new-release_albums_cn',100),
    u'欧美最新专辑':('ea_new-release_albums_cn',100),
    u'华语热碟':('chinese_albums_cn',100),
    u'欧美热碟':('ea_albums_cn',100),
    u'日韩热碟':('jk_albums_cn',100),
    u'流行新碟':('pop_new_albums_cn',10),
    u'流行热碟':('pop_albums_cn',100),
    u'摇滚新碟':('rock_new_albums_cn',10),
    u'摇滚热碟':('rock_albums_cn',100),
    u'嘻哈新碟':('hip-hop_new_albums_cn',10),
    u'嘻哈热碟':('hip-hop_albums_cn',100),
    u'影视新碟':('soundtrack_new_albums_cn',10),
    u'影视热碟':('soundtrack_albums_cn',100),
    u'民族热碟':('ethnic_albums_cn',100),
    u'拉丁热碟':('latin_albums_cn',100),
    u'R&B热碟':('rnb_albums_cn',100),
    u'乡村热碟':('country_albums_cn',100),
    u'民谣热碟':('folk_albums_cn',100),
    u'灵歌热碟':('soul_albums_cn',100),
    u'轻音乐热碟':('easy-listening_albums_cn',100),
    u'爵士蓝调热碟':('jnb_albums_cn',100),
}

list_url_template = 'http://www.google.cn/music/chartlisting?q=%s&cat=song&start=%d'
albums_list_url_template = 'http://www.google.cn/music/chartlisting?q=%s&cat=album&start=%d'
album_song_list_url_template = 'http://www.google.cn/music/album?id=%s'
xml_album_song_list_url_template = 'http://www.google.cn/music/album?id=%s&output=xml'
search_url_template = 'http://www.google.cn/music/search?q=%s&cat=song&start=%d'
albums_search_url_template = 'http://www.google.cn/music/search?q=%s&cat=album&start=%d'
song_url_template = 'http://www.google.cn/music/top100/musicdownload?id=%s'
song_streaming_url_template = 'http://www.google.cn/music/songstreaming?id=%s&cad=pl_player&sig=%s&output=xml'
flash_player_key = 'c51181b7f9bfce1ac742ed8b4a1ae4ed'
