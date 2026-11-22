# The file limit raised to 200

- Feature: GRD-21
- Release: patch (v1.1.x)
- Goals: grd21-cap-lift
- Needs: 
- Replaced by: 
- Source: frozen-source-v1.1.0-1052 (sha256 cd66455a83be4a0b), owner o721; the owner's o718 words as recorded in the goal file of grd21-cap-lift

## Purpose

the file limit raised to 200 (o718, o719)
Temporarily raise the package file cap to 200 (owner o718, GRD-21)

## Done when

- MAX_FILES is 200, a package of 200 files passes its file check and a 201st file fails it
