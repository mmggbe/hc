#!/usr/bin/env python3
# -*- coding:Utf8 -*-
'''
Created on 15 août 2016

@author: marc
'''

""" need to create DB 1st :

sudo mysql -u root -p
 
pwd homeauto given at MariaDB configuration
CREATE DATABASE climax_gw CHARACTER SET UTF8;
CREATE USER gw@localhost IDENTIFIED BY 'test';
GRANT ALL PRIVILEGES ON climax_gw.* TO gw@localhost;
FLUSH PRIVILEGES;
exit

use climax_gw;
show tables;
show columns in gateways;

INSERT INTO gateway (userID,gwMAC) VALUES ("usr001","00:1D:94:03:0F:16");

DELETE from sensors where sensorID >0;
select * from gw_sensors;

UPDATE alarm_gateways SET mac="00:1D:94:03:0F:61" WHERE id=2;

The simple way would be to disable the foreign key check; make the changes then re-enable foreign key check.

SET FOREIGN_KEY_CHECKS=0; -- to disable them
SET FOREIGN_KEY_CHECKS=1; -- to re-enable them



ALTER TABLE alarm_gateways DROP COLUMN userWEB_id

show open tables;
DROP TABLE gateways ;

To repair DB
mysqlcheck -u root --password=homeauto --auto-repair --check --all-databases

to restart mysql
sudo service mysql restart


To show/list the users in a MySQL database, first log into your MySQL server as an administrative user using the mysql client, then run this MySQL query:
mysql> select * from mysql.user;


sudo pip3 install mysql-connector-python-2.0.4.zip 

"""



import mysql.connector as mariadb
import sys
import time
import logging
import configparser

"""
class Glob:

    dbName = "climax_gw"      # nom de la base de données
    user = "gw"              # propriétaire ou utilisateur
    passwd = "test"            # mot de passe d'accès
#    host = "127.0.0.1"          # nom ou adresse IP du serveur
#    port =5432
"""
 
class DB_mngt:
    def __init__(self, configFileName ):
        
        config = configparser.ConfigParser()
        config.read(configFileName)
        params = config['database']
        
        #"DB cursor creation"
        try:
            self.DB = mariadb.connect(user=params['user'], password=params['password'],
                              host=params['host'],
                              database=params['database'])
            
            #self.DB = mariadb.connect(database=dbName,
            #                                  user=user, password=passwd)

        except Exception as err:
            print('DB connection failed :\n'\
                  'Error is:\n%s' % err)
            self.echec =1
        else:
            self.cursor = self.DB.cursor()   # création du curseur
            self.echec =0

 
    def executerReq(self, req, param =None):
        "Exécution de la requête <req>, avec détection d'erreur éventuelle"
        try:
            self.cursor.execute(req, param)
        except Exception as err:
            # afficher la requête et le message d'erreur système :
            print("Invalid SQL request :\n{}\nError:".format(req))
            print(err)
            return 0
        else:
            return 1

    def resultatReq(self):
        "renvoie le résultat de la requête précédente (une liste de tuples)"
        return self.cursor.fetchall()
        
    def resultatReqOneRec(self):
        "send back only one record"
        return self.cursor.fetchone()

    def commit(self):
        if self.DB:
            self.DB.commit()         # transfert curseur -> disque

    def close(self):
        if self.DB:
            self.DB.close()


class DB_gw:  
            
    def __init__(self, db ):
        self.db =db
        self.table ="alarm_gateways"
  
    def search_gw_from_acct(self, rptipid, acct2 ):
#select id FROM alarm_gateways WHERE rptipid  = 730 and acct2= 104

        req="SELECT id FROM {} WHERE rptipid  = %s AND acct2 = %s;".format(self.table)
        value= (rptipid, acct2,)
        self.db.executerReq(req, value)
        gw_id = self.db.resultatReq() # returns a tuple
        return gw_id
        
  
    def search_gw(self, MAC):
