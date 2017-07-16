#!/usr/bin/python3
# -*- coding: utf-8 -*-


# Remark: in order to create the thumbnail and to convert the video the "avconv" need to be installed on the server
# the software is present in the following library: "libav-tools" --> sudo apt-get install libav-tools

import mysql.connector as mariadb
import shutil
import sys, os
import logging
import time
import subprocess


#VIDEO_STORAGE= "/home/storage/"
#LOG_FILE= "/home/marc/workspace/FTPCam/FTPCamera.log"
VIDEO_STORAGE= "/home/hc/cam/hc/climax_web/media/"
LOG_FILE= "/home/ftp/cameraFTP.log"

DBUSER= "hc"
DBPASSWD= "HCMGGDB9"
DB="hcdb_branch_cam"

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
		result=True
	
	finally:
		logger.info('<<<do_movevideo')
	
	return result


def do_search_DB(mac):
	
	logger.info('>>>do_search_DB, MAC= %s', mac)
	
	mariadb_connection = mariadb.connect(user=DBUSER, password=DBPASSWD, database=DB)
	cursor = mariadb_connection.cursor()

	#retrieving information
#	MAC = '00:0E:8F:96:82:D6'
	cursor.execute("SELECT id, CameraMac, description FROM camera_camera WHERE CameraMac=%s", (mac,))

	record_nbr=0
	for id, CameraMAC, description in cursor:
		logger.info(("Camera found: camera_id= {}, MAC= {} Description= {}").format(id,CameraMAC, description))
		record_nbr +=1

	if record_nbr >1:
		logger.error('Multiple entries for MAC= %s', mac)
		mariadb_connection.close()

		exit()
		
	elif record_nbr == 0:

		logger.info("MAC not found")

		rtn_val=None
		
	else:
		rtn_val=id
			
	mariadb_connection.close()
	logger.info('<<<do_search_DB, return camera_id= %s', rtn_val)
	return rtn_val

def do_write_path_DB(camera_id, filepath):

	head, tail = os.path.split(filepath)
	
	logger.info('>>>do_write_path_DB: CAM= %s File= %s', camera_id, tail)
	
	mariadb_connection = mariadb.connect(user=DBUSER, password=DBPASSWD, database=DB)
	cursor = mariadb_connection.cursor()

# MySql DATETIME values in 'YYYY-MM-DD HH:MM:SS'
	now = time.strftime("%Y-%m-%d %H:%M:%S")
	
	cursor.execute("INSERT INTO camera_file_list (timestamp,filename,camera_id) VALUES (%s,%s,%s)", (now, tail[0:-4],camera_id))

	mariadb_connection.commit()
	mariadb_connection.close()
	
	logger.info('<<<do_write_path_DB' )

def do_create_vignette(filepath):

#avconv -i 000E8F9AF368123456201605191553170001.avi -f mjpeg -ss 10 -vframes 1 -s 320x240 fichier_vignette.jpg

	FFMPEG_BIN= "avconv"

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
	logger.info( ("Argument List: {}").format(str(sys.argv)))

#000E8F88C2F1 201209031438030001.avi
#000E8F9AF368 123456 201605181528390001.avi

	#FTP_file_path = argv[1]

##	MAC_hex=argv[1][len(argv[1])-40:len(argv[1])-28]
	
	#head, tail = os.path.split(argv[1])

	#MAC_hex=tail[0:12]
	#MAC_str=do_MAC_formatting(MAC_hex)
		
	#timestamp=argv[1][len(argv[1])-22:len(argv[1])-4]
	
	#head, tail = os.path.split(argv[1])

	#logger.info( ("Camera MAC= {}, Timestamp= {}").format(MAC_str,timestamp))

	#res=0
	#res=do_search_DB(MAC_str)
	#if res:
		#if do_movevideo(FTP_file_path, VIDEO_STORAGE+tail ) :
			#do_write_path_DB(res, VIDEO_STORAGE+tail)					
			#do_create_vignette(VIDEO_STORAGE+tail)
			#do_create_mp4(VIDEO_STORAGE+tail)
			#os.remove(VIDEO_STORAGE+tail)
			#logger.info( "{0} successfully terminated".format(argv[0]))

	#else:
		#logger.info("Camera {0} not registered".format(MAC_str))
			
		#try:
			#os.remove(FTP_file_path)

		#except OSError as e:
			#logger.info( "Cannot delete: {0}, OS error: {1}".format(FTP_file_path, os.strerror(e.errno)))
		#else:
			#logger.info( "File deleted: {0}".format(FTP_file_path))
			#logger.info( "{0} successfully terminated".format(argv[0]))		
	

if __name__ == "__main__":
   main(sys.argv)

