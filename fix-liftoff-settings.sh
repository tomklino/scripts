HEIGHT=$(xdpyinfo | grep dimensions | grep -Eo [0-9]+x[0-9]+ | head -n1 | sed -r 's/^[0-9]+x([0-9]+)$/\1/')
WIDTH=$(xdpyinfo | grep dimensions | grep -Eo [0-9]+x[0-9]+ | head -n1 | sed -r 's/^([0-9]+)x[0-9]+$/\1/')

sed "{/Fullscreen/s/1/0/;/Resolution\ Height/s/>0</>$HEIGHT</;/Resolution\ Width/s/>0</>$WIDTH</}" -i ${HOME}/.config/unity3d/LuGus\ Studios/Liftoff/prefs
