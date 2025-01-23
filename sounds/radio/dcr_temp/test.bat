@echo on
setlocal

:: Define the base directory
set "base_dir=E:\Modding Tools\BAE v0.11-78-0-11-1541070494\extracts\4\Sound\Voice\Fallout4.esm\NPCMTravisMiles"

:: Remove all existing 'pre' and 'after' directories recursively from the base directory
FOR /d /r "%base_dir%" %%d IN (pre) DO IF EXIST "%%d" rd /s /q "%%d"
FOR /d /r "%base_dir%" %%d IN (after) DO IF EXIST "%%d" rd /s /q "%%d"

:: Main script
:: Call the function to create 'pre' and 'after' folders in base_dir and its subdirectories
call :CreateFolders "%base_dir%"

:: End the script
endlocal
exit /b

:: Function to create 'pre' and 'after' folders
:CreateFolders
set "current_dir=%~1"

:: Iterate through each subdirectory in the current directory
for /d %%d in ("%current_dir%\*") do (
    :: Get the name of the subdirectory
    set "subdir_name=%%~nxd"
    
    :: Skip folders named 'pre' or 'after' and continue recursion in other directories
    if /i not "%subdir_name%" == "pre" if /i not "%subdir_name%" == "after" (
        :: Recursively call the function for each subdirectory
        call :CreateFolders "%%~d"
    )
)

:: Create 'pre' and 'after' folders in the current directory
if /i not "%current_dir%" == *\pre if /i not "%current_dir%" == *\after (
    if not exist "%current_dir%\pre" mkdir "%current_dir%\pre"
    if not exist "%current_dir%\after" mkdir "%current_dir%\after"
)

:: Return control to the calling script
exit /b
