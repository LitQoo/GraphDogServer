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
from google.appengine.ext import db
from webapp2_extras import sessions
from Crypto.Cipher import DES
from Crypto.Hash import MD5
from google.appengine.api import users
import json
import base64
import time

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

#############################################################################
# session
#############################################################################
class SessionBaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the datastore.
        return self.session_store.get_session(backend='datastore')

#############################################################################
# database class
#############################################################################

class DB_Developer(db.Model):
	email = db.StringProperty()
	name = db.StringProperty()
	password = db.StringProperty()

	def put(self):
		if DB_Developer.get_by_key_name(self.email):
			raise UniqueConstraintViolation("email", self.email)
		self._key_name = self.email
		return db.Model.put(self)

class DB_App(db.Model):
	title = db.StringProperty()
	secretKey = db.StringProperty()
	scoresSortType = db.StringProperty()
	scoresSortValue = db.StringProperty()
	developer = db.ReferenceProperty()

class DB_User(db.Model):
	nick = db.StringProperty()
	flag = db.StringProperty()
	udid = db.StringProperty()

class DB_AppUser(db.Model):
	nick = db.StringProperty()
	flag = db.StringProperty()
	uid = db.ReferenceProperty()


class DB_AppScore(db.Model):
	pass

class DB_AppData(db.Model):
	pass

class UniqueConstraintViolation(Exception):
    def __init__(self, scope, value):
        super(UniqueConstraintViolation, self).__init__("Value '%s' is not unique within scope '%s'." % (value, scope, ))
#############################################################################
# handler
#############################################################################


class MainHandler(SessionBaseHandler):
    def get(self):
    	path = self.request.path

    	if doRender(self,path):
    		return

    	doRender(self,'index.html')

class CommandHandler(SessionBaseHandler):
	def post(self):
		path = self.request.path
		action = self.request.get('action')
		aid = self.request.get('aid')
		token = self.request.get('token')
		param = self.decParam(self.request.get('param'))
		
		#find app
		try:
			ak = db.Key(aid)
			app = DB_App.get(ak)
		except Exception, e:
			self.response.write('''{"state":"error","error":"dont find app"}''')
			return

		#dec token
		tokens = self.decToken(token,'GDSK5438')

		cTime = time.time()


		# if not param.get('callback'):
		# 	param['callback']=0

		result = {'action':action , 'callback': param.get('callback')}

		t = int(time.time())
		self.response.write('timestamp:'+str(t))

		# for k in param:
		# 	self.response.write(k + ' : ' + param[k] + '<br>')

	def get(self):
		self.post()

	def decParam(self,param):
		try:
			re = base64.decodestring(param)
			re = json.loads(re) #json.dumps
		except Exception, e:
			return ''
		return re
	def decToken(self,token,skey):
		re={}
		try:
			token=token.replace(" ","+")
			to = base64.decodestring(token)
			#to = to + ' '*(8-len(to)%8)
			obj = DES.new(skey,DES.MODE_ECB)
			to=obj.decrypt(to)
			to=to.split('||')
			re['auID']=to[0]
			re['udid']=to[1]
			re['flag']=to[2]
			re['nick']=to[3]
			re['email']=to[4]
			re['platform']=to[5]
			re['createTime']=to[6]
		except Exception, e:
			return re
		return re

# GDSK5428
#http://localhost:8080/command/?action=start&aid=agxkZXZ-Z3JhcGhkb2dyDAsSBkRCX0FwcBgyDA&param=ewoJIm5leHRBY3Rpb24iIDogImdldFJlcXVlc3RzIiwKCSJuZXh0UGFyYW0iIDogewoJCSJ0eXBlIiA6ICJhbGwiCgl9Cn0=&token=7QfVMt4f3eA0ja+TRsPkfggmtYGnRH9oNyD8kAJ+lSQJoOIXomjmgNiVICaG4QyfDJE93cZDqgy78qbLB48EhoW+P+lUFGMG14vCI8ANnUMdYcx3KEXsYA==
#test action=start&aID=5124e0b9ae52a09358000031&param=ewoJIm5leHRBY3Rpb24iIDogImdldFJlcXVlc3RzIiwKCSJuZXh0UGFyYW0iIDogewoJCSJ0eXBlIiA6ICJhbGwiCgl9Cn0=&token=7QfVMt4f3eA0ja+TRsPkfggmtYGnRH9oNyD8kAJ+lSQJoOIXomjmgNiVICaG4QyfDJE93cZDqgy78qbLB48EhoW+P+lUFGMG14vCI8ANnUMdYcx3KEXsYA==
class DevelopCenterHandler(SessionBaseHandler):
	def get(self):
		path = self.request.path
		values = {}
		user = users.get_current_user()
		
		developer={}
		if user:
			developer = DB_Developer.get_by_key_name(user.email())


		#check email and join
		if path == '/developcenter/login':
			if not developer:
				self.response.write('welcome to join')
				developer = DB_Developer()
				developer.name = user.nickname()
				developer.email = user.email()
				developer.put() 

		if developer:
			values['developer_email']=developer.email
			values['developer_nickname']=developer.name
		
		values['loginurl'] = users.create_login_url("/developcenter/login")
		values['logouturl'] = users.create_logout_url("/developcenter/logout")

		if path == '/developcenter/appmanager.html':
			if not developer:
				return
			que = db.Query(DB_App)
			que = que.filter('developer =',developer.key())
			appList = que.fetch(limit=100)
			values['appList']=appList

		if doRender(self,path,values):
			return

   		doRender(self,'developcenter/index.html',values)
	def post(self):
		path = self.request.path
		if path == '/developcenter/createapp.html':
			user = users.get_current_user()
			developer={}
			if user:
				developer = DB_Developer.get_by_key_name(user.email())

			if not developer:
				self.response.write('check id')
				return

			newApp = DB_App();
			newApp.title = self.request.get('title')
			newApp.secretKey = self.request.get('secretKey')
			newApp.scoresSortType = self.request.get('scoresSortType')
			newApp.scoresSortValue = self.request.get('scoresSortValue')
			newApp.developer = developer.key()
			newApp.put()

			self.response.write('<a href=appmanager>appmanager</a>')


config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'hsgraphdogsessionsk',
}

app = webapp2.WSGIApplication([
	('/developcenter', DevelopCenterHandler),
	('/developcenter/.*', DevelopCenterHandler),
	('/command', CommandHandler),
	('/command/.*', CommandHandler),
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
