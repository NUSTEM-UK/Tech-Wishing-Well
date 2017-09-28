# Python camera notes

## test01 -- Capture to file
For 768 x 768 resoution, takes about 0.58 sec to process and output.

## test02 -- Stream capture
Same resoution: about 0.55 sec to capture to in-memory stream. Ouch.

## test03 -- stream to PIL
Adds very little overhead - 0.56 sec to capture to PIL object.

## test04 -- capture_continuous
Appears to be terrible (~1fps?), but thats mostly the processing to JPEG?

## test05 -- capture to numpy array
Still about 0.54 secs

## test06 -- capture to YUV
Still 0.54 sec

