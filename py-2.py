#!/usr/bin/env python

import leveldb
import sys
import re
import json
import codecs
import os
import shutil
import glob
import zipfile
import traceback
logf = open("github-action-run.log", "w", encoding="utf8")


def log(msg):
    print(msg)
    logf.write(str(msg)+"\n")


def logAndClose(msg):
    print(msg)
    logf.write(str(msg)+"\n")
    logf.close()

f = sys.argv[1].strip()

log(f"arg1 is:{f}")
log(f"pwd:{os.getcwd()}")
unpack_dir="unpack-output"
shutil.rmtree(unpack_dir, ignore_errors=True)
if os.path.exists(f) and os.path.isfile(f):
    try:
        shutil.unpack_archive(f, unpack_dir)
    except Exception as e:
        # qz,traceback.print_tb(e)
        msg=traceback.format_exc()
        logAndClose(msg)
        exit()
    print("success")
else:
    msg=f"arg 1 do not exist or is not file:{f}."
    log(msg)
    exit(1)

print("-"*20,"begin os.walk to find the database root")
target_dirs=[]
for dirpath, dirnames, filenames in os.walk(unpack_dir):
    for file_name in filenames:
        if file_name.startswith("MANIFEST-"):
            target_dirs.append(dirpath)
            break
if len(target_dirs)==0:
    logAndClose(f"no dir that include MANIFEST-xxx file ")
    exit(1)
elif len(target_dirs)>1:
    logAndClose(f"one more dirs that include MANIFEST-xxx file ")
    exit(1)
leveldb_dir = target_dirs[0]
log(f"leveldb database dir:{leveldb_dir}")

output_dir = "extract_tampermonkey_script_output"
shutil.rmtree(output_dir,ignore_errors=True)

# os.mkdir(output_dir)
os.makedirs(output_dir,exist_ok=True)

pattern = re.compile("^@source(.*)$")

db = leveldb.LevelDB(leveldb_dir)

for k, v in db.RangeIter():
    m = pattern.match(k.decode('utf-8'))
    if m:
        name = re.sub("[\W\b]", "_", m.groups()[0].strip())
        # full_name = "%s.user.js" % name
        full_name = os.path.join(output_dir,"%s.user.js" % name)

        print("Writing to %s" % full_name)

        content = json.JSONDecoder().decode(v.decode('utf-8'))['value']

        with codecs.open(full_name, 'w', 'utf-8') as text_file:
            text_file.write(content)
# pack
# "zip", "tar", "gztar","bztar", or "xztar".
# pack_dir='result'
# shutil.rmtree(pack_dir,ignore_errors=True)
# os.makedirs(pack_dir,exist_ok=True)
# shutil.make_archive("result/ret","zip",base_dir=output_dir)
# log(f"result is:result/ret.zip")
logAndClose("finished.")