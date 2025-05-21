@ECHO ON
title AB_Foundation

call C:/anaconda3/Scripts/activate.bat C:/anaconda3
call conda activate ab_foundation2_1
cd C:\pythonProject\ab_foundation2_1\ab_foundation2_1
python manage.py runserver
pause