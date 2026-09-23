import os
import time
import glob
import shutil
import subprocess
import threading


from contextlib import suppress
quiet = suppress(BaseException)
 



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
         
         
        # sleep 1/2 sec before restart   
        time.sleep(0.5)
 
                        
    
    
def reset_settings5(index=1):
    ''' copies settings5_x.conf
    '''
    src = './autochanger/settings5_%s.conf'%index
    dst = './settings5.conf'
    with quiet: shutil.copy2(src, dst)

    src = './autochanger/controls.conf'
    dst = './controls.conf'
    with quiet: shutil.copy2(src, dst)

    if index == 9:
        src = './autochanger/controlsbackroom.conf'
        dst = './controls.conf'
        with quiet: shutil.copy2(src, dst)  
      
    #src = './autochanger/settings5_%s.conf'%index
    #dst = './settings5.conf'
    #with quiet: shutil.copy2(src, dst)
    
    
    
def launch_retrofe(index=1):
    RETRO_FE = './core/retrofe.exe'
    
    # if retrofe is visible
    if os.path.isfile(RETRO_FE):
        
        # reset mame
        reset_mame()
        
        # set proper settings5.conf
        reset_settings5(index)
        
        
        
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
            
             
    


