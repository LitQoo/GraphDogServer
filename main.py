# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
from google.appengine.ext import webapp
from google.appengine.api import images
from google.appengine.ext.webapp import template
import urllib
#from google.appengine.api import rdbms
#from google.appengine.ext import db
from google.appengine.ext import ndb
from Crypto.Cipher import DES
from Crypto.Hash import MD5
from Crypto import Random

from google.appengine.api import users
from google.appengine.api import namespace_manager
import json
import datetime
import time
import base64
import sys
import logging
import random
import string
from dbclass import *
from SessionBaseHandler import *
from command1 import CommandHandler

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.api import memcache

#render function
def doRender(handler,tname='index.html',values={}):
	temp = os.path.join(
    	os.path.dirname(__file__),
    	'templates/'+tname)
	if not os.path.isfile(temp):
		return False

	newval = dict(values)
	newval['path']=handler.request.path

	
	outstr = template.render(temp,newval)
	handler.response.write(outstr)
	return True

#def rdbms_connection(DATA_NAME,USER_NAME,PASSWORD):
	#return rdbms.connection(instance=CLOUDSQL_INSTANCE, database=DATA_NAME,user=USER_NAME, password=PASSWORD, charset='utf8')

#############################################################################
# handler
#############################################################################


class TestHandler(SessionBaseHandler):
	def p(self,v):
		self.response.write(str(v)+"<br>")

	def cs(self,stats,ns):
		for category in stats:
			if type(stats[category])==list:
				for idx, val in enumerate(stats[category]):
					if stats[category][idx] < ns[category][idx]:
						stats[category][idx]=ns[category][idx]
						self.p('update list')

			elif type(stats[category])==dict:
				for key in stats[category]:
					stats[category][key]+=ns[category][key]
					ns[category][key]=0		

		self.p('result stats')
		self.p(stats)

		self.p('result new stats')
		self.p(ns)
		self.p('')
		return (stats,ns)

	def get(self):
		self.response.write('welcome to test')
		stats = {'join': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'hit': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'update': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'platform': {'android': 0, 'ios': 0}}
		ns = {'join': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0], 'hit': [0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 33, 0, 0, 0, 0], 'update': [0, 0, 0, 0, 0, 44, 0, 0, 0, 0, 0, 0, 0, 0, 0, 33, 0, 0, 0, 1, 0, 0, 0, 0], 'platform': {'android': 22, 'ios': 0}}

		self.cs(stats,ns)

		ns = {'join': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 4, 10, 0, 0, 0], 'hit': [0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 33, 0, 0, 0, 0], 'update': [0, 0, 0, 0, 0, 44, 0, 0, 0, 0, 0, 0, 0, 0, 0, 33, 0, 0, 0, 1, 0, 0, 0, 0], 'platform': {'android': 22, 'ios': 0}}

		self.cs(stats,ns)


		ns = {'join': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'hit': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'update': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'platform': {'android': 0, 'ios': 0}}

		self.cs(stats,ns)


class MainHandler(SessionBaseHandler):
    def get(self):
    	path = self.request.path
    	if doRender(self,path):
    		return

    	doRender(self,'index.html')


