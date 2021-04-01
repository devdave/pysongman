import sys
import argparse


import PySide2
from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2 import QtWidgets
from PySide2 import QtMultimedia


class PlayerWindow(QtWidgets.QWidget):
    
    def __init__(self, *args, **kwargs):
        super(PlayerWindow, self).__init__(*args, **kwargs)

        self.setupUI()

        self.player = QtMultimedia.QMediaPlayer()



    def setupUI(self):
        """            
                        
            main body
            ----------------------------------------------------------
            Time progress - misc info - spectragraph
            marque
            ----------------------------------------------------------
            one vertical
            
            
            playlist controls
            ----------------------------------------------------------
            Repeat 1/all
            random playlist
            ----------------------------------------------------------
            one vertical
            
            layout
            ---------------------------------------------------------
            LINE1 => Main body - playlist controls
            LINE2 => progress bar - load file - playlist view - media view
            LINE3 => previous, play, pause, stop, next - mute - volume slider
            ---------------------------------------------------------
            three horz layouts wrapped in one vertical
            
        """

        #Main display body
        self.time_display = QtWidgets.QLabel("0:00")
        self.diagnostics = QtWidgets.QLabel("Place holder")
        self.spectagraph = QtWidgets.QLabel("Spectragraph")
        self.info_dash1 = QtWidgets.QHBoxLayout()
        self.info_dash1.addWidget(self.time_display)
        self.info_dash1.addWidget(self.diagnostics)
        self.info_dash1.addWidget(self.spectagraph)


        self.info_dash = QtWidgets.QVBoxLayout()
        self.current_song = QtWidgets.QLabel("Artist - Title (12:34)")
        self.info_dash.addLayout(self.info_dash1)
        self.info_dash.addWidget(self.current_song)

        self.info_dash.setObjectName("infoDashboard")


        #Playlist controls
        self.repeat_button = QtWidgets.QPushButton("L")
        self.random_button = QtWidgets.QPushButton("RA")


        self.playlist = QtWidgets.QVBoxLayout()
        for button in [self.repeat_button, self.random_button]:
            button.setMinimumWidth(3)
            button.setMaximumWidth(25)
            self.playlist.addWidget(button)

        self.playlist.setObjectName("playListControls")

        #line1
        self.body_playlist_behavior = QtWidgets.QHBoxLayout()
        self.body_playlist_behavior.addLayout(self.info_dash)
        self.body_playlist_behavior.addLayout(self.playlist)


        #Line2
        self.progress_bar = QtWidgets.QSlider(Qt.Horizontal)
        self.load_btn = QtWidgets.QPushButton("LD")
        self.playlist_btn = QtWidgets.QPushButton("PL")
        self.medialib_btn = QtWidgets.QPushButton("ML")

        self.status_and_views = QtWidgets.QHBoxLayout()
        self.status_and_views.addWidget(self.progress_bar)

        for button in [self.load_btn, self.playlist_btn, self.medialib_btn]:
            button.setMinimumWidth(3)
            button.setMaximumWidth(25)
            self.status_and_views.addWidget(button)



        #line3 - previous, play, pause, stop, next - mute - volume slider
        self.previous_btn = QtWidgets.QPushButton("PR")
        self.play_btn = QtWidgets.QPushButton("PL")
        self.pause_btn = QtWidgets.QPushButton("PS")
        self.stop_btn = QtWidgets.QPushButton("ST")
        self.next_btn = QtWidgets.QPushButton("NXT")
        self.mute_btn = QtWidgets.QPushButton("MUTE")
        self.volume_slider = QtWidgets.QSlider(Qt.Horizontal)

        self.controls = QtWidgets.QHBoxLayout()
        self.controls.setObjectName("controlBar")

        for button in [self.previous_btn, self.play_btn, self.pause_btn, self.stop_btn, self.next_btn, self.mute_btn]:
            button.setMinimumWidth(3)
            button.setMaximumWidth(25)
            self.controls.addWidget(button)


        self.controls.addWidget(self.volume_slider)

        #Menu bar
        self.menu_bar = QtWidgets.QMenuBar()

        self.menu_file = QtWidgets.QMenu("&File")
        self.menu_play = QtWidgets.QMenu("&Play")
        self.menu_options = QtWidgets.QMenu("&Options")
        self.menu_view = QtWidgets.QMenu("&View")
        self.menu_help = QtWidgets.QMenu("&Help")

        for menu in [self.menu_file, self.menu_play, self.menu_options, self.menu_view, self.menu_help]:
            self.menu_bar.addMenu(menu)

        # Put it all together
        self.main_body = QtWidgets.QVBoxLayout()
        self.main_body.layout().setMenuBar(self.menu_bar)
        self.main_body.addLayout(self.body_playlist_behavior)
        self.main_body.addLayout(self.status_and_views)
        self.main_body.addLayout(self.controls)


        self.setLayout(self.main_body)
        self.setWindowTitle("PySongMan")
        self.setMinimumWidth(350)




class PlayerController(QtCore.QObject):
    def __init__(self):
        self.view = PlayerWindow()







def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("music-file")
    args = parser.parse_args(argv)

    app = QtWidgets.QApplication(argv)

    controller = PlayerController()
    controller.view.show()

    app.exec_()
    return



if __name__ == '__main__':
    main(sys.argv[1:])