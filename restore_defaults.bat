@echo off

set build="Arise BP Edition PLUS"
::set build="Arise Max"
::set build="Forgotten Worlds EVO 2 (2026)"
::set build="Forgotten Worlds EVO 2 Vertical (2026)"

set setup="cocktail"
::set setup="desktop"

echo Restoring LazyGalaxy Defaults on %build% for %setup% ...

cd ..
cd %build%
echo Restoring Build Defaults
call "- Restore Defaults.bat"
pause

cd ".\- Advanced Configs\"
if %setup%=="cocktail" (
    echo Running 4 Player Games
    call "4 PLAYER Games.bat"
)
echo Running Swap Mame Screen
call "SWAP MAME SCREEN 1st 2nd.bat"
pause

cd ..
cd ".\- Bezels Glass and Scanlines\"
echo Disable Bezels
call "BEZELS Off.bat"
pause

cd ..
cd ".\- Themes\"
echo Running Theme
call "Cabinet.bat"
pause

if %setup%=="desktop" (
    cd ..
    cd ".\- Themes 2nd Screen\"
    echo Running Desktop Theme
    call "Desktop (for 16x9 Screen).bat"
    pause
)

cd ..
cd ..
cd "coinops"
echo Copying Favorites
:: TODO: move to python script with folder agnostic pathing for various favourite paths
:: TODO: also check the format of the file
copy favorites.txt ..\%build%\collections\Arcade\playlists\favorites.txt
copy favorites.txt ..\%build%\collections\Arcader\playlists\favorites.txt
copy favorites.txt ..\%build%\collections\Arcades\playlists\favorites.txt
copy favorites.txt ..\%build%\collections\Arcade34\playlists\favorites.txt
copy favorites.txt ..\%build%\collections\Arcade94\playlists\favorites.txt
copy favorites.txt ..\%build%\collections\Arcade248\playlists\favorites.txt
pause
rem call "adjust_mame_ini.bat" %build%
rem pause
call "apply_game_setup.bat" %build% %setup%
pause
if %setup%=="cocktail" (
    echo Copying Mame Configs
    copy mame\cfg\cocktail\*.cfg ..\%build%\emulators\mame\cfg\
    pause
)
