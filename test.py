import time
import mouse_control as mc
import pyautogui
import wayland_automation as wa

cooldown = 0.5  # en secondes (ex: 500 ms)
last_click = 0


i = 0



while True:
    
    x,y = mc.get_position()

    #print(mc.get_position())

    if x < 500 and y < 500 and time.time() >  last_click + cooldown:
        
        print(i)
        i = i + 1

        last_click = time.time() 
