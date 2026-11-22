# Implement DEL-3.1 to DEL-3.5 (revised DEL-3): one fixed list of the owner's decisions, everything else on the recommendation (release v1.2.0; owner o780 "DEL-3 reviewed")

- Slug: v120-del3-core
- Touches: skills/workflow-monitoring, skills/workflow-delivery, dev/toy, .loop/regression.tsv
- ETA: 335 active minutes (estimate 267m plus a 25% margin)

Stacked on: ce67522c33fceaf6c441c274e5a6ef713fafdba5

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given DEL-3.1, then one file every session reads holds the fixed list of five classes, only owner words change it, and a toy goal facing a choice not on the list goes ahead on the recommendation and asks nothing, while a choice on the list waits and asks
2. Given DEL-3.2, then a toy goal facing a two-option choice not on the list acts on the recommended option within 2 minutes, and its record shows the options, the reason and the undo
3. Given DEL-3.3, then a toy goal whose lane finds a tool bug opens one issue and starts a patch goal that merges on green, and no question reaches the owner; a fix that would change a promise or loosen a test waits on the list
4. Given DEL-3.4, then an answer typed in one operation session is written into the one record of owner words with the session it was typed in, another machine's guard finds and acts on it without a retype, and a relayed message is never counted as owner words
5. Given DEL-3.5, then after two decisions made for the owner the board's "Decided for you" list shows both with their reasons, and typing one undo line reverses that decision
6. Given the whole change, then the docs check, package check and private-name scan pass, every new behaviour has a regression row with a negative control, no existing row changes result, no file newly crosses 19,000 bytes or the 20,480 cap, and any change to a guard that protects the owner (DEL-3.1 item 1, DEL-3.4) waits for the owner's word on its pull request

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
