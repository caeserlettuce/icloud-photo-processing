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
import zipfile
import shutil
import ffmpeg
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
  "photo": ["png", "jpg", "jpeg", "heic", "gif"], #i know gif is a video file but it should be treated like a photo for reasons lmao
  "video": ["mp4", "mov", "avi"]
}

input_folder = "in"
output_folder = "out"

month_folder_names = {
  1: "01 january",
  2: "02 february",
  3: "03 march",
  4: "04 april",
  5: "05 may",
  6: "06 june",
  7: "07 july",
  8: "08 august",
  9: "09 september",
  10: "10 october",
  11: "11 november",
  12: "12 december"
}

def exit_handler():
  print(bc.GREEN + "t'as been closed" + bc.END)

settings = json.load(open('settings.json'.encode()))

def folder_check(folder):
  exists = os.path.exists(folder)
  if (exists != True):
    print(bc.GREEN + bc.UNDERLINE + folder + bc.END + bc.BLUE + " does not exist! making folder..." + bc.END)
    os.mkdir(folder)

folder_check("in")
folder_check("out")

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
  if (name_info["type"].lower() in filetype_groups["photo"]):
    exif = Image.open(path)._getexif()
    if exif and 36867 in exif:
      info_out["metadate"] = exif[36867]
    else:
      info_out["metadate"] = False
  elif (name_info["type"].lower() in filetype_groups["video"]):
    video_metadata = ffmpeg.probe(path)["streams"]
    if type(video_metadata) == type([]):
     for i in video_metadata:
       if "tags" in i:
         # has tags!!
         if "creation_time" in i["tags"]:
           # has video created!!!! tag!!! metadata!!!! omg!!!
           info_out["vidodate"] = str(i["tags"]["creation_time"]).split(".")[0]
    else:
     if "tags" in video_metadata:
       # has tags!!
       if "creation_time" in video_metadata["tags"]:
         # has video created!!!! tag!!! metadata!!!! omg!!!
         info_out["vidodate"] = str(video_metadata["tags"]["creation_time"]).split(".")[0]

  info_out["filedate"] = time.ctime(os.path.getmtime(path))
  if (info_out.get("vidodate", False) == False):
    info_out["vidodate"] = False
  if (info_out.get("metadate", False) == False):
    info_out["metadate"] = False
  if (info_out.get("filedate", False) == False):
    info_out["filedate"] = False
  return info_out

def get_size(start_path = '.'):
  total_size = 0
  for dirpath, dirnames, filenames in os.walk(start_path):
    for f in filenames:
      fp = os.path.join(dirpath, f)
      # skip if it is symbolic link
      if not os.path.islink(fp):
        total_size += os.path.getsize(fp)
  return total_size

def convert_size(size_bytes):
  if size_bytes == 0:
    return "0B"
  size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
  i = int(math.floor(math.log(size_bytes, 1024)))
  p = math.pow(1024, i)
  s = round(size_bytes / p, 2)
  return "%s %s" % (s, size_name[i])

print(bc.HEADER + "processing the photos now!!!" + bc.END) # yippee!!

big_file_list = os.listdir(input_folder)

start_files_size = get_size(input_folder)


