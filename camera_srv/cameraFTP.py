#!/usr/bin/python3
# -*- coding: utf-8 -*-


# Remark: in order to create the thumbnail and to convert the video the "avconv" need to be installed on the server
# the software is present in the following library: "libav-tools" --> sudo apt-get install libav-tools

#pure-ftp configuration:
# In the file /etc/default/pure-ftpd-common modify the following line:
#	   UPLOADSCRIPT=/<script path>/cameraFTP.py

import sys, os

sys.path.append ('/home/ftp/Env/userftp/lib/python3.5/site-packages')
sys.path.append ('/home/hc/Env/uat/lib/python3.5/site-packages')
sys.path.append ('/home/hc/uat/hc/lib')
sys.path.append ('/home/hc/uat/hc/climax_web')
sys.path.append ('/home/hc/uat/hc/climax_svr')
sys.path.append ('/home/hc/uat/hc/climax_notif')


sys.path.append ('/home/marc/workspace2/hc/climax_web')
sys.path.append ('/home/marc/workspace2/hc/climax_svr')
sys.path.append ('/home/marc/workspace2/hc/climax_notif')


import shutil
import datetime
import subprocess
import getpass

from HCsettings import HcDB, EventCode, HcLog, HcFTP

from GW_DB.Dj_Server_DB import DB_mngt
from notifier import send_notification

import logging
from logging.handlers import TimedRotatingFileHandler



VIDEO_STORAGE = HcFTP.config("VIDEO_STORAGE")
MAX_FILES = HcFTP.config("MAX_FILES")


def search_usrprofile_from_CamID( cam_id ):

  req="SELECT prof.user_id, propertyaddr, SN_SMS, SN_Voice, prof.email, language " \
    "FROM camera_camera AS cam, " \
    "auth_user AS auth, " \
    "alarm_userprofile AS prof " \
    "WHERE  auth.id=prof.user_id and cam.user_id=prof.user_id and cam.id=%s;"

  value= (cam_id,)

  db_cursor= DB_mngt(HcDB.config())

  if db_cursor.echec:
    sys.exit(1)

  db_cursor.executerReq(req, value)

  usr_profile = db_cursor.resultatReq()
  db_cursor.close()

  return usr_profile[0]

def do_movevideo(src, dest):
  hclog.info('>>>do_movevideo {}'.format(src) )
  result = False

  try:
    shutil.move(src, dest)

  except IOError as e:
    hclog.info("ERROR: I/O error({0}): {1}, cannot move to {2}".format(e.errno, e.strerror, dest))
    try:
      os.remove(src)
    except OSError as e:
      hclog.info( "ERROR: Cannot delete {0}: OS error: {1}".format(src, os.strerror(e.errno)))
    else:
      hclog.info( "File deleted: {0}".format(src))

  else:
    hclog.info('Succesfully moved from {} to {}'.format(src, dest) )
    try:
      os.chmod(dest, stat.S_IWGRP)
    except Exception as e:
      hclog.info( "ERROR: Cannot change file access: {0}".format(e))
    result=True

  finally:
    hclog.info('<<<do_movevideo')

  return result


def do_search_DB(mac):

  hclog.info('>>>do_search_DB, MAC= {}'.format(mac) )
  db_cursor= DB_mngt(HcDB.config())
  if db_cursor.echec:
    sys.exit(1)

  #retrieving information
#	MAC = '00:0E:8F:96:82:D6'

#Mage 31/12 (user_id added)
#MaGe 11/4 (notificationEnabled added )

  db_cursor.executerReq("""SELECT id, user_id, CameraMac, description, notificationEnabled FROM camera_camera WHERE CameraMac=%s""", (mac,))

  answer = db_cursor.resultatReq()
  db_cursor.close()

  record_nbr = len(answer)

  if record_nbr >1:
    hclog.info('ERROR DB : Multiple entries for MAC= {}'.format(mac) )
    exit()

  elif record_nbr == 0:
    hclog.info("MAC not found")
    rtn_val=[]

  else: # MAC is unique
    rtn_val=answer[0]

  hclog.info('<<<do_search_DB, return camera_id= {}'.format (rtn_val))
  return rtn_val

