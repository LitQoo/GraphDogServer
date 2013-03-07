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
import datetime
import time
import base64
import sys
import logging

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
class UniqueConstraintViolation(Exception):
    def __init__(self, scope, value):
        super(UniqueConstraintViolation, self).__init__("Value '%s' is not unique within scope '%s'." % (value, scope, ))

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
	aID = db.StringProperty()
	title = db.StringProperty()
	secretKey = db.StringProperty()
	scoresSortType = db.StringProperty()
	scoresSortValue = db.StringProperty()
	developer = db.ReferenceProperty()
	
	def put(self):
		if DB_Developer.get_by_key_name(self.aID):
			raise UniqueConstraintViolation("aID", self.aID)
		self._key_name = self.aID
		return db.Model.put(self)



class DB_User(db.Model):
	nick = db.StringProperty()
	flag = db.StringProperty()
	udid = db.StringProperty()
	installs = db.StringListProperty()

class _DB_AppUser(db.Model):
	nick = db.StringProperty()
	flag = db.StringProperty()
	uInfo  = db.ReferenceProperty(DB_User)
	createTime = db.StringProperty()
	udid = db.StringProperty()

	@classmethod
	def createClass(cls,aid):
		exec '''class DB_AppUser(_DB_AppUser):
			@classmethod
			def kind(cls):
				return 'app_%s_user'
			''' % aid
		return DB_AppUser

class _DB_AppScore(db.Model):
	auInfo=db.ReferenceProperty(_DB_AppUser)
	userData = db.StringProperty()
	sTime=db.StringProperty()
	uTime=db.StringProperty()
	eTime=db.StringProperty() 
	gType=db.StringProperty()
	score=db.IntegerProperty()
	
	@classmethod
	def createClass(cls,aid):
		exec '''class DB_AppScore(_DB_AppScore):
			@classmethod
			def kind(cls):
				return 'app_%s_score'
			''' % aid
		return DB_AppUser

