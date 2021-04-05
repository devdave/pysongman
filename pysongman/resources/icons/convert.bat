for %%f in (*.svg) do (
    echo %%~nf
    echo %%~nf.svg
    echo %%~nf.png
    magick -background none %%~nf.svg %%~nf.png
)