def do_write_path_DB(cam_params, filepath):

  head, tail = os.path.split(filepath)

  hclog.info('>>>do_write_path_DB: CAM= %s File= {}'.format(cam_params, tail) )

  db_cursor= DB_mngt(HcDB.config())
  if db_cursor.echec:
    sys.exit(1)

# Mage 31/12 : MySql DATETIME values in 'YYYY-MM-DD HH:MM:SS' and MUST be UTC (django applies timez zone afterwards)

  now=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

  # write into history
  req="INSERT INTO {} (timestamp, userWEB_id, type, cameraID_id, event_code, event_description, video_file) VALUES ( %s, %s, %s, %s, %s, %s, %s )".format("history_events")
  value= (now, cam_params[1], "CA", cam_params[0],"800", EventCode.value("800")[0]+" on " + cam_params[3], tail[0:-4], )
  db_cursor.executerReq(req, value)
  db_cursor.commit()

#Mage	record_id=cursor.lastrowid

  # write into camera.file_list

  hclog.info('<<<do_write_path_DB' )

def do_create_vignette(filepath):

#avconv -i 000E8F9AF368123456201605191553170001.avi -f mjpeg -ss 10 -vframes 1 -s 320x240 fichier_vignette.jpg

  FFMPEG_BIN= "avconv"	# need to install: sudo apt-get install libav-tools

  head, tail = os.path.split(filepath)
  hclog.info('>>>do_create_vignette: File= {}'.format(filepath))
  subprocess.call([FFMPEG_BIN, "-y", "-i", filepath, '-f', 'mjpeg', '-ss', '1', '-vframes', '1', '-s', '320x240', filepath[0:-4]+".jpg"] )
  hclog.info('<<<do_create_vignette' )

def do_create_mp4(filepath):

#avconv -i 000E8F9AF368123456201605191553170001.avi -y -strict experimental -s 640x480 -c:v libx264 -c:a aac -ac 2 -ar 8000 -b:a 32k -threads auto test.mp4

    FFMPEG_BIN= "avconv"

    head, tail = os.path.split(filepath)
    hclog.info('>>>do_create_mp4: File= {}'.format(filepath))
    subprocess.call([FFMPEG_BIN, "-y", "-i", filepath, '-strict', 'experimental', '-s', '640x480', '-c:v', 'libx264', '-c:a', 'aac', '-ac', '2','-ar', '8000', '-b:a', '32k', '-threads', 'auto', filepath[0:-4]+".mp4"] )

    hclog.info('<<<do_create_mp4' )

def do_count_record(cam):
  hclog.info('>>>do_count_record for camera id {}'.format(cam))
  db_cursor= DB_mngt(HcDB.config())
  if db_cursor.echec:
    hclog.info('exit ')
    sys.exit(1)
  db_cursor.executerReq("""select count(*) from history_events where cameraID_id = %s and video_file is not null""", (cam,))
  answer = db_cursor.resultatReq()
  db_cursor.close()
  hclog.info("<<<<do_count_record {0}".format(answer[0][0]))
  return answer[0][0]

def do_clean_up_files (cam_params):
  hclog.info('>>>do_clean_up_files')
  camID=cam_params[0]
  while do_count_record(camID) > int(MAX_FILES):
    hclog.info("more than {} files need clean up!".format(MAX_FILES) )
    #extract the oldest file from the db
    db_cursor= DB_mngt(HcDB.config())
    if db_cursor.echec:
      sys.exit(1)
    db_cursor.executerReq("""select id, video_file from history_events where cameraID_id = %s and video_file is not null order by timestamp limit 1""", (camID,))
    (id, file) = db_cursor.resultatReq()[0]

    #delete file . mp4 + .jpg
    try:
      os.remove(VIDEO_STORAGE + file + ".mp4")
    except:
      hclog.info("ERROR: file: {}.mp4 doesn't exist".format(file) )
    try:
      os.remove(VIDEO_STORAGE + file + ".jpg")
    except:
      hclog.info("ERROR: file: {}.jpg doesn't exist".format(file))

    hclog.info("id: {}".format(id) )
    db_cursor.executerReq("""delete from history_events where id = %s""", (id,))
    db_cursor.commit()
    hclog.info("file: {} deleted".format(id) )

  hclog.info('<<<do_clean_up_files' )