#SELECT mac, acct2 FROM gateways WHERE mac = '01:02:02:03:03:06';

        req="SELECT mac, acct2, id, userID, rptipid FROM {} WHERE mac = %s;".format(self.table)

        value= ( MAC,)

        record_nbr=0
#        if self.db.executerReq(req, value):
        if self.db.executerReq(req, value):
            # analyse the result 
            records = self.db.resultatReq()      # returns a tuple of tuples
            for rec in records:             
                record_nbr +=1
#                for item in rec:            
#                    print(item, end=' ')
#                print()
                if record_nbr >1 :
                    print("ERROD DB : Redundant GW %s", rec)
                    return None
                else:
                    return rec
        return 0    
        
    def upd_polling_gw(self, MAC, mode ):
        
        req="UPDATE {} SET  mode= %s WHERE mac = %s;".format(self.table)
        value= ( mode, MAC )
        self.db.executerReq(req, value)
        self.db.commit() 
        
    def upd_cmd_id_gw(self, gw_id, cmd_id):
        
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        req="UPDATE {} SET lastSeenTimestamp = %s, last_cmd_id = %s WHERE id = %s;".format(self.table)
        value= ( now, cmd_id, gw_id )
        self.db.executerReq(req, value)
        self.db.commit() 
        
    def upd_account_gw(self, MAC, rptipid, acct2 ):
        
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        req="UPDATE {} SET registrationDatec = %s, rptipid = %s, acct2 = %s WHERE mac = %s;".format(self.table)
        value= ( now, rptipid, acct2, MAC )
        self.db.executerReq(req, value)
        self.db.commit() 
        
    def get_last_cmdID(self, gw_id):
        req="SELECT last_cmd_id FROM {} WHERE id = %s;".format(self.table)
        value= ( gw_id, )
        self.db.executerReq(req, value)
        
        last_cmdID=self.db.resultatReq() # returns a tuple
        if len( last_cmdID ) > 0 :
            req="UPDATE {} SET last_cmd_id = %s WHERE id = %s;".format(self.table)
            value= ( 1 + last_cmdID[0][0], gw_id )
            self.db.executerReq(req, value)
            self.db.commit()        
            
            return last_cmdID [0][0]
        else: 
            return "9999"

###### Programme principal : #########
def main(argv):
    
    # Création de l'objet-interface avec la base de données :
    db = DB_mngt("config.ini")
    if db.echec:
        sys.exit()
    
    while 1:
        print("\nQue voulez-vous faire :\n"\
              "1) Lister les gateways\n"\
              "2) Lister les sensors\n"\
              "3) Run a SQL query\n"\
              "4) Search GW \n"\
              "5) Get last cmdID of GW \n"\
              "9) Terminate ?                         Votre choix :" , end=' ')
        
        ch = int(input())
        if ch ==1 or ch ==2:
            # listage de tous les compositeurs, ou toutes les oeuvres :
            table ={1:'alarm_gateways', 2:'alarm_sensors'}[ch]
            if db.executerReq("SELECT * FROM %s" % table):
                # analyser le résultat de la requête ci-dessus :
                records = db.resultatReq()      # ce sera un tuple de tuples
                for rec in records:             # => chaque enregistrement
                    for item in rec:            # => chaque champ dans l'enreg.
                        print(item, end=' ')
                    print()
        elif ch ==3:
            req =input("Enter SQL query : ")
            if db.executerReq(req):
                tmp=db.resultatReq()
                print(tmp)          # ce sera un tuple de tuples
        
        elif ch ==4:
            req =input("Enter GW MAC (xx:xx:xx:xx:xx:xx) : ")
            gw_ptr=DB_gw(db)
            tmp=gw_ptr.search_gw(req)
            print(tmp)          # ce sera un tuple de tuples
            
        elif ch ==5:
            req =input("Enter GW ID : ")
            gw_ptr=DB_gw(db)
            tmp=gw_ptr.get_last_cmdID(req);  
            print("Cmd ID= {}".format(tmp))
                        
        
        else:
            db.commit()
            db.close()
            break
    print("End")

if __name__ == "__main__":
    main(sys.argv)
        