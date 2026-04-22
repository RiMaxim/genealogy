# Обрабатывает каждый файл и сохраняет изменения в нём же
for file in *.txt; do
    awk -v OFS='\t' '{print FILENAME, $0}' "$file" > temp && mv temp "$file"
done

