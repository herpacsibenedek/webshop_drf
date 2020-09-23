set filename=%~n0

start cmd.exe /k "cd /D E:\p\%filename% & env\Scripts\activate & echo Python FTW!! "
start cmd.exe /k "cd /D E:\p\%filename% & env\Scripts\activate & echo Python FTW!! & python manage.py runserver"

