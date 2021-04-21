# pysongman

## Project goal
 Learn PySide2 and then make a music player


## Music player initial goals

Collect and index a LARGE music library (~40 GB or ~10K files)  
Play mp3 & ogg files


## Future goals

Emulate the winamp player UI without visualizations
* library breakdown
    * Artist -> Album -> Song
    * Active playlist/queue
    * Smart views
  
Support a direct SQL inject input for selecting songs for a library "view"  
Support small python scripts for selecting songs for a library "view"  


## Nice to have but not necessary

* spectrographic visualization

## TODO

1. Right now the Player controller is becoming increasingly overloaded
so perhaps a better solution would be to make a faceless controller/Application
which implements the anti-pattern God Module pattern but lords over
the whole application.
   

## PyTaglib adventure

The issues with reading id3/file tag data is pissing me off so
I've decided to bring out the big guns and search for a viable
c++ library to do the work for me.   Tag lib seems to be the best option
at the moment.

My steps:
Install Visual Studio 2019 community edition
Grab the 8.1 SDK - https://stackoverflow.com/a/53840125/9908
git clone'd pytaglib from github
python windows/build_win.py
Minor issue cropped up and my fix was here https://github.com/supermihi/pytaglib/issues/49