class DB_AppData(db.Model):
	pass


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
		logging.info('########################### start command ###############################')
		path = self.request.path
		action = self.request.get('action')
		aID = self.request.get('aID')
		token = self.request.get('token')
		param = CommandHandler.decParam(self.request.get('param'))
		auInfo={}
		aInfo={}
		
		if not param:
			param={}

		#find app
		try:
			aInfo = DB_App.get_by_key_name(aID)
		except Exception, e:
			self.printError('dont find app',100)
			return


		#create dbclass
		DB_AppUser =  _DB_AppUser.createClass(aID)

		#dec token
		tokens = CommandHandler.decToken(token,aInfo.secretKey)
		logging.info('tokens : ' + str(tokens))
		cTime = str(int(time.time()))

		#/actionname/?param  && ?action=actionname&param 형식모두지원하기
		if not action:
		 	ga = path.split("/")
		 	if len(ga)>2:
		 		action = ga[2]

		#action 없으면 에러
		if not action:
			self.printError('dont find action',100)
			return
		
		#기본리턴값
		result = {'action':action , 'callback': param.get('callback'), 'createTime':cTime}

		# timestamp action
		if action == 'timestamp':
			result['timestamp'] = int(time.time())
			result['state']='ok'

		# getweek
		if action == 'getweek':
			result['week']=int(datetime.date.today().strftime("%U"))
			

		# start action
		if action == 'start':	#로그인하기
			#auID있으면 au정보 뽑아오기~
			if tokens.get('auID'):
				try:
					logging.info('finded by auID : '+tokens['auID'])
					key = db.Key(tokens['auID'])
					auInfo = DB_AppUser.get(key)
				except Exception, e:
					pass
			

			#auID존재여부확인 , ctime check && uuid check  and appuser.createTime == tokens.get('createTime')
			if auInfo:	#and auInfo.udid == tokens.get('udid')
				logging.info("user finded")
				# name , flag 확인해서 업데이트하기
				if auInfo.nick != tokens.get('nick') or auInfo.flag != tokens.get('flag'):
					logging.info('chage the nick & flag key:'+str(auInfo.uInfo.key()))
					uInfo=DB_User.get(auInfo.uInfo.key())
					uInfo.nick = auInfo.nick = tokens.get('nick')
					uInfo.flag = auInfo.flag = tokens.get('flag')
					uInfo.put()

				#createTime update
					auInfo.createTime=cTime
					auInfo.put()

				#weekly점수 검사후 초기화!##############################
				

			else:	#join 하기
				#udid로 회원테이블뒤지기
				logging.info("user dont finded")
				uInfo = {}
				que = DB_User.all()
				que = que.filter('udid =',tokens.get('udid'))
				find = que.fetch(limit=1)
				
				if len(find)>0: #회원정보찾음
					logging.info("find uid by udid")
					uInfo = find[0]
					if not tokens.get('nick'):
						tokens['nick']=uInfo.nick
						tokens['flag']=uInfo.flag

					#회원정보에서 앱설치한적있는가 찾아보자
					if aID in uInfo.installs:
						q = DB_AppUser.all()
						q = q.filter('uid =',uInfo.key())
						for a in q.run(limit=1):
							logging.info("find auid in installs")
							auInfo = a


				else:	#못찾음
					logging.info("dont find uid by udid")
					#전체회원가입
					uInfo = DB_User();
					uInfo.nick = tokens.get('nick')
					uInfo.flag = tokens.get('flag')
					uInfo.udid = tokens.get('udid')
					uInfo.put()

				
				if not auInfo: #앱정보없으면 앱회원가입
					logging.info("join appuser")
					auInfo = DB_AppUser()
					auInfo.nick = tokens.get('nick')
					auInfo.flag = tokens.get('flag')
					auInfo.udid = tokens.get('udid')
					auInfo.uInfo = uInfo.key()
					auInfo.put()

					#인스톨즈 업데이트
					uInfo.installs.append(aID)
					uInfo.put()

					result['isFirst']=True
					#cpiEvents체크

			#결과리턴~
			result['tokenUpdate']='ok';
			result['state']='ok';
			result['nick']=tokens.get('nick')
			result['flag']=tokens.get('flag')
			result['auid']=str(auInfo.key())
			self.session['aID']=aID
			self.session['auID']=str(auInfo.key())
			#nextaction

		#login 검사
		if not self.session.get('aID') or not self.session.get('auID'):
			self.printError('error',100)

		#action startscores
		if action == 'getflagranks':#점수시작~
			logging.info('startscores')


		#action startscores
		if action == 'startscores':#점수시작~
			logging.info('startscores')
		#param ->  type, score, userdata, 
			gType = param.get('type')
			if not gType:
				gType = 'defalut'
			
			asInfo = DB_AppScore()
			asInfo.gType = gType
			asInfo.score = int(param.get('score'))
			asInfo.auInfo = auInfo.key()


			# 설정에 따라 기준id찾기
	# //여기서 사람수기준이면 설정사람수번째 id를 얻어오기, 설정사람수보다 사람이 적을경우 제일먼사람
	# $_result=array();
	# if($aInfo['scoresSortType']=="people"){
	# 	$mongo->selectDB("APP".$aID);
	# 	$asTable=$mongo->getCollection("scores");
	# 	$cursor=$asTable->find()->sort(array("_id"=>-1))->skip($aInfo['scoresSortValue'])->limit(1);
	# 	if($cursor->hasNext()){
	# 		$_result=$cursor->getNext();	
	# 	}else{
	# 		$cursor=$asTable->find()->sort(array("_id"=>-1))->limit(1);
	# 		$_result=$cursor->getNext();
	# 	}			
	
	# //여기서 시간기준이면 설정시간으로부터 가장 앞에있는 사람 id를 asTimeId에 저장
	# }else if($aInfo['scoresSortType']=="time"){
	# 	$mongo->selectDB("APP".$aID);
	# 	$asTable=$mongo->getCollection("scores");
	# 	$cursor=$asTable->find(
	# 							array(
	# 									"sTime"=>array('$gt'=>($cTime-$aInfo['scoresSortValue']))
	# 								  )
	# 						   )->sort(array("_id"=>1))->limit(1);
	# 	$_result=$cursor->getNext();
	# }


			#세션에 asID저장
			#세션에 asSortId 저장
			#세션에 gType 저장
			#result[state]='ok'

		#결과리턴
		self.response.write(json.dumps(result))
		
		logging.info('########################### end command ###############################')
		
	def get(self):
		self.post()

	@classmethod
	def decParam(cls,param):
		re={}
		try:
			re = base64.decodestring(param)
			re = json.loads(re) #json.dumps
		except Exception, e:
			return re
		return re
	
	@classmethod
	def encParam(cls,paramstr):
		re = base64.encodestring(paramstr)
		return re

	@classmethod
	def decToken(cls,token,skey):
		re={}
		try:
			token=token.replace(" ","+")
			to = base64.decodestring(token)
			to = to + ' '*(8-len(to)%8)
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
	
	@classmethod
	def encToken(cls,auID,udid,flag,nick,email,platform,createTime,skey):
		token = str(auID)+'||'+str(udid)+'||'+str(flag)+'||'+str(nick)+'||'+str(email)+'||'+str(platform)+'||'+str(createTime)+'||'
		token = token + ' '*(8-len(token)%8)
		obj = DES.new(skey,DES.MODE_ECB)
		token = obj.encrypt(token)
		token = base64.encodestring(token)
		return token

	def printError(self,msg,code):
		re = {'state':'error', 'msg':msg, 'errorcode':code}
		self.response.write(json.dumps(re))
		

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
			que = DB_App.all()
			que = que.filter('developer =',developer.key())
			appList = que.fetch(limit=100)
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
													self.request.get('secretkey')
													).replace(" ","")
			arglist=self.request.arguments()
			logging.info(values['enctoken'])
			for arg in arglist:
				values[arg]=self.request.get(arg)

			values['encparam'] = CommandHandler.encParam(self.request.get('param'))

			values['dectoken']= CommandHandler.decToken(values['enctoken'],values['secretkey'])
			values['decparam']= CommandHandler.decParam(values['encparam'])
			doRender(self,path,values)
		if path == '/developcenter/createapp.html':
			user = users.get_current_user()
			developer={}
			if user:
				developer = DB_Developer.get_by_key_name(user.email())

			if not developer:
				self.response.write('check id')
				return

			newApp = DB_App();
			newApp.aID = self.request.get('aID')
			newApp.title = self.request.get('title')
			newApp.secretKey = self.request.get('secretKey')
			newApp.scoresSortType = self.request.get('scoresSortType')
			newApp.scoresSortValue = self.request.get('scoresSortValue')
			newApp.developer = developer.key()
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
