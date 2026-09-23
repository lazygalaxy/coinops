@echo off
set build="Arise BP Edition PLUS"
echo Restoring LazyGalaxy Defaults on %build% ...

cd ..
cd %build%
echo Restoring Build Defaults
call "- Restore Defaults.bat"
pause

cd ".\- Advanced Configs\"
echo Running 2 Player Games
call "2 PLAYER Games.bat"
echo Running Swap Mame Screen
call "SWAP MAME SCREEN 1st 2nd.bat"
pause

cd ..
cd ".\- Themes\"
echo Running Theme
call "Cabinet.bat"
pause

cd ..
cd ".\- Themes 2nd Screen\"
echo Running Marquee Theme
call "Animated Marquee (for 16x9 Screen).bat"
pause

cd ..
cd ..
cd "coinops"
echo Copying Favorites
copy favorites.txt ..\%build%\collections\Arcade\playlists\favorites.txt
pause
call "adjust_mame_ini.bat" %build%
pause
