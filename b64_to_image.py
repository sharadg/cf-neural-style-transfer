import io
import base64
import sys

#Invoke like this:
#python b64_to_image.py tmp.jpg $(cat tmp.txt)

file_name = str(sys.argv[1]) if len(sys.argv) > 1 else 'image.jpg'
raw = str(sys.argv[2]) if len(sys.argv) > 2 else ''

#print(file_name)
#print(raw)

f = open(file_name, "wb")
f.write(base64.b64decode(raw.encode()))
f.flush()
f.close()
