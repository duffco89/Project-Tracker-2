REM a simple batch file to call push revision to the USB stick and 
REM copy the database and media files too.  Ensures, to the greatest extent possible
REM that the development environments remain consistent across platforms.

REM push to the repository
git push usb --all

REM Copy the database
echo D | XCOPY c:\1work\Python\djcode\pjtk2\db E:\pjtk2_files\db /S /Y /C 

REM Copy the uploaded files:
echo D | XCOPY c:\1work\Python\djcode\pjtk2\uploads E:\pjtk2_files\uploads /S /Y /C 