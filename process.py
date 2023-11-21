from datetime import datetime
import os, sys
import json
import atexit
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS, GPSTAGS
import math
import random
import logging
import time
now = datetime.now()


# this is designed for zip files ONLY from icloud, so any other zip files may not work!!!

class bc:
  HEADER = '\033[95m'
  BLUE = '\033[94m'
  CYAN = '\033[96m'
  GREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  END = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

filetype_groups = {   # capitals dont matter, it compares them all in lowercase
  "archive": ["zip"],
  "photo": ["png", "jpg", "jpeg", "heic"],
  "video": ["mp4", "mov", "avi"]
}

input_folder = "in"

def exit_handler():
  print(bc.GREEN + "t'as been closed" + bc.END)

settings = json.load(open('settings.json'.encode()))


atexit.register(exit_handler)

def get_filename_info(filename):
  info_out = {}
  split = filename.split(".")               # split filename by "."
  info_out["type"] = split[len(split) - 1]  # get the last bit of text after "." (the file extension)
  split_copy = split.copy()                 # make a copy of split
  split_copy.pop()                          # remove the last element (the file extension)
  info_out["name"] = ".".join(split_copy)   # join the rest back together with dots (this is just in case there are dots in the file NAME but arent related to the extension)
  return info_out                           # return

def get_file_info(path, name_info):
  info_out = {}
  if (name_info["type"].lower() in filetype_groups["photo"] or name_info["type"].lower() in filetype_groups["video"]):

    exif = Image.open(path)._getexif()
    if not exif:
      info_out["metadate"] = False
    else:
      info_out["metadate"] = exif[36867]
  info_out["filedate"] = time.ctime(os.path.getmtime(path))
  return info_out

print(bc.HEADER + "processing the photos now!!!") # yippee!!

big_file_list = os.listdir(input_folder)


for filename in big_file_list:
  f_path = os.path.join(input_folder, filename)
  nameinfo = get_filename_info(filename)

  print(bc.BLUE + "\ninfo for " + bc.UNDERLINE + bc.GREEN + filename + bc.END + bc.BLUE + ":" + bc.END)
  print(bc.BLUE + str(nameinfo) + bc.END)

  fileinfo = get_file_info(f_path, nameinfo)

  print(bc.BLUE + str(fileinfo) + bc.END)



  if (nameinfo["type"].lower() in filetype_groups["archive"]):  # archive file
    print(bc.CYAN + "it's an archive file!" + bc.END)

  elif (nameinfo["type"].lower() in filetype_groups["photo"] ): # photo file
    print(bc.CYAN + "it's a photo file!" + bc.END)

  elif (nameinfo["type"].lower() in filetype_groups["video"] ): # video file
    print(bc.CYAN + "it's a video file!" + bc.END)



