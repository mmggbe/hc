#!/usr/bin/python3
# -*- coding: utf-8 -*-


# Remark: in order to create the thumbnail and to convert the video the "avconv" need to be installed on the server
# the software is present in the following library: "libav-tools" --> sudo apt-get install libav-tools

#pure-ftp configuration:
# In the file /etc/default/pure-ftpd-common modify the following line:
#	   UPLOADSCRIPT=/<script path>/cameraFTP.py
 
import sys, os

sys.path.append ('/home/ftp/Env/userftp/lib/python3.5/site-packages')
sys.path.append ('/home/hc/uat/hc/climax_web')
sys.path.append ('/home/hc/uat/hc/climax_svr')
sys.path.append ('/home/hc/uat/hc/climax_notif')
sys.path.append ('/home/hc/uat/hc/history')

import shutil
import logging
import datetime
import subprocess

from HCsettings import HcDB, EventCode, HcFTP

from GW_DB.Dj_Server_DB import DB_mngt
from notifier import send_notification

LOG_FILE = HcFTP.config("LOG_FILE")

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
	logger.info('>>>do_movevideo %s', src)
	result = False
	
	try:
		shutil.move(src, dest)
		
	except IOError as e:
		logger.info("I/O error({0}): {1}, cannot move to {2}".format(e.errno, e.strerror, dest))
		try:
			os.remove(src)
		except OSError as e:
			logger.info( "Cannot delete {0}: OS error: {1}".format(src, os.strerror(e.errno)))
		else:
			logger.info( "File deleted: {0}".format(src))			
		
	else:
		logger.info('Succesfully moved from %s to %s', src, dest)
		try:
			os.chmod(dest, stat.S_IWGRP)
		except Exception as e:
			logger.info( "Cannot change file access: {0}".format(e))
		result=True
	
	finally:
		logger.info('<<<do_movevideo')
	
	return result


def do_search_DB(mac):
	
	logger.info('>>>do_search_DB, MAC= %s', mac)
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
		logger.error('Multiple entries for MAC= %s', mac)
		exit()
		
	elif record_nbr == 0:
		logger.info("MAC not found")
		rtn_val=[]
		
	else: # MAC is unique
		rtn_val=answer[0]

	logger.info('<<<do_search_DB, return camera_id= %s', rtn_val)
	return rtn_val

def do_write_path_DB(cam_params, filepath):

	head, tail = os.path.split(filepath)
	
	logger.info('>>>do_write_path_DB: CAM= %s File= %s', cam_params, tail)
	
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
	
	logger.info('<<<do_write_path_DB' )

def do_create_vignette(filepath):

#avconv -i 000E8F9AF368123456201605191553170001.avi -f mjpeg -ss 10 -vframes 1 -s 320x240 fichier_vignette.jpg

	FFMPEG_BIN= "avconv"	# need to install: sudo apt-get install libav-tools

	head, tail = os.path.split(filepath)
	logger.info('>>>do_create_vignette: File= %s', filepath)
	subprocess.call([FFMPEG_BIN, "-y", "-i", filepath, '-f', 'mjpeg', '-ss', '1', '-vframes', '1', '-s', '320x240', filepath[0:-4]+".jpg"] )
	logger.info('<<<do_create_vignette' )

def do_create_mp4(filepath):

#avconv -i 000E8F9AF368123456201605191553170001.avi -y -strict experimental -s 640x480 -c:v libx264 -c:a aac -ac 2 -ar 8000 -b:a 32k -threads auto test.mp4

		FFMPEG_BIN= "avconv"

		head, tail = os.path.split(filepath)
		logger.info('>>>do_create_mp4: File= %s', filepath)
		subprocess.call([FFMPEG_BIN, "-y", "-i", filepath, '-strict', 'experimental', '-s', '640x480', '-c:v', 'libx264', '-c:a', 'aac', '-ac', '2','-ar', '8000', '-b:a', '32k', '-threads', 'auto', filepath[0:-4]+".mp4"] )

		logger.info('<<<do_create_mp4' )

def do_count_record(cam):
	logger.info('>>>do_count_record for camera id %s', cam)
	db_cursor= DB_mngt(HcDB.config())
	if db_cursor.echec:
		logger.info('exit ')
		sys.exit(1)	   
	db_cursor.executerReq("""select count(*) from history_events where cameraID_id = %s and video_file is not null""", (cam,))
	answer = db_cursor.resultatReq()
	db_cursor.close()
	logger.info("<<<<do_count_record {0}".format(answer[0][0]))
	return answer[0][0]

def do_clean_up_files (cam_params):
	logger.info('>>>do_delete_file')
	camID=cam_params[0]
	while do_count_record(camID) > int(MAX_FILES):
		logger.info("more than %s files need clean up!", MAX_FILES)
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
			logger.info("file: %s.mp4 doesn't exist", file)
		try:
			os.remove(VIDEO_STORAGE + file + ".jpg")
		except:
			logger.info("file: %s.jpg doesn't exist", file)
			
		logger.info("id: %s", id)
		db_cursor.executerReq("""delete from history_events where id = %s""", (id,))
		db_cursor.commit()
		logger.info("file: %s deleted", id)
	

def do_MAC_formatting(mac_string):
	logger.info('>>>do_MAC_formatting' )

	try:
			mac = (':'.join([mac_string[i]+mac_string[i+1] for i in range(0,12,2)]))
	except:
			logger.info( "Invalid MAC string: {0}".format(mac_string) )
			ret = None
	else:
			ret = mac

	logger.info('<<<do_MAC_formatting' )
	return ret

def main(argv):


	global logger 
	global FTP_file_path

	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)

# create a file handler
	handler = logging.FileHandler(LOG_FILE)
	handler.setLevel(logging.INFO)

# create a logging format
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	handler.setFormatter(formatter)

# add the handlers to the logger
	logger.addHandler(handler)

	for arg in sys.argv:
			print( arg )

	logger.info("++++ {0} started with UID {1}, GID {2} ++++".format(argv[0],os.getuid(),os.getgid()))
	logger.info("path: {0}".format(LOG_FILE))
	logger.info( ("Argument List: {}").format(str(sys.argv)))

#000E8F88C2F1 201209031438030001.avi
#000E8F9AF368 123456 201605181528390001.avi

	FTP_file_path = argv[1]

#	MAC_hex=argv[1][len(argv[1])-40:len(argv[1])-28]

	head, tail = os.path.split(argv[1])

	MAC_hex=tail[0:12]
	MAC_str=do_MAC_formatting(MAC_hex)
			
	timestamp=argv[1][len(argv[1])-22:len(argv[1])-4]

	head, tail = os.path.split(argv[1])

	logger.info( ("Camera MAC= {}, Timestamp= {}").format(MAC_str,timestamp))

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

				logger.info( "{0} successfully terminated".format(argv[0]))

		else:
			logger.info("Issue with video file of camera {0}".format(MAC_str))
				
			try:
				os.remove(FTP_file_path)

			except OSError as e:
				logger.info( "Cannot delete: {0}, OS error: {1}".format(FTP_file_path, os.strerror(e.errno)))
			else:
				logger.info( "File deleted: {0}".format(FTP_file_path))
				logger.info( "{0} successfully terminated".format(argv[0]))
	

if __name__ == "__main__":
   main(sys.argv)
