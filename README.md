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
   
