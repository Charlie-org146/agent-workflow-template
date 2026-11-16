# Design: toys-userprofile

Problem: dev/toy/test-prd-copy.sh sets HOME without USERPROFILE, so the toys-set-userprofile row (test-home-guard.py isolate) fails on this PC and on CI (#4514).

Approaches: (1) add USERPROFILE beside HOME in the toy; (2) also exempt the toy from the scan. Chosen: 1, since the scan is right. The scan gets a function and two controls (HOME alone is found, HOME with USERPROFILE is not), so it is proven able to fail.

Done lines: line 1 is the one-line toy fix; line 2 is the scan function with its controls inside the same row.
