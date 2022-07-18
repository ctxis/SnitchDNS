#!/bin/bash

INPUT_FILE="$1"
OUTPUT_FILE="$2"

if [ -z "$INPUT_FILE" ] || [ -z "$OUTPUT_FILE" ]; then
    echo "Syntax: ./convert.sh [FILE] [OUTPUT]"
    exit 1
fi
echo "Reading file..."
DATA=""
while IFS=, read -r id domain ip
do
    domain=$(echo "$domain" | tr -d "\"")
    if [ "$domain" = "domain" ]; then
        continue
    fi

    DATA="${DATA}\n${domain}"
done < "$INPUT_FILE"

echo "Putting file together..."
DATA=$(echo -e "$DATA" | sort)
HEX=""
while IFS= read -r line; do
    IFS="." read -r -a subs <<< "$line"
    HEX="${HEX}${subs[1]}"
done <<< "$DATA"

echo "Saving file..."
echo "$HEX" | xxd -r -p > "$OUTPUT_FILE"