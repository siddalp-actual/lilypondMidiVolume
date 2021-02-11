# lilypondMidiVolume
A technique to increase the midi volume (velocity) on each iteration through a repeated section

Bogus dynamic instructions `\spf` and `\rpf` (for set and read) are defined.  The `dynamicAbsoluteVolumeFunction` is overridden so that when the `\spf` or `\rfp` instructions are seen, the 'volume' is updated or read.  
A scheme closure is used to hold the current volume (velocity) with methods to read and update it.

## Contents
```
notebookScript/
  Repeat Volume.py : This is the python script representation of a jupyter notebook containing my notes
repeatStave.ly : a simple lilypond piece used to create a midi file, dumped by the above notebook
dynamicPart.ly : lilypond piece containing a simple repeating phrase which gets louder with each iteration.
.atombuild.yaml : configuration for atom editor to build lilypond files
```