class DevelopCenterHandler(SessionBaseHandler):
	@classmethod
	def createGiftcode(size=10, chars=string.ascii_uppercase):
		return ''.join(random.choice(chars) for x in range(10))

	def get(self):
		path = self.request.path
		values = {}
		user = users.get_current_user()
		developer={}
		


		if user:
			developer=ndb.Key('DB_Developer',user.email()).get()
		
		if not developer and user:
			developer = DB_Developer(id=user.email())
			developer.name = user.nickname()
			developer.email = user.email()
			developer.put()
			
		if developer:
			values['developer_email']=developer.email
			values['developer_nickname']=developer.name

		values['loginurl'] = users.create_login_url("/developcenter")
		values['logouturl'] = users.create_logout_url("/developcenter")


		if path == '/developcenter/index.html' or path == '/developcenter' or  path == '/developcenter/':
			doRender(self,'/developcenter/index.html',values)
			return
			
		if path == '/developcenter/reference.html':	####################################################################
			doRender(self,'/developcenter/reference.html',values)
			return

		if path == '/developcenter/desDecoder.html':	####################################################################
			doRender(self,'/developcenter/desDecoder.html',values)
			return

		if path == '/developcenter/jsonForm.html':	####################################################################
			doRender(self,'/developcenter/jsonForm.html',values)
			return

		if path == '/developcenter/jsoneditor.html':	####################################################################
			values['input']=self.request.get('input')
			values['valuename']=self.request.get('valuename')
			values['keyname']=self.request.get('keyname')
			doRender(self,'/developcenter/jsoneditor.html',values)
			return
		
		if not developer:
			return

		aID = self.request.get('aID')
		values['user']=user

		localtime = time.asctime( time.localtime(time.time()) )
		values['localtime'] = localtime

		if aID:
			gdNamespace = namespace_manager.get_namespace()
			appNamespace = 'APP_'+aID
			aInfo = DB_App.get_by_id(aID)
			values['aInfo'] = aInfo
			values['aInfo'].store = json.dumps(values.get('aInfo').store,encoding="utf-8",ensure_ascii=False)
			values['aInfo'].cpiReward = json.dumps(values.get('aInfo').cpiReward,encoding="utf-8",ensure_ascii=False)
			values['aInfo'].descript = json.dumps(values.get('aInfo').descript,encoding="utf-8",ensure_ascii=False)
			values['aID']=aID;

			if aInfo.developer != developer.key:
				return

		if path == '/developcenter/test':

			namespace_manager.set_namespace(appNamespace)
			'''au = DB_AppUser()
			au.nick=DevelopCenterHandler.createGiftcode()
			au.flag=DevelopCenterHandler.createGiftcode()
			au.udid=DevelopCenterHandler.createGiftcode()
			au.put()
			self.response.write('ok')'''

			alog = DB_AppLog()
			alog.category = 'efg'
			alog.text = DevelopCenterHandler.createGiftcode()
			alog.version = 3
			alog.put()

			return

		filterfield = self.request.get('filterfield')
		filtervalue = self.request.get('filtervalue')
		limit = self.request.get('limit')
		if not limit: limit=30
		else: limit=int(limit)
		values['filtervalue'] = filtervalue
		values['filterfield'] = filterfield
		values['limit'] = limit

		if path == '/developcenter/appmanager.html':	####################################################################
			values['appList'] = DB_App.query(DB_App.developer == developer.key).fetch()
		
		if path == '/developcenter/appView_version.html':		####################################################################
			namespace_manager.set_namespace(appNamespace)

		if path == '/developcenter/appView_notice.html':		####################################################################
			namespace_manager.set_namespace(appNamespace)
			

		if path == '/developcenter/appView_user.html':		####################################################################
			namespace_manager.set_namespace(appNamespace)


		if path == '/developcenter/appView_log.html':		####################################################################
			namespace_manager.set_namespace(appNamespace)
			if filterfield=='auid':
				auserkey = DB_AppUser.get_by_id(int(filtervalue)) #ndb.Key('DB_AppUser',auser).get()
				values['auInfo']=auserkey

			##logList = DB_AppLog.query().order(-DB_AppLog.time).fetch()


		if path == '/developcenter/appView_data.html': ############################################################################
			namespace_manager.set_namespace(appNamespace)
			db = self.request.get('db')
			mode = self.request.get('mode')
			dataid = self.request.get('id')
			curs = Cursor(urlsafe=self.request.get('cursor'))

			if not limit: limit=30
			else: limit=int(limit)
			datalist=[]
			jsondata={}
			

			if mode == "delete":
				data = ndb.Key(db,dataid).get()
				if not data: data = ndb.Key(db,int(dataid)).get()
				if data:
					logging.info(data.to_dict())
					data.key.delete()
					self.response.write('{"result":"ok"}')
				return

			if mode == "edit":
				datafield = self.request.get('field')
				datavalue = self.request.get('value')
				logging.info("#############################a")
				logging.info(datafield)
				logging.info(datavalue)
				logging.info("#############################b")
				data = ndb.Key(db,dataid).get()
				if not data: data = ndb.Key(db,int(dataid)).get()
				if data:

					try:
						if (type(datavalue)==str or type(datavalue)==unicode) and datavalue[0]=="{" and datavalue[-1]=="}":
							logging.info('its json')
							datavalue=json.loads(datavalue)
							logging.info(datavalue)
					except:
						pass

					try:
						exec('data.'+datafield+' = datavalue')
					except:
						exec('data.'+datafield+' = int(datavalue)')
					data.put()
					self.response.write('{"result":"ok"}')
				return

			if db == 'DB_AppLog': # ----------------------------------------------------------------------------------
				if filterfield=='auid':
					auserkey = ndb.Key('DB_AppUser', int(filtervalue))
					datalist, next_curs, more=DB_AppLog.query(DB_AppLog.auInfo==auserkey).order(-DB_AppLog.time).fetch_page(limit, start_cursor=curs)
				elif filterfield=='category':
					datalist, next_curs, more=DB_AppLog.query(DB_AppLog.category==filtervalue).order(-DB_AppLog.time).fetch_page(limit, start_cursor=curs)
				else:
					datalist, next_curs, more=DB_AppLog.query().order(-DB_AppLog.time).fetch_page(limit, start_cursor=curs)

			if db == 'DB_AppUser': # ----------------------------------------------------------------------------------
				datalist, next_curs, more=DB_AppUser.query().order(-DB_AppUser.joinDate).fetch_page(limit, start_cursor=curs)

			if db == 'DB_AppStats': # ----------------------------------------------------------------------------------
				datalist, next_curs, more=DB_AppStats.query().order(-DB_AppStats.ymd).fetch_page(limit, start_cursor=curs)
				todaynumber = int(time.strftime("%Y%m%d", time.localtime(time.time())))
				todayStat = DB_AppStats(statsData = DB_AppStats.getInMC(), ymd=todaynumber)
				datalist.insert(0,todayStat)
			
			if db == 'DB_AppStage': # ----------------------------------------------------------------------------------
				datalist, next_curs, more=DB_AppStage.query().order(-DB_AppStage.createTime).fetch_page(limit, start_cursor=curs)
			
			if db == 'DB_AppNotice': # ----------------------------------------------------------------------------------
				datalist, next_curs, more=DB_AppNotice.query().order(-DB_AppNotice.createTime).fetch_page(limit, start_cursor=curs)

			if db == 'DB_AppGiftcode': # ----------------------------------------------------------------------------------
				datalist, next_curs, more=DB_AppGiftcode.query().order(-DB_AppGiftcode.createTime).fetch_page(limit, start_cursor=curs)

			if db == 'DB_AppVersions': # ----------------------------------------------------------------------------------
				datalist, next_curs, more=DB_AppVersions.query().order(-DB_AppVersions.createTime).fetch_page(limit, start_cursor=curs)

			if db == 'DB_AppFeedback': # ----------------------------------------------------------------------------------
				if filterfield=='sender':
					auserkey = ndb.Key('DB_AppUser', int(filtervalue))
					datalist, next_curs, more=DB_AppFeedback.query(DB_AppFeedback.sender==auserkey).order(-DB_AppFeedback.createTime).fetch_page(limit, start_cursor=curs)
				else:
					datalist, next_curs, more=DB_AppFeedback.query().order(-DB_AppFeedback.createTime).fetch_page(limit, start_cursor=curs)

			jsondata['list'] = []
			for f in datalist:
			  jsondata['list'].append(f.toResult())

			jsondata['filtervalue'] = filtervalue
			jsondata['filterfield'] = filterfield
			if next_curs: jsondata['cursor'] = str(next_curs.urlsafe())
			else: jsondata['cursor']= ""
			jsondata['aID'] = aID
			jsondata['more'] = more
			jsondata['limit'] = limit
			result= json.dumps(jsondata,encoding="utf-8",ensure_ascii=False)
			#result = json.encode(values)
			self.response.write(result)
			return
		if path == '/developcenter/appView_giftcode.html':		####################################################################
			namespace_manager.set_namespace(appNamespace)

		if path == '/developcenter/appView_rank.html':		####################################################################
			namespace_manager.set_namespace(appNamespace)
			setSqlConnect(aid=aInfo.aID,instance=aInfo.dbInstance)

			curs = Cursor(urlsafe=self.request.get('cursor'))
			limit = self.request.get('limit')
			auser = self.request.get('auser')

			if not limit:
				limit=30
			else:
				limit=int(limit)
			rankList=[]
			if auser:
				rankList = DB_AppScores.query("WHERE auInfo="+str(auser)+" ORDER BY no desc LIMIT "+str(limit))
			else:
				rankList = DB_AppScores.query("ORDER BY no desc LIMIT "+str(limit))
				
			values['rankList']=[]
			for row in rankList:
				sinfo = DB_AppScores.set(row)
				sinfo.sTime = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(sinfo.sTime))
				values['rankList'].append(sinfo)

			values['limit'] = limit
			values['auser'] = auser
			sqlClose()

		if path == '/developcenter/appView_stats.html':		####################################################################
			namespace_manager.set_namespace(appNamespace)


		if path == '/developcenter/appView_stages.html':		####################################################################
			namespace_manager.set_namespace(appNamespace)

		if doRender(self,path,values):
			return


   		#doRender(self,'developcenter/index.html',values)
	def post(self):
		path = self.request.path
		aID = self.request.get('aID')
		gdNamespace = namespace_manager.get_namespace()
		appNamespace = 'APP_'+aID
		values={}
		aInfo = {}
		logging.info('post start')
		if aID:
			aInfo = DB_App.get_by_id(aID)
			values['aInfo'] = aInfo
			values['aID']=aID

		user = users.get_current_user()
		developer={}
		
		if user:
			developer = DB_Developer.get_by_id(user.email())

		if not developer:
			self.response.write('check id')
			return

		if path == '/developcenter/jsonForm.html':#########################################
			logging.info('jsonForm test ####################################')
			logging.info(self.request)
			self.response.write(self.request)
			logging.info('jsonForm test ####################################')
			doRender(self,'/developcenter/jsonForm.html',values)
			return
		if path == '/developcenter/desDecoder.html':	####################################################################
			sKey = self.request.get('sKey')
			crytMode = self.request.get('crytMode')
			mode = self.request.get('mode')
			logging.info(mode)
			if mode == 'decode':
				logging.info('decode')
				encodeTxt = self.request.get('fromTxt')
				encodeTxt= encodeTxt.replace(" ","+")
				if encodeTxt:
					to = base64.decodestring(encodeTxt)
					logging.info("base64 decode")
					logging.info(to)
					sKey=sKey.ljust(8,' ')

					if len(to)%8>0:
						to = to + ' '*(8-len(to)%8)
					logging.info(to)

					if crytMode=='ECB':
						logging.info('ECBMODE')
						obj = DES.new(sKey,DES.MODE_ECB)
					elif crytMode=='CBC':
						logging.info('CBCMODE')
						iv = '12345678'
						obj = DES.new(sKey,DES.MODE_CBC,iv)
					else:
						obj = DES.new(sKey,DES.MODE_ECB)
					
					decodetxt=obj.decrypt(to)

					values['toTxt']=decodetxt
					values['sKey']=sKey
					values['fromTxt']=encodeTxt
			else:
				logging.info('encode')
				encodeTxt = self.request.get('fromTxt')
				encodeTxt= encodeTxt.replace(" ","+")
				if encodeTxt:
					to = encodeTxt
					logging.info("base64 decode")
					logging.info(to)
					sKey=sKey.ljust(8,' ')
					
					if len(to)%8>0:
						to = to + ' '*(8-len(to)%8)

					logging.info(to)

					if crytMode=='ECB':
						logging.info('ECBMODE')
						obj = DES.new(sKey,DES.MODE_ECB)
					elif crytMode=='CBC':
						logging.info('CBCMODE')
						iv = '12345678'
						obj = DES.new(sKey,DES.MODE_CBC,iv)
					else:
						obj = DES.new(sKey,DES.MODE_ECB)
					
					decodetxt=obj.encrypt(to)
					decodetxt=base64.encodestring(decodetxt)
					values['toTxt']=decodetxt
					values['sKey']=sKey
					values['fromTxt']=encodeTxt

			doRender(self,'/developcenter/desDecoder.html',values)
			return

		if path == '/developcenter/createapp.html':#########################################
			namespace_manager.set_namespace(gdNamespace)

			newApp = ndb.Key('DB_App',self.request.get('aID')).get()
			if not newApp:
				newApp = DB_App(id=self.request.get('aID'))
			else:
				self.response.write('check aID')
				return
			newApp.aID = self.request.get('aID')
			newApp.title = self.request.get('title')
			newApp.secretKey = self.request.get('secretKey')
			#newApp.scoresSortType = self.request.get('scoresSortType')
			newApp.scoresSortValue = int(self.request.get('scoresSortValue'))
			newApp.developer = developer.key

			global GD_CLOUDSQL_CONNECT
			
			newApp.dbInstance = GD_CLOUDSQL_CONNECT

			try:
				newApp.put()
			except Exception, e:
				self.response.write('error : change aID')
				return

			try:
				createDatabaseAndConnect(aid=newApp.aID,instance=CLOUDSQL_INSTANCE)
				DB_AppScores.createTable()
				DB_AppWeeklyScores.createTable()
				DB_AppMaxScores.createTable()
			except:
				self.response.write("score db did not created <br>")
			self.response.write('<a href=appmanager.html>appmanager</a>')
		if path == '/developcenter/appView.html': #####################################
			if not aInfo:
				self.response.write('check aID')
				return
			namespace_manager.set_namespace(gdNamespace)
			aInfo.title = self.request.get('title')
			aInfo.group = self.request.get('group')
			aInfo.secretKey = self.request.get('secretKey')
			aInfo.scoresSortValue = int(self.request.get('scoresSortValue'))
			aInfo.useCPI = bool(self.request.get('useCPI'))
			aInfo.bannerImg = self.request.get('bannerImg')
			aInfo.iconImg = self.request.get('iconImg')

			aInfo.store = json.loads(self.request.get('store'))
			aInfo.descript = json.loads(self.request.get('descript'))
			aInfo.cpiReward = json.loads(self.request.get('cpiReward'))
			aInfo.put()

			#values['aInfo'] = aInfo
			
			self.redirect(path+"?aID="+self.request.get('aID'))
			#doRender(self,path,values)

				


		if path == '/developcenter/appView_explorer.html': ######################################
			values['enctoken'] = CommandHandler.encToken(self.request.get('auID'),
													self.request.get('udid'),
													self.request.get('flag'),
													self.request.get('lang'),
													self.request.get('nick'),
													self.request.get('email'),
													self.request.get('platform'),
													self.request.get('createTime'),
													self.request.get('secretKey')
													).replace(" ","")
			arglist=self.request.arguments()
			for arg in arglist:
				values[arg]=self.request.get(arg)

			values['encparam'] = CommandHandler.encParam(self.request.get('param'))

			values['dectoken']= CommandHandler.decToken(values['enctoken'],values['secretKey'])
			values['decparam']= CommandHandler.decParam(values['encparam'])
			

			self.redirect(path+"?aID="+self.request.get('aID'))
			#doRender(self,path,values)

		if path =='/developcenter/appView_notice.html':######################################
			namespace_manager.set_namespace(appNamespace)
			newNotice = DB_AppNotice()
			newNotice.title=self.request.get('title')
			newNotice.category=self.request.get('category')
			if self.request.get('content'):
				newNotice.content=json.loads(self.request.get('content'))
			if self.request.get('userdata'):
				logging.info(self.request.get('userdata'))
				newNotice.userdata=json.loads(self.request.get('userdata'))
			newNotice.platform=self.request.get('platform')
			newNotice.createTime = int(time.time())
			newNotice.put()
			values['msg']='save new data'
			
			self.redirect(path+"?aID="+self.request.get('aID'))
			#doRender(self,path,values)

		if path =='/developcenter/appView_giftcode.html':######################################
			namespace_manager.set_namespace(appNamespace)
			count = int(self.request.get('count'))

			while count is not 0 :
				codelist = ''
				code = DevelopCenterHandler.createGiftcode()
				newGiftcode = DB_AppGiftcode.get_or_insert(code)
				if not newGiftcode.value:
					newGiftcode.category=self.request.get('category')
					newGiftcode.value=int(self.request.get('value'))
					newGiftcode.code=code
					newGiftcode.createTime =int(time.time())
					if self.request.get('userdata'):
						newGiftcode.userdata = json.loads(self.request.get('userdata'))
					newGiftcode.put()
					codelist = codelist + code + ' <br>' 
					count-=1
			
			values['msg']= "created giftcode category:"+self.request.get('category')+"<br> value:"+self.request.get('value')+"<br>"+ codelist
			
			self.redirect(path+"?aID="+self.request.get('aID'))
			#doRender(self,path,values)

		if path =='/developcenter/appView_stages.html':######################################
			namespace_manager.set_namespace(appNamespace)
			newRow = DB_AppStage()
			newRow.stage=self.request.get('stage')
			newRow.category=self.request.get('category')
			if self.request.get('userdata'):
				newRow.userdata=json.loads(self.request.get('userdata'))
			newRow.put()
			values['msg']='save new data'
			self.redirect(path+"?aID="+self.request.get('aID'))
			#doRender(self,path,values)
		
		if path =='/developcenter/appView_feedback.html':######################################
			namespace_manager.set_namespace(appNamespace)
			auid = self.request.get('userid')
			touser =  DB_AppUser.get_by_id(int(auid))
			if not touser:
				self.response.write('do not find user')
				return


			newfeed = DB_AppFeedback()
			newfeed.sender = touser.key
			newfeed.category = self.request.get('category')
			newfeed.content = self.request.get('content')
			newfeed.mode = "send"
			if self.request.get('userdata'):
				newfeed.userdata=json.loads(self.request.get('userdata'))
			newfeed.put()

			newRequest = {}
			newRequest['rid'] = newfeed.key.id()
			newRequest['sender'] = {'type':'app','id':aInfo.key.id(),'name':aInfo.title}
			newRequest['category'] = newfeed.category
			newRequest['content'] = newfeed.content
			newRequest['userdata']=newfeed.userdata
			touser.requests.insert(0,newRequest)
			touser.put()


			self.redirect(path+"?aID="+self.request.get('aID'))

class ImageUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):

    upload_files = self.get_uploads('file')

    if not upload_files:
    	self.redirect('/developcenter/imageselector/?input='+self.request.get('input'))
    	return

    logging.info(upload_files)
    blob_info = upload_files[0]
    

    user = users.get_current_user()
    newImg = DB_AppImage()
    newImg.developer = user
    newImg.imageName = str(blob_info.key())
    newImg.put()
    self.redirect('/developcenter/imageselector/?input='+self.request.get('input'))



  def get(self):
	user = users.get_current_user()
	mode = self.request.get('mode')

	uploadUrl = blobstore.create_upload_url('/developcenter/imageselector')
	
	
  	imagelist =  DB_AppImage.query()
  	for img in imagelist:
  		imgurl = images.get_serving_url(img.imageName)
  		img.imgurl=imgurl

  	values={}
  	values['images']=imagelist
  	
  	#logging.info(images.get_serving_url(blob_info.key()))
  	values['input']=self.request.get('input')
  	values['imgUploadUrl']=uploadUrl
	doRender(self,'/developcenter/imageselector.html',values)

class ImageServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'hsgraphdogsessionsk',
}

app = webapp2.WSGIApplication([
	('/test',TestHandler),
	('/test/.*',TestHandler),
	('/developcenter/imageselector', ImageUploadHandler),
	('/developcenter/imageselector/', ImageUploadHandler),
    ('/imageview/([^/]+)?', ImageServeHandler),
	('/developcenter', DevelopCenterHandler),
	('/developcenter/.*', DevelopCenterHandler),
	('/.*', MainHandler)
],
config=config,
debug=True)




#############################
##한글
##############################
		# 세션
    	# foo = self.session.get('foo')
    	# if not foo:
    	# 	foo = 0
    	
    	# self.response.write('foo : ' + str(foo) + '<br>')

    	# foo=foo+1
    	# self.session['foo'] = foo


    	# 데이터스토어 테이블명 마음대로 하기
    	# exec '''class testdb(DB_App):
    	# 	@classmethod
    	# 	def kind(cls):
    	# 		return 'app_agxkZXZ-Z3JhcGhkb2dyDAsSBkRCX0FwcBgzDA_score'
    	# 	'''
    	# exec '''testuser = testdb()'''
    	# testuser.title = 'title'
    	# testuser.put()
