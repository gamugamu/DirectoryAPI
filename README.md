# directoryAPI

http://www.color-hex.com/color-palettes/

Lancer le serveur en debug (watchdog change file support)

watchmedo shell-command --patterns="*.py;*.html;*.css;*.js" --recursive --command='echo "${watch_src_path}" && kill -HUP `cat gunicorn.pid`' . &
gunicorn app:app --pid=gunicorn.pid --threads 4
