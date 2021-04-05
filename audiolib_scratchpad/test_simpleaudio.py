import simpleaudio as sa

from pydub import AudioSegment
from pydub.playback import play, get_player_name

song = AudioSegment.from_mp3(r"C:\Users\lived\Google Drive\projects\pysongman\test_data\Louis Armstrong - Struttin With Some Barbecue (1927).mp3")

response = play(song)

debug = 1