def process_file(filename):
  print("processing file " + filename + "...")

  if settings["sort by month/year"] == True:
    # sort
    info = get_file_info(os.path.join(input_folder, filename), get_filename_info(filename))  # the info
    metadate = False
    filedate = False
    vidodate = False

    if info["metadate"] != False:
      metadate = datetime.strptime(info["metadate"], "%Y:%m:%d %H:%M:%S")
    if info["filedate"] != False:
      filedate = datetime.strptime(info["filedate"], "%a %b %d %H:%M:%S %Y")
    if info["vidodate"] != False:
      vidodate = datetime.strptime(info["vidodate"], "%Y-%m-%dT%H:%M:%S")
    print(bc.BLUE + "metadate: " + bc.GREEN + str(metadate) + bc.END)
    print(bc.BLUE + "filedate: " + bc.GREEN + str(filedate) + bc.END)
    print(bc.BLUE + "vidodate: " + bc.GREEN + str(vidodate) + bc.END)
    month = 0
    year = 0
    if metadate == False and vidodate == False:
      if settings["use modified date as backup"] == True:
        month = filedate.month
        year = filedate.year
      else:
        month = False
        year = False
    elif metadate == False and vidodate != False:
      month = vidodate.month
      year = vidodate.year
    else:
      month = metadate.month
      year = metadate.year
    print(bc.BLUE + "month: " + bc.GREEN + bc.UNDERLINE + str(month) + bc.END)
    print(bc.BLUE + "year: " + bc.GREEN + bc.UNDERLINE + str(year) + bc.END)

    if type(year) != type(1):
      # no year!!
      year = "unknown"
    if month in month_folder_names:
      month = month_folder_names[month]
    else:
      # no month!!
      month = False

    folder_check(os.path.join(output_folder, str(year)))              # check year folder
    if (month != False):
      folder_check(os.path.join(output_folder, str(year), str(month)))  # check month folder
      if settings["output to iphone folders"] == True:
        folder_check(os.path.join(output_folder, str(year), str(month), "iphone"))  # check iphone folder
    else:
      if settings["output to iphone folders"] == True:
        folder_check(os.path.join(output_folder, str(year), "iphone"))  # check iphone folder
    
    print(bc.GREEN + "saving file " + bc.BLUE + bc.UNDERLINE + filename + bc.END + bc.GREEN + "!" + bc.END)
    if (month == False):
      if settings["output to iphone folders"] == True:
        shutil.move(os.path.join(input_folder, filename), os.path.join(output_folder, str(year), "iphone", filename))
      else:
        shutil.move(os.path.join(input_folder, filename), os.path.join(output_folder, str(year), filename))
    else:
      if settings["output to iphone folders"] == True:
        shutil.move(os.path.join(input_folder, filename), os.path.join(output_folder, str(year), str(month), "iphone", filename))
      else:
        shutil.move(os.path.join(input_folder, filename), os.path.join(output_folder, str(year), str(month), filename))
  else:
    # dont sort
    print(bc.GREEN + "saving file " + bc.BLUE + bc.UNDERLINE + filename + bc.END + bc.GREEN + "!" + bc.END)
    shutil.move(os.path.join(input_folder, filename), os.path.join(output_folder, filename))



for filename in big_file_list:
  f_path = os.path.join(input_folder, filename)
  nameinfo = get_filename_info(filename)

  if (nameinfo["type"].lower() in filetype_groups["archive"]):  # archive file
    zip = zipfile.ZipFile(f_path)
    for file in zip.namelist():
      print(file)
      if file.startswith('iCloud Photos/'):
        zip.extract(file, input_folder)

    
    for filename in os.listdir(os.path.join(input_folder, 'iCloud Photos')):
      shutil.move(os.path.join(input_folder, 'iCloud Photos', filename), os.path.join(input_folder, filename))
    os.rmdir(os.path.join(input_folder, 'iCloud Photos'))
    os.remove(f_path)

big_file_list = os.listdir(input_folder)

file_process_list = []

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
    file_process_list.append(filename)
  elif (nameinfo["type"].lower() in filetype_groups["video"] ): # video file
    print(bc.CYAN + "it's a video file!" + bc.END)
    if settings["delete live photos"] == True:
      # delete if matching file
      possible_name = nameinfo["name"] + ".JPG"
      print(possible_name)
      if os.path.exists(os.path.join(input_folder, possible_name)):
        # it exists!
        print(bc.WARNING + "photo " + bc.UNDERLINE + possible_name + bc.END + bc.WARNING + " exists! deleting the video.")
        os.remove(f_path)
      else:
        file_process_list.append(filename)
    else:
      file_process_list.append(filename)

for file in file_process_list:  # if i make it process in the function above, the live video deletey thing doesnt work cause itll move the photos before the videos
  process_file(file)



end_files_size = get_size(output_folder)

if (start_files_size == end_files_size):
  print( bc.BOLD + bc.HEADER +"\ndone! :)" + bc.END)
  print( bc.BOLD + bc.BLUE + "\n total size: " + bc.END + bc.GREEN + str(convert_size(end_files_size)) + bc.END)
else:
  print( bc.BOLD + bc.HEADER + "\ndone! :)" + bc.END)
  print( bc.BOLD + bc.BLUE + "\n start size: " + bc.END + bc.GREEN + str(convert_size(start_files_size)) + bc.END)
  print( bc.BOLD + bc.BLUE + "   end size: " + bc.END + bc.GREEN + str(convert_size(end_files_size)) + bc.END)
  print( bc.BOLD + bc.BLUE + "space saved: " + bc.END + bc.GREEN + str(convert_size(start_files_size - end_files_size)) + bc.END)