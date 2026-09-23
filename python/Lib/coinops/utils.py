import os
import sys
import time
import glob
import shutil
import subprocess
import threading
import signal, atexit
import argparse

from contextlib import suppress
quiet = suppress(BaseException)
 
 

# ensure cleanup of all threads if python process is terminated
def handle_exit():
    os._exit(1)
    
atexit.register(handle_exit)
signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)    




def reset_mame():
    ''' This function resets mame's default.cfg
    '''
    
    DEFAULTX = './emulators/mame/cfg/defaultx.cfg'
    DEFAULT  = './emulators/mame/cfg/default.cfg'
    with quiet: shutil.copy2(DEFAULTX, DEFAULT)
 

def refresh_favorites(txt_file, icon_png, sub_file, png_path):
    
    ''' Monitors the favorite list and updates .pngs
    '''
    timestamp = None
    
    while True:
        if os.path.isdir(png_path):  
            stamp = os.stat(txt_file).st_mtime
            
            # text file has changed !
            if timestamp is None or stamp != timestamp:
                timestamp = stamp
                
                # gather existing pngs
                existing_pngs  = glob.glob('%s/*.png'%png_path)
                existing_names = [os.path.splitext(os.path.split(x)[-1])[0] for x in existing_pngs]
                existing       = dict(zip(existing_names, existing_pngs))
                
                # read the favorites file
                favorites = []
                if os.path.isfile(txt_file):
                    with open(txt_file, 'r') as io:
                        favorites = io.readlines()
                    favorites = [x.strip() for x in favorites if x.strip()]
                
                # add new files
                for game in favorites:
                    if not game in existing:
                        with quiet: shutil.copy2(icon_png, '%s/%s.png'%(png_path,game))
    
                # delete missing files
                for game in existing:
                    if not game in favorites:
                        with quiet: os.remove(existing[game])
                        
                # overwrite ArcadeAll.sub
                with quiet: shutil.copy2(txt_file, sub_file)
         
         
        # sleep 1/10 sec before restart   
        time.sleep(0.1)
 
                        
    
    
def reset_settings5(src):
    ''' copies settings5_x.conf
    '''
    
    dst = './settings5.conf'
    with quiet: os.remove(dst)
    with quiet: shutil.copy2(src, dst)
    
    
 
def launch_retrofe():    
    
    parser = argparse.ArgumentParser(description='CoinOPS configuration')
    parser.add_argument('-settings5',
                        '--settings5',
                        action='store',
                        required=False,
                        help="Copies the specified config file to settings5.conf.")
    
    options = parser.parse_known_args()
         
    
    
    # if retrofe is visible
    RETRO_FE = './core/retrofe.exe'
    
    if os.path.isfile(RETRO_FE):
        
        # reset mame
        reset_mame()
        
        
        # set proper settings5.conf
        reset_settings5(options[0].settings5)

        
        
        # monitor favorites for changes on its own thread
        monitor_all      = threading.Thread(target=refresh_favorites, args=('./collections/ArcadeAll/playlists/favorites.txt',
                                                                            './autochanger/favorites.png',
                                                                            './collections/ArcadeFavs/ArcadeAll.sub',
                                                                            './collections/ArcadeAll/medium_artwork/hearts'))
              
        monitor_micro    = threading.Thread(target=refresh_favorites, args=('./collections/ArcadeMicroAll/playlists/favorites.txt',
                                                                            './autochanger/favorites_micro.png',
                                                                            './collections/ArcadeMicroFavs/ArcadeMicroAll.sub',
                                                                            './collections/ArcadeMicroAll/medium_artwork/hearts'))
              
        monitor_backroom = threading.Thread(target=refresh_favorites, args=('./collections/Backroom/playlists/favorites.txt',
                                                                            './autochanger/favorites_backroom.png',
                                                                            './collections/ArcadeAll/exclude.txt',
                                                                            './collections/Backroom/medium_artwork/hearts'))
           
        monitor_all.start()
        monitor_micro.start()
        monitor_backroom.start()
        
        
        # launch retrofe and wait for it to exit
        p = subprocess.Popen(RETRO_FE)
        p.wait()
        
        
        # exit and cleanup
        os._exit(1)
            
             
    


