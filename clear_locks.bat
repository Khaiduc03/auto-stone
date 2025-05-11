@echo off
REM Kiểm tra xem đã truyền tham số chưa
if "%~1"=="" (
    echo Usage: %~nx0 DEVICE_ID
    echo Ví dụ: %~nx0 127.0.0.1:5557
    goto :eof
)

set "deviceId=%~1"
echo ======================================
echo   Thao tác trên thiết bị: %deviceId%
echo ======================================

REM Xóa các file khóa màn hình
adb.exe -s %deviceId% shell "su -c 'rm /data/system/gesture.key'"     > nul 2>&1
adb.exe -s %deviceId% shell "su -c 'rm /data/system/password.key'"    > nul 2>&1
adb.exe -s %deviceId% shell "su -c 'rm /data/system/gatekeeper.pattern.key'"  > nul 2>&1
adb.exe -s %deviceId% shell "su -c 'rm /data/system/gatekeeper.password.key'" > nul 2>&1
adb.exe -s %deviceId% shell "su -c 'rm /data/system/locksettings.db'"   > nul 2>&1
adb.exe -s %deviceId% shell "su -c 'rm /data/system/locksettings.db-shm'"   > nul 2>&1
adb.exe -s %deviceId% shell "su -c 'rm /data/system/locksettings.db-wal'"   > nul 2>&1

echo Hoan tat!
