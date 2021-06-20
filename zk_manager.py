# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
from zk import ZK, const

NO_JOBS=0
ERROR=1
COMMIT=2#COMMIT,OK
NO_HANDLED=3
SUPERUSER_ID=1

class ZkManager(object):
    
    def __init__(self,ip,port=4370,timeout=5,verbose=False):        
        self.conn = None
        self.zk = ZK(ip, port=port, timeout=timeout,verbose=verbose)
    
    def _log(self,msg):
		if self.verbose:
			print(msg)
        
    def __get_info_user(self,user):
       return {
            "UID":user.id,
            "Name":user.name,
            "Privilege":user.privilege
        }
        
    def __get_info_zk(self,conn):
        return {
            'Firmware Version':conn.get_firmware_version(),
            'Serial Number':conn.get_serialnumber(),
            'Platform':conn.get_platform(),
            'MAC':conn.get_mac(),
            'Device Name':conn.get_device_name(),
            'Face Version':conn.get_face_version(),
            'FingerPrint Name':conn.get_fp_version()           
        }
    
    def get_device_info(self):
        values={"info":None,"status":NO_JOBS,"message":None}
        if self.zk:
            try:
                self.conn = self.zk.connect()
                self.conn.disable_device()
                info=self.__get_info_zk(self.conn)
                values["info"]=info                
                self.conn.enable_device()
                values["status"]=COMMIT
                values["message"]="OK"
            except Exception as e:
                values["info"]=None                
                values["status"]=ERROR
                values["message"]=str(e)               
            finally:
                if self.conn:
                    self.conn.disconnect()
        return values
    
    def get_user_info(self,uid):
        values={"info":None,"status":NO_JOBS,"message":None}
        if self.zk:
            try:
                self.conn = self.zk.connect()
                self.conn.disable_device()
                exists_test,exists_user=self.exists(uid)
                if exists_test:
                    info=self.__get_info_user(exists_user)
                    values["info"]=info                
                self.conn.enable_device()
                values["status"]=COMMIT
                values["message"]="OK"
            except Exception as e:
                values["info"]=None                
                values["status"]=ERROR
                values["message"]=str(e)               
            finally:
                if self.conn:
                    self.conn.disconnect()
        return values
       
    def get_users(self):
        values={"users":{},"status":NO_JOBS,"message":None}
        if self.zk:
            try:
                self.conn = self.zk.connect()
                self.conn.disable_device()
                users = self.conn.get_users()
                user_maps={}
                for user in users:
                    user_maps[user.uid]=user
                values["users"]=user_maps                
                self.conn.enable_device()
                values["status"]=COMMIT
                values["message"]="OK"
            except Exception as e:
                values["users"]=None                
                values["status"]=ERROR
                values["message"]=str(e)               
            finally:
                if self.conn:
                    self.conn.disconnect()
        return values
    
    def _exists(self,users,uid):
        if users:
            for user in users:
                if(user.uid==uid):
                    return (True,user)
        return (False,None)
    
    def exists(self,uid):
        users = self.conn.get_users()
        exists_test,exists_user=self._exists(users, uid)
        return exists_test,exists_user
        
    def create_user(self,uid,name, privilege=0, password='1234', group_id='', user_id=False, card=0):
        values={"user":None,
                "status":NO_JOBS,
                "message":None}
        if self.zk:
            try:
                self.conn = self.zk.connect()
                self.conn.disable_device()
                if not user_id:
                    user_id=str(uid)
                exists_test,exists_user=self.exists(uid)
                if not exists_test:
                    self.zk.set_user(uid=uid, name=name, privilege=privilege, password=password, group_id=group_id, user_id=user_id, card=card)
                    exists_test,exists_user=self.exists(uid)   
                    if exists_test:
                        values["user"]=exists_user
                        values["status"]=COMMIT
                        values["message"]="CREATED"
                else:
                    values["user"]=exists_user
                    values["status"]=NO_HANDLED
                    values["message"]="ALREADY EXISTS"
                self.conn.enable_device()                              
            except Exception as e:
                values["user"]=None                
                values["status"]=ERROR
                values["message"]=str(e)               
            finally:
                if self.conn:
                    self.conn.disconnect()
        return values
    
    def write_user(self,uid,name, privilege=False, password=False, group_id=False, card=False):
        values={"user":None,
                "status":NO_JOBS,
                "message":None}
        if self.zk:
            try:
                self.conn = self.zk.connect()
                self.conn.disable_device()
                exists_test,exists_user=self.exists(uid)
                if not exists_test:
                    values["message"]="USER NOT FOUND"
                else:   
                    privilege=privilege or exists_user.privilege
                    password=password or exists_user.password
                    group_id=group_id or exists_user.group_id
                    card=card or exists_user.card
                    self.zk.set_user(uid=uid, name=name, privilege=privilege, password=password, group_id=group_id, user_id=exists_user.user_id, card=card)
                    exists_test,exists_user=self.exists(uid)
                    values["user"]=exists_user
                    values["status"]=COMMIT
                    values["message"]="UPDATED"
                self.conn.enable_device()                              
            except Exception as e:
                values["user"]=None                
                values["status"]=ERROR
                values["message"]=str(e)               
            finally:
                if self.conn:
                    self.conn.disconnect()
        return values
    
    def get_attendances(self):
        values={"attendances":None,
                "status":NO_JOBS,
                "message":None}
        if self.zk:
            try:
                self.conn = self.zk.connect()
                self.conn.disable_device()
                attendances=self.conn.get_attendance()                
                self.conn.enable_device()             
                values["attendances"]=attendances                
                values["status"]=COMMIT
                values["message"]="OK"                 
            except Exception as e:
                values["attendances"]=None                
                values["status"]=ERROR
                values["message"]=str(e)               
            finally:
                if self.conn:
                    self.conn.disconnect()
        return values
    
    def clear_attendances(self):
        values={"attendances":None,
                "status":NO_JOBS,
                "message":None}
        if self.zk:
            try:
                self.conn = self.zk.connect()
                self.conn.disable_device()
                attendances=self.conn.get_attendance()   
                self.conn.clear_attendance()             
                self.conn.enable_device()             
                values["attendances"]=attendances                
                values["status"]=COMMIT
                values["message"]="OK"                 
            except Exception as e:
                values["attendances"]=None                
                values["status"]=ERROR
                values["message"]=str(e)               
            finally:
                if self.conn:
                    self.conn.disconnect()
        return values
    
    def delete_user(self,uid):
        values={"user":None,
                "status":NO_JOBS,
                "message":None}
        if self.zk:
            try:
                self.conn = self.zk.connect()
                self.conn.disable_device()
                exists_test,exists_user=self.exists(uid)
                if not exists_test:
                    values["message"]="USER NOT FOUND"
                else: 
                    self.zk.delete_user(uid, exists_user.user_id)               
                    values["user"]=exists_user                
                    values["status"]=COMMIT
                    values["message"]="OK" 
                self.conn.enable_device()                 
            except Exception as e:
                values["user"]=None                
                values["status"]=ERROR
                values["message"]=str(e)               
            finally:
                if self.conn:
                    self.conn.disconnect()
        return values
    
    def delete_users(self):
        values={"users":None,
                "status":NO_JOBS,
                "message":None}
        if self.zk:
            try:
                self.conn = self.zk.connect()
                self.conn.disable_device()
                users = self.conn.get_users()
                for user in users:
                    if(user.uid!=SUPERUSER_ID):
                        self.zk.delete_user(user.uid, user.user_id)
                values["users"]=users                
                values["status"]=COMMIT
                values["message"]="OK"
                self.conn.enable_device()                
            except Exception as e:
                values["users"]=None                
                values["status"]=ERROR
                values["message"]=str(e)               
            finally:
                if self.conn:
                    self.conn.disconnect()
        return values
    
    def take_fingerprint(self,uid,finger):
        #finger 0-9 
        values={"user":None,
                "status":NO_JOBS,
                "message":None}
        if(finger<0 or finger>9):
            values["status"]=ERROR
            values["message"]="footprints range from 0 to 9 (left to right)"            
            return values
        if self.zk:
            try:
                self.conn = self.zk.connect()
                self.conn.disable_device()
                exists_test,exists_user=self.exists(uid)
                if not exists_test:
                    values["message"]="USER NOT FOUND"
                else:
                    values["user"]=exists_user 
                    self.conn.delete_user_template(uid, finger)
                    self.conn.reg_event(0xFFFF) #
                    values["status"]=NO_HANDLED
                    values["message"]="ENROLLING USER"
                    self._log("ENROLLING USER {}...".format(uid))
                    result_enroll=self.conn.enroll_user(uid, finger)
                    self._log(result_enroll)
                    if result_enroll:
                        self.conn.test_voice(0) # register ok
                        tem = self.conn.get_user_template(uid, finger)                                       
                        self.__log(tem)
                        values["status"]=COMMIT
                        values["message"]="OK"
                    else:
                        values["status"]=ERROR
                        values["message"]="REINTENTE CON LA TOMA DE HUELLAS"
                        self.conn.test_voice(4) # not registered
                self.conn.enable_device()                
            except Exception as e:
                values["user"]=None                
                values["status"]=ERROR
                values["message"]=str(e)               
            finally:
                if self.conn:
                    self.conn.disconnect()
        return values
