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
from google.appengine.ext.webapp import template
#from google.appengine.api import rdbms
#from google.appengine.ext import db
from google.appengine.ext import ndb
from Crypto.Cipher import DES
from Crypto.Hash import MD5
from google.appengine.api import users
from google.appengine.api import namespace_manager
import json
import datetime
import time
import base64
import sys
import logging
import random
from dbclass import *
from SessionBaseHandler import *
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


class MainHandler(SessionBaseHandler):
    def get(self):
    	path = self.request.path

    	if doRender(self,path):
    		return

    	doRender(self,'index.html')


class DevelopCenterHandler(SessionBaseHandler):
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

		if path == '/developcenter/appmanager.html':
			if not developer:
				return

		if developer:
			que = DB_App.query(DB_App.developer == developer.key)
			appList = que.fetch()
			values['appList']=appList

		if doRender(self,path,values):
			return

   		doRender(self,'developcenter/index.html',values)
	def post(self):
		path = self.request.path
		

		if path == '/developcenter/createtoken.html':
			values={}
			values['enctoken'] = CommandHandler.encToken(self.request.get('auID'),
													self.request.get('udid'),
													self.request.get('flag'),
													self.request.get('nick'),
													self.request.get('email'),
													self.request.get('platform'),
													self.request.get('createTime'),
													self.request.get('secretKey')
													).replace(" ","")
			arglist=self.request.arguments()
			logging.info(values['enctoken'])
			for arg in arglist:
				values[arg]=self.request.get(arg)

			values['encparam'] = CommandHandler.encParam(self.request.get('param'))

			values['dectoken']= CommandHandler.decToken(values['enctoken'],values['secretKey'])
			values['decparam']= CommandHandler.decParam(values['encparam'])
			doRender(self,path,values)
		if path == '/developcenter/createapp.html':
			user = users.get_current_user()
			developer={}
			if user:
				developer = DB_Developer.get_by_id(user.email())

			if not developer:
				self.response.write('check id')
				return

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
			try:
				newApp.put()
			except Exception, e:
				self.response.write('error : change aID ')
				return
			

			self.response.write('<a href=appmanager.html>appmanager</a>')


config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'hsgraphdogsessionsk',
}

app = webapp2.WSGIApplication([
	('/test',TestHandler),
	('/test/.*',TestHandler),
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
