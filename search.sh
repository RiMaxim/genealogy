#!/bin/bash

# Папки
IMAGE_DIR="$HOME/Desktop/tmp/image"
PDF_DIR="$HOME/Desktop/tmp/pdf"
TXT_DIR="$HOME/Desktop/tmp/txt"

# Проверка аргументов
if [ $# -lt 2 ]; then
    echo "Usage: $0 <filename> <char1> [char2] [char3] ..."
    exit 1
fi

FILENAME="$1"
shift

# Закрываем Preview перед началом
killall Preview 2>/dev/null
sleep 1

# Создаем PDF
img2pdf "$IMAGE_DIR/$FILENAME.jpg" -o "$PDF_DIR/$FILENAME.pdf"

# Очищаем буфер обмена
pbcopy < /dev/null

# Открываем ТОЛЬКО этот PDF
open -a "Preview" "$PDF_DIR/$FILENAME.pdf"
sleep 3

# Строим команду для AppleScript с проверкой КАЖДОГО иероглифа
CHECK_CMD=""
for i in $(seq 1 $#); do
    CHAR="${!i}"
    CHECK_CMD="$CHECK_CMD
    if theText contains \"$CHAR\" then
        set c$i to $i
    else
        set c$i to 0
    end if"
done

# Строим строку результата из ВСЕХ проверок
RESULT_STR="c1 as string"
for i in $(seq 2 $#); do
    RESULT_STR="$RESULT_STR & \"\\t\" & c$i as string"
done

osascript -e "
tell application \"Preview\" to activate
delay 1
tell application \"System Events\"
    keystroke \"a\" using command down
    delay 0.5
    keystroke \"c\" using command down
    delay 0.5
end tell
delay 0.5
tell application \"Preview\" to quit

try
    set theText to the clipboard as text
    set c1 to 0
    $CHECK_CMD
    set result to $RESULT_STR
    do shell script \"mkdir -p '$TXT_DIR' && echo '\" & result & \"' > '$TXT_DIR/$FILENAME.txt'\"
on error
    do shell script \"mkdir -p '$TXT_DIR' && echo '0' > '$TXT_DIR/$FILENAME.txt'\"
end try
"

# Закрываем Preview после всего
killall Preview 2>/dev/null

