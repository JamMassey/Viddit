@echo off

set exclude_file=%1
set folder_to_upload=%2
set pem_location=%3
set user_server=%4

if not defined exclude_file goto :error_no_exclude
if not defined folder_to_upload goto :error_no_folder
if not defined pem_location goto :error_no_pem
if not defined user_server goto :error_no_user_server

set folder_temp=%folder_to_upload%-temp

echo Creating a temporary copy of the folder without the excluded files...
xcopy /E /I /EXCLUDE:%exclude_file% %folder_to_upload% %folder_temp%

echo Transferring files to remote server...
scp -i "%pem_location%" -r "%folder_temp%" "%user_server%:/home/ubuntu/app/"

echo Removing temporary folder...
rmdir /S /Q %folder_temp%

echo Transfer complete.
goto :EOF

:error_no_exclude
    echo ERROR: Missing exclude file argument.
    goto :EOF

:error_no_folder
    echo ERROR: Missing folder to upload argument.
    goto :EOF

:error_no_pem
    echo ERROR: Missing .pem location argument.
    goto :EOF

:error_no_user_server
    echo ERROR: Missing user@server argument.
    goto :EOF
