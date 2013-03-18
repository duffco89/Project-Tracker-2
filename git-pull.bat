REM a simple batch file to pull a git repository from my USB stick and
REM get updated version of the database and media files too.  Ensures,
REM to the greatest extent possible that the development environments
REM remain consistent across platforms.

REM push to the repository
git pull usb master

REM Copy the database
echo D | XCOPY E:\pjtk2_files\db c:\1work\Python\djcode\pjtk2\db  /S /Y /C 

REM Copy the uploaded files:
echo D | XCOPY E:\pjtk2_files\uploads c:\1work\Python\djcode\pjtk2\uploads /S /Y /C 