from torrent_format.torrent_file import TorrentFile, PrivateTorrentFile
from webserver.webserver import User

User.initialize()
TorrentFile.initialize()
PrivateTorrentFile.initialize()
