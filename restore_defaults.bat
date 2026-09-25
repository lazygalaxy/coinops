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
if %setup%=="desktop" (
    echo Running 2 Player Games
    call "2 PLAYER Games.bat"
)
echo Running Swap Mame Screen
call "SWAP MAME SCREEN 1st 2nd.bat"

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
copy favorites.txt ..\%build%\collections\Arcade\playlists\favorites.txt
pause
call "adjust_mame_ini.bat" %build% %setup%
pause