def do_MAC_formatting(mac_string):
  hclog.info('>>>do_MAC_formatting' )

  try:
      mac = (':'.join([mac_string[i]+mac_string[i+1] for i in range(0,12,2)]))
  except:
      hclog.info( "ERROR: Invalid MAC string: {0}".format(mac_string) )
      ret = None
  else:
      ret = mac

  hclog.info('<<<do_MAC_formatting' )
  return ret

def main(argv):

	level = "debug"
	
	logPath= HcLog.config("logPath")
	retentionTime = int(HcLog.config("retentionTime"))
	moduleName = "cameraFTP_svr"

	global hclog
	hclog = logging.getLogger()   # must be the rotlogger, otherwise sub-modules will not benefit from the config.
	
	handler = TimedRotatingFileHandler(logPath + moduleName + '.log',
	                              when='midnight',
	                              backupCount=retentionTime)
	if level == 'debug':
	    hclog.setLevel(logging.DEBUG)
	    handler.setLevel(logging.DEBUG)
	else:
	    hclog.setLevel(logging.INFO)
	    handler.setLevel(logging.INFO)
	
	formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s',datefmt='%b %d %H:%M:%S')
	handler.setFormatter(formatter)
	
	hclog.addHandler(handler)


	
	print( "Starting {} with user {}".format( __name__, getpass.getuser() ) )

	for arg in sys.argv:
	    print( arg )
	
	hclog.info("++++ {0} started with UID {1}, GID {2} ++++".format(argv[0],os.getuid(),os.getgid()))
	hclog.info( ("Argument List: {}").format(str(sys.argv)))
	
	#000E8F88C2F1 201209031438030001.avi
	#000E8F9AF368 123456 201605181528390001.avi

	global FTP_file_path
	FTP_file_path = argv[1]
	
	#	MAC_hex=argv[1][len(argv[1])-40:len(argv[1])-28]
	
	head, tail = os.path.split(argv[1])
	
	MAC_hex=tail[0:12]
	MAC_str=do_MAC_formatting(MAC_hex)
	
	timestamp=argv[1][len(argv[1])-22:len(argv[1])-4]
	
	head, tail = os.path.split(argv[1])
	
	hclog.info( ("Camera MAC= {}, Timestamp= {}").format(MAC_str,timestamp))
	
	res=do_search_DB(MAC_str)
	
	if res:
		do_clean_up_files(res)
		if do_movevideo(FTP_file_path, VIDEO_STORAGE+tail ) :
			do_write_path_DB(res, VIDEO_STORAGE+tail)
			do_create_vignette(VIDEO_STORAGE+tail)
			do_create_mp4(VIDEO_STORAGE+tail)
			os.remove(VIDEO_STORAGE+tail)
			
			camID = res[0]
			camName = res[3]
			notificationEnabled = res[4]
			
			if notificationEnabled == 1:
		                          # ( evt, alarmMsg, EventCode.value(evt)[1], sensor_ref_id )
			    notif_flag = EventCode.value("800")[1]	  # '800':("Camera motion detected", ("1", "1", "0")),
			    event=["800","Motion detected on camera: " + camName, notif_flag, camID]
			    profile = search_usrprofile_from_CamID( camID )		# get user profile of the camera owner
			    send_notification( profile, event )
			
			    hclog.info( "{0} successfully terminated".format(argv[0]))
		
		else:
			hclog.info("Issue with video file of camera {0}".format(MAC_str))
			
			try:
				os.remove(FTP_file_path)
			
			except OSError as e:
				hclog.info( "ERROR: Cannot delete: {0}, OS error: {1}".format(FTP_file_path, os.strerror(e.errno)))
			else:
				hclog.info( "File deleted: {0}".format(FTP_file_path))
				hclog.info( "{0} successfully terminated".format(argv[0]))


if __name__ == "__main__":
   main(sys.argv)
