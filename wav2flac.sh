#!/bin/bash
# Convert list of wav files to flac 
for f in *.wav; 
  do ffmpeg -i  "$f" "${f%.wav}.flac"; 
done
rm -i *.wav