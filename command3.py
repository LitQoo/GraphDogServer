# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
#	보내는것 받는것 모두 암호화~!
#
#
#
#

import os
import webapp2
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
#from google.appengine.api import rdbms
#from google.appengine.ext import db
from google.appengine.ext import ndb
from webapp2_extras import sessions
from Crypto.Cipher import DES
from Crypto.Hash import MD5
from google.appengine.api import users
from google.appengine.api import namespace_manager
import datetime
import time
import base64
import sys
import logging
import random
import string
import copy
from dbclass import *
from SessionBaseHandler import *

class CommandHandler(SessionBaseHandler):
	def post(self):
		logging.info('self.request')
		logging.info(self.request)
		logging.info('self.request.POST')
		logging.info(self.request.POST)

		token = self.request.get('token')
		version = self.request.get('appver')
		path = self.request.path
		pathArray = path.split("/")
		aID = pathArray[3]
		cTime = int(time.time())
		auInfo={}
		aInfo={}
		param={}
		allresult={}
		gdNamespace = namespace_manager.get_namespace()
		appNamespace = 'APP_'+aID




		namespace_manager.set_namespace(gdNamespace)
		#find app
		try:
			aInfo = DB_App.get_by_id(aID)
		except Exception, e:
			self.printError("dont find app1",100,aInfo.secretKey)
			return

		if not aInfo:
			self.printError('dont find app2' + aID,100,aInfo.secretKey)
			return
		
		#dec token & commands
		cmdtext = self.request.get('command')
		cmdtext = CommandHandler.DesInBase64ToStr(cmdtext,aInfo.secretKey)
		cmdtext = cmdtext.replace('\x00','')
		commands = {}
		if cmdtext:
			commands = json.loads(cmdtext) #decParam(self.request.get('command'))
		
		logging.info(commands)
		tokens = CommandHandler.decToken(token,aInfo.secretKey)

		namespace_manager.set_namespace(appNamespace)

		logging.info('tokens2')
		logging.info(tokens)
		logging.info('session')
		logging.info(self.session)
		logging.info(self.session.get('aID'))

		
		
		allresult = {'timestamp':int(cTime),'createTime':str(cTime), 'version':version, 'state':'ok'}	

		#result = {'timestamp':int(cTime),'createTime':str(cTime), 'version':version}
		if not self.session.get('aID') or self.session.get('aID')!=aID:	#login ##########################################################################
			logging.info('start authorise' + str(tokens.get('auID')))
			
			appver = self.request.get('appver')
			if not appver:
				appver='0'
			
			appverid = tokens.get('platform')+"_"+str(appver)
			appversions = DB_AppVersions.get_by_id(appverid)
			
			if not appversions:
				appversions = DB_AppVersions.get_or_insert(appverid)
				appversions.platform = tokens.get('platform')
				appversions.version = int(appver)
				appversions.put()

			#auID있으면 au정보 뽑아오기~
			if tokens.get('auID'):
				try:
					logging.info('finded by auID : '+str(tokens['auID']))
					auInfo = DB_AppUser.get_by_id(tokens['auID'])
					#key =  ndb.Key(urlsafe=tokens['auID'])
					#auInfo = key.get()
				except Exception, e:
					pass

			#auID존재여부확인 , ctime check && uuid check  and appuser.createTime == tokens.get('createTime')
			# and auInfo.createTime == tokens.get('createTime')
			if auInfo and auInfo.udid == tokens.get('udid'):	#and auInfo.udid == tokens.get('udid')
				logging.info("user finded")
				stats = DB_AppStats.getInMC()
				hour = int(datetime.datetime.now().hour)
				try:
					stats['hit'][hour]+=1
				except KeyError:
					stats['hit'][hour]=1
				DB_AppStats.setInMC(stats)
				# name , flag update after check
				#if tokens.get('nick') and tokens.get('flag'):
					#logging.info('chage the nick & flag key:'+str(auInfo.uInfo.key))
				#	if auInfo.nick != tokens.get('nick') or auInfo.flag != tokens.get('flag'):
				#		namespace_manager.set_namespace(gdNamespace)
				#		uInfo=auInfo.uInfo.get()
				#		uInfo.nick = auInfo.nick = tokens.get('nick')
				#		uInfo.flag = auInfo.flag = tokens.get('flag')
				#		uInfo.put()
				#		namespace_manager.set_namespace(appNamespace)
				#createTime update
				
				auInfo.createTime=str(cTime)
				auInfo.putOn()

				#weekly pint update after check!##############################
				

			elif tokens.get('createTime')=='9999':	#join
				#find at user table by udid
				logging.info("user dont finded")
				uInfo = {}
				namespace_manager.set_namespace(gdNamespace)
				que = DB_User.query(DB_User.udid == tokens.get('udid'))
				find = que.fetch(limit=1)
				namespace_manager.set_namespace(appNamespace)
				if len(find)>0: #회원정보찾음
					logging.info("find uid by udid")
					uInfo = find[0]
					if not tokens.get('nick'):
						tokens['nick']=uInfo.nick
						tokens['flag']=uInfo.flag

					#check app installed in user info
					
					if aID in uInfo.installs:
						namespace_manager.set_namespace(appNamespace)
						q = DB_AppUser.query(DB_AppUser.uInfo == uInfo.key)
						for a in q.fetch(limit=1):
							logging.info("find auid in installs")
							auInfo = a


				else:	#don't find
					logging.info("dont find uid by udid")
					#join
					namespace_manager.set_namespace(gdNamespace)
					uInfo = DB_User()
					uInfo.nick = tokens.get('nick')
					uInfo.flag = tokens.get('flag')
					uInfo.udid = tokens.get('udid')
					uInfo.put()
					namespace_manager.set_namespace(appNamespace)
				
				if not auInfo: # if not app user , app join 
					logging.info("join appuser")
					auInfo = DB_AppUser()
					auInfo.nick = tokens.get('nick')
					auInfo.flag = tokens.get('flag')
					auInfo.udid = tokens.get('udid')
					auInfo.uInfo = uInfo.key
					auInfo.put()

					#update installs
					namespace_manager.set_namespace(gdNamespace)
					uInfo.installs.append(aID)
					uInfo.put()
					namespace_manager.set_namespace(appNamespace)
					allresult['isFirst']=True
					
					stats = DB_AppStats.getInMC()
					hour = int(datetime.datetime.now().hour)
					try:
						stats['install'][hour]+=1
					except KeyError:
						stats['install'][hour]=1
					DB_AppStats.setInMC(stats)

					#cpiEvents check get
					if len(uInfo.CPIEvents)>0:
						logging.info('check cpievent')
						i=0
						for cpi in uInfo.CPIEvents:
							if aID == cpi.get('eventAppID'):
								logging.info('find cpi Event')
								namespace_manager.set_namespace('APP_'+cpi.get('fromAppID'))
								#newRequest = DB_AppRequest()
								#newRequest.receiver = ndb.Key('DB_AppUser',int(cpi.get('fromAppUserID')))
								#newRequest.sender = aInfo.key
								#newRequest.category = 'cpiEvent'
								#newRequest.content = 'complete cpiEvent'
								#newRequest.userdata={"reward":cpi.get('reward'),"title":aInfo.title}
								#newRequest.put()
								
								fromAppUserInfo = ndb.Key('DB_AppUser',int(cpi.get('fromAppUserID'))).get()
								newRequest = {}
								newRequest['rid'] = ''.join(random.choice(string.ascii_uppercase) for x in range(10))
								newRequest['sender'] = {'type':'app','id':aInfo.key.id(),'name':aInfo.title}
								newRequest['category'] = 'cpievent'
								newRequest['content'] = 'complete cpiEvent'
								newRequest['userdata']={"reward":cpi.get('reward')}

								if type(fromAppUserInfo.requests)==list:
									fromAppUserInfo.requests.insert(0,newRequest)
								else:
									fromAppUserInfo.requests = [newRequest]

								fromAppUserInfo.put()
								logging.info('add cpirequest')
								logging.info(newRequest)
								logging.info(fromAppUserInfo.nick)

								namespace_manager.set_namespace(gdNamespace)
								del uInfo.CPIEvents[i]
								uInfo.put()
								namespace_manager.set_namespace(appNamespace)

								allresult['cpiEvent']=True
								break
							i=i+1
			else :
				self.printError('authorise error11',9999,aInfo.secretKey)
				logging.info(tokens.get('createTime'))
				return


			namespace_manager.set_namespace(appNamespace)
			#return result
			allresult['tokenUpdate']='ok'
			allresult['state']='ok'
			allresult['auID']=str(auInfo.key.id())
			
			self.session['aID']=aID
			self.session['auID']=auInfo.key.id()
			logging.info('session update!! :'+aID+":"+str(auInfo.key.id()))
			logging.info('session auid:'+str(self.session.get('auID')))
			logging.info('session aid:'+str(self.session.get('aID')))
			logging.info('session cTime:'+str(cTime))
			auInfo.createTime=str(cTime)
			tokens['createTime']=str(cTime)
			logging.info(json.dumps(allresult))
			self.response.write(CommandHandler.strToDesInBase64(json.dumps(allresult),aInfo.secretKey).strip())
			return


		if self.session.get('auID'):
			#key =  ndb.Key(urlsafe=self.session.get('auID'))
			#auInfo = key.get()
			auInfo = DB_AppUser.get_by_id(int(self.session.get('auID')))
			logging.info('nick : ' + str(self.session.get('auID')))

		#login check
		if not self.session.get('aID') or not self.session.get('auID'):
			self.printError('error',100,aInfo.secretKey)
			return

		#token check
		if tokens.get('createTime')!=auInfo.createTime:
			logging.info("####################### cTime ERROR #############################")
			#self.printError('token Error',9999,aInfo.secretKey)
			#return





		for commandID,command in commands.items():
			logging.info('########################### start command ###############################')
			actions=[command.get('a')]
			action=command.get('a')
			param=command.get('p')
			logging.info(param)

			#기본리턴값
			result = {'action':actions[0]}

			namespace_manager.set_namespace(appNamespace)




			if 'logout' in actions:
				self.session['auID']=''
				self.session['aID']=''
				allresult[commandID]=self.createError('logout',100)
				
				logging.info('session auid:'+self.session.get('auID'))
				logging.info('session aid:'+self.session.get('aID'))
				continue



			



			namespace_manager.set_namespace(appNamespace)
			#create dbclass
			#DB_AppUser =  _DB_AppUser.createClass(aID)
			#DB_AppScore = _DB_AppScore.createClass(aID)

			

			# timestamp action
			if 'timestamp' in actions: ##########################################################################
				result['state']='ok'
				result['timestamp']=int(cTime)

			# getweek
			if 'getweek' in actions: ##########################################################################
				result['week']=int(datetime.date.today().strftime("%U"))+1
				localtime = time.localtime(time.time())
				weekday = int(datetime.date.today().strftime("%u"))
				result['timestamp']=int(cTime)
				if weekday==7:
					weekday = 0
				result['lefttime']=(7-weekday)*24*60*60 - localtime.tm_hour*60*60 -localtime.tm_min*60 - localtime.tm_sec
				result['state']='ok'

			# getweek
			if 'sessiontest' in actions: ##########################################################################
				number = 0
				if self.session.get('stest'):
					number = self.session.get('stest')

				number+=1

				self.session['stest']=number
				result['stest']=number
				
			#logging.info('aID in session : '+self.session.get('aID'))
			# start action

			

			#action startscores
			if 'getflagranks' in actions:#~ ##########################################################################
				scoresSortValue = aInfo.scoresSortValue
				startTime = int(cTime)/scoresSortValue*scoresSortValue
				gType = param.get('type')
				if not gType:
					gType = 'default'

				logging.info('startscores')
				#DB_AppScore.sTime==startTime
				nowdate = datetime.date.today().strftime("%Y%m%d")
				flaglist =  DB_AppFlagScore.query(ndb.AND(DB_AppFlagScore.date==nowdate,DB_AppFlagScore.gType==gType)).order(-DB_AppFlagScore.score).fetch(10)
				result['list']=[]
				alluser=0
				for flagInfo in flaglist:
					_new = flagInfo.toResult()
					result['list'].append(_new)
					alluser += _new.get('user')
				



				#_list = []
				


				#if gType=='all':
				#	_list = DB_AppScore.query().fetch(5)
				#else:
				#	_list = DB_AppScore.query(DB_AppScore.gType==self.session.get('gType')).fetch(5)
				
				#alluser=0
				#flags={}
				#for _as in _list:
				#	if not flags.get(_as.flag):
				#		flags[_as.flag]={'user':int(1),'score':int(_as.score),'flag':_as.flag}
				#	else:
				#		_cnt = int(flags.get(_as.flag).get('user'))+1
				#		_scr = int(flags.get(_as.flag).get('score'))+_as.score
				#		flags[_as.flag]={'score':_scr,'user':_cnt,'flag':_as.flag}

				#	alluser=alluser+1

				#flags=sorted(flags, key=flags.__getitem__,flags.__getitem__, reverse=True)

				#items = [v for k, v in flags.items()]
				#items=sorted(items, key=lambda x: x['score'],cmp=lambda x,y: y-x) 

				#result['list']=items[:5]
				result['alluser']=alluser
				result['state']='ok'

			#action startscores
			if 'startscores' in actions:#~ ##########################################################################
				sqlConnect(aid=aInfo.aID,instance=aInfo.dbInstance)
				logging.info('startscores')
				sortValue=aInfo.scoresSortValue
			#param ->  type, score, userdata, 
				gType = param.get('type')
				userdata = param.get('userdata')
				if not gType:
					gType = 'default'

				if param.get('score'):
					score = int(param.get('score'))
				else:
					score=0
				
				startTime = int(cTime)/sortValue*sortValue


				#asInfo = DB_AppScore()
				#asInfo.sTime = startTime
				#asInfo.uTime = int(cTime)
				#asInfo.gType = gType
				#asInfo.score =  score
				#asInfo.auInfo = auInfo.key
				#asInfo.flag = tokens.get('flag')
				#asInfo.nick = tokens.get('nick')
				#if userdata:
				#	asInfo.userdata = userdata
				#asInfo.isOver = False
				#asInfo.put()

				#######################################################
				asInfo2 = DB_AppScores()
				asInfo2.auInfo = auInfo.key.id()
				asInfo2.gType = gType
				asInfo2.score = score
				asInfo2.sTime = int(cTime)
				asInfo2.uTime = int(cTime)
				asInfo2.flag = tokens.get('flag')
				asInfo2.nick = tokens.get('nick')
				if userdata:
					asInfo2.userdata = userdata
				asInfo2.put()

				baseSIDs = DB_AppScores.query('ORDER BY no desc LIMIT 100,1')
				if baseSIDs:
					baseSID=DB_AppScores.set(baseSIDs[0])
					self.session['baseScoreID']=baseSID.asid
				else:
					baseSIDs = DB_AppScores.query('ORDER BY no asc LIMIT 1')
					baseSID=DB_AppScores.set(baseSIDs[0])
					self.session['baseScoreID']=baseSID.asid

				logging.info('set base id')
				logging.info(baseSID.to_dict())

				self.session['asID2']=asInfo2.asid
				########################################################

				self.session['asSortTime'] = startTime
				self.session['asSortPrevTime'] = startTime-sortValue
				##self.session['asID']=asInfo.key.id()
				self.session['gType']=str(gType)

				logging.info(namespace_manager.get_namespace())
				logging.info(str(self.session.get('asID')))
				logging.info(str(self.session.get('asSortTime')))
				logging.info(str(self.session.get('auID')))
				logging.info(str(self.session.get('aID')))
				logging.info(str(self.session.get('gType')))

				result['state']='ok'
				sqlClose()

			if 'getscores' in actions: ##########################################################################
				sqlConnect(aid=aInfo.aID,instance=aInfo.dbInstance)
				logging.info(namespace_manager.get_namespace())
				logging.info(str(self.session.get('asID')))
				logging.info(str(self.session.get('asSortTime')))
				logging.info(str(self.session.get('auID')))
				logging.info(str(self.session.get('aID')))
				logging.info(str(self.session.get('gType')))
				
				asInfo2 = DB_AppScores.get(int(self.session.get('asID2')))

				##asInfo =  ndb.Key('DB_AppScore',int(self.session.get('asID'))).get()
				asSortTime = self.session.get('asSortTime')
				asSortTimeList = [self.session.get('asSortTime'),self.session.get('asSortPrevTime')]
				baseScoreID = self.session.get('baseScoreID')
				gType = asInfo2.gType
				userdata = param.get('userdata')
				
				if not asInfo2:

					allresult[commandID]=self.createError('dont find asid',100)
					continue


				if param.get('score'):
					##asInfo.score = int(param.get('score'))
					asInfo2.score = int(param.get('score'))
				else:
					##asInfo.score = 0
					asInfo2.score = 0
				

				##asInfo.isOver = bool(param.get('isover'))
				asInfo2.isOver = bool(param.get('isover'))



				if userdata:
					if type(asInfo2.userdata)==dict:
						##asInfo.userdata.update(userdata)
						asInfo2.userdata.update(userdata)
					else:
						##asInfo.userdata = userdata
						asInfo2.userdata = userdata

				# game over!!
				if asInfo2.isOver:
					##asInfo.eTime = cTime
					asInfo2.eTime = cTime
					logging.info(self.session.get('asID'))

					#flag scores update
					nowdate = datetime.date.today().strftime("%Y%m%d")
					flagid = nowdate+"_"+gType+"_"+auInfo.flag
					flagInfo=DB_AppFlagScore.get_or_insert(flagid)
					flagInfo.date = nowdate
					flagInfo.flag = auInfo.flag
					flagInfo.gType = gType
					
					if flagInfo.score:
						flagInfo.score += int(param.get('score'))/10
					else:
						flagInfo.score = int(param.get('score'))/10
					
					if flagInfo.user:
						flagInfo.user += 1
					else:
						flagInfo.user = 1

					flagInfo.put()

					#check weekly score
					nowweek = int(datetime.date.today().strftime("%U"))
					weekid = str(auInfo.key.id())+"_"+str(gType)+"_"+str(nowweek)

					##weeklydata = DB_AppWeeklyScore.get_or_insert(weekid)
					weeklydata = DB_AppWeeklyScores.get_or_insert(weekid)
					logging.info(weeklydata.to_dict())
					logging.info(nowweek)
					if weeklydata.score<asInfo2.score or weeklydata.week != nowweek:
						weeklydata.week=nowweek
						weeklydata.gType=asInfo2.gType
						weeklydata.auInfo=auInfo.key.id()
						weeklydata.score = asInfo2.score
						weeklydata.nick = asInfo2.nick
						weeklydata.flag = asInfo2.flag
						weeklydata.sTime = asInfo2.uTime
						weeklydata.eTime = asInfo2.eTime
						weeklydata.userdata = asInfo2.userdata
						logging.info(weeklydata.to_dict())
						weeklydata.put()
						result['newweeklyscore']=True
						


						#check max score
						maxid = str(auInfo.key.id())+"_"+str(gType)
						maxdata = DB_AppMaxScores.get_or_insert(maxid)
						
						if maxdata.score<asInfo2.score:
							maxdata.gType = gType
							maxdata.auInfo = auInfo.key.id()
							maxdata.score = asInfo2.score
							maxdata.nick = asInfo2.nick
							maxdata.flag = asInfo2.flag
							maxdata.sTime = asInfo2.uTime
							maxdata.eTime = asInfo2.eTime
							maxdata.userdata = asInfo2.userdata
							maxdata.put()
							result['newmaxscore']=True

				
				asInfo2.put()

				#2. alluser
				##result['alluser'] = DB_AppScore.query(ndb.AND(DB_AppScore.sTime.IN(asSortTimeList),DB_AppScore.gType==gType)).count()
				result['alluser'] = DB_AppScores.count("WHERE no>%s and gType='%s'"%(baseScoreID,gType))

				#1. myrank
				if asInfo2.score == 0:
					##result['myrank']=result.get('alluser')
					result['myrank']=result.get('alluser')
				else:
					##result['myrank'] = result.get('alluser')-DB_AppScore.query(ndb.AND(DB_AppScore.sTime.IN(asSortTimeList),DB_AppScore.gType==gType,DB_AppScore.score<=asInfo.score)).count()+1
					result['myrank'] = DB_AppScores.count("WHERE no>%s AND gType='%s' AND score>%s"%(baseScoreID,gType,asInfo2.score))+1

				logging.info('myrank is')
				logging.info(result['myrank'])

				logging.info('myscore is')
				logging.info('info '+str(asInfo2.score))

				#asInfo = future.get_result()
				isAddMe=False
				result['list']=[]
				##result['list2']=[]
				##rank=1

				#############################################################################################
				rank=1
				if result['myrank']<=8:
					scorelist2 = DB_AppScores.query("WHERE no>%s AND gType='%s' ORDER BY score desc LIMIT 10"%(baseScoreID,gType))
					for row in scorelist2:
						sinfo = DB_AppScores.set(row)
						_new =sinfo.to_dict()
						_new['rank']=rank
						
						if _new.get('asid')==asInfo2.asid:
							_new['isme']=True

						result['list'].append(_new)
						rank+=1
				else:
					_offset = result.get('myrank')-5
					scorelist2 = DB_AppScores.query("WHERE no>%s AND gType='%s' ORDER BY score desc LIMIT 3"%(baseScoreID,gType))
					scorelist2 += DB_AppScores.query("WHERE no>%s AND gType='%s' ORDER BY score desc LIMIT %s,7"%(baseScoreID,gType,_offset))
					for row in scorelist2:
						sinfo = DB_AppScores.set(row)
						_new =sinfo.to_dict()
						ofs=0
						if rank>3:
							ofs =_offset-3

						_new['rank']=rank+ofs
						
						if _new.get('asid')==asInfo2.asid:
							_new['isme']=True

						result['list'].append(_new)
						rank+=1


				#############################################################################################

	##			if result['myrank']<=10:
	##				scorelist = DB_AppScore.query(ndb.AND(DB_AppScore.sTime.IN(asSortTimeList)),DB_AppScore.gType==gType).order(-DB_AppScore.score).fetch(10)
	##
	##				for sinfo in scorelist:
	##					_new = sinfo.toResult()
	##
	##					if isAddMe==False and _new.get('score')<=asInfo.score:
	##						_me = asInfo.toResult()
	##						_me['rank']=rank
	##						_me['isme']=True
	##						result['list'].append(_me)
	##						rank+=1
	##						isAddMe=True
	##
	##					_new['rank']=rank
	##					if _new['asid']!=asInfo.key.id():
	##						result['list'].append(_new)
	##						rank=rank+1
	##			else:
	##				#curs = Cursor(urlsafe=self.request.get('cursor'))
	## 	  			#greets, next_curs, more = Greeting.query().fetch_page(10, start_cursor=curs)
	##				scorelist = DB_AppScore.query(ndb.AND(DB_AppScore.sTime.IN(asSortTimeList),DB_AppScore.gType==gType)).order(-DB_AppScore.score).fetch(3)
	##				scorelist += DB_AppScore.query(ndb.AND(DB_AppScore.sTime.IN(asSortTimeList),DB_AppScore.gType==gType)).order(-DB_AppScore.score).fetch(offset=result.get('myrank')-5,limit=7)
	##
	##
	##				for sinfo in scorelist:
	##					_new = sinfo.toResult()
	##					
	##					ofs=0
	##					if rank>3:
	##						ofs =result['myrank']-8
	##
	##					if isAddMe==False and _new.get('score')<=asInfo.score:
	##						_me = asInfo.toResult()
	##						_me['rank']=rank+ofs
	##						_me['isme']=True
	##						result['list'].append(_me)
	##						rank+=1
	##						isAddMe=True
	##
	##					_new['rank']=rank+ofs
	##
	##					if _new['asid']!=asInfo.key.id():
	##						result['list'].append(_new)
	##						rank=rank+1
	##
	##
	##			if not isAddMe:
	##				_me = asInfo.toResult()
	##				_me['rank']=rank
	##				_me['isme']=True
	##				result['list'].append(_me)


	#			if not checkme:
	#				logging.info('write!! new!!!')
	#				_new = asInfo.toResult()
	#				_new['rank']=result['myrank']
	#				_new['isme']=True
	#
	#				if result.get('myrank')<=10:
	#					result['list'].insert(result.get('myrank')-1,_new)
	#					logging.info('insert to myrank'+str(result.get('myrank')-1))
	#				else:
	#					result['list'].insert(7,_new)
	#					logging.info('insert to 7')
					
					
				result['list'] = result['list'][:10]
				result['state']='ok'

				if asInfo2.isOver:
					self.session['asSortID']=''
					self.session['asID']=''

				#asInfo.put()
				sqlClose()
			if 'getmaxscores' in actions: ###############################################################################
				sqlConnect(aid=aInfo.aID,instance=aInfo.dbInstance)
				gType = param.get('type')
				if not gType:
					gType = 'default'

				maxdata = {}
				
				maxid = str(auInfo.key.id())+"_"+str(gType)
				
				maxdata = DB_AppMaxScores.get_or_insert(maxid)

				##findmaxdata = DB_AppMaxScore.query(ndb.AND(DB_AppMaxScore.auInfo==auInfo.key,DB_AppMaxScore.gType==gType)).fetch(1)
				##if findmaxdata:
				##	maxdata = findmaxdata[0]
				##else:
				##	maxdata = DB_AppMaxScore(score=0,gType=gType,auInfo=auInfo.key,flag=auInfo.flag,nick=auInfo.nick)

				##result['alluser']=DB_AppMaxScore.query(DB_AppMaxScore.gType==gType).count()
				##result['myrank']=result.get('alluser')-DB_AppMaxScore.query(ndb.AND(DB_AppMaxScore.gType==gType,DB_AppMaxScore.score<=maxdata.score)).count()+1

				result['alluser']=DB_AppMaxScores.count("WHERE gType='%s'"%gType)
				result['myrank']=DB_AppMaxScores.count("WHERE gType='%s' and score<%s"%(gType,maxdata.score))
				notinten=False
				if(result.get('myrank')<=10):
					##maxlist = DB_AppMaxScore.query(ndb.AND(DB_AppMaxScore.gType==gType)).order(-DB_AppMaxScore.score).fetch(10)
					maxlist = DB_AppMaxScores.query("WHERE gType='%s' ORDER BY score desc LIMIT 10"%gType)
				else:
					_offset = result.get('myrank')-5
					maxlist = DB_AppMaxScores.query("WHERE gType='%s' ORDER BY score desc LIMIT 3"%gType)
					maxlist += DB_AppMaxScores.query("WHERE gType='%s' ORDER BY score desc LIMIT %s,7"%(gType,_offset))

					##maxlist = DB_AppMaxScore.query(ndb.AND(DB_AppMaxScore.gType==gType)).order(-DB_AppMaxScore.score).fetch(3)
					##maxlist+= DB_AppMaxScore.query(ndb.AND(DB_AppMaxScore.gType==gType)).order(-DB_AppMaxScore.score).fetch(offset=result.get('myrank')-5,limit=7)
					notinten=True
				result['list']=[]
				r=1

				for minfo in maxlist:
					_result = DB_AppMaxScores.set(minfo)
					resultdata = _result.to_dict()
					
					ofs=0
					if r>3 and notinten:
						ofs =result['myrank']-8

					resultdata['rank']=r+ofs

					if resultdata['auid']==auInfo.key.id():
						resultdata['isme']=True

					result['list'].append(resultdata)
					r+=1

				result['state']='ok'
				sqlClose()



			if 'getweeklyscores' in actions: ################################################################################

				sqlConnect(aid=aInfo.aID,instance=aInfo.dbInstance)
				gType = param.get('type')
				if not gType:
					gType = 'default'

				weeklydata = {}
				
				nowweek = int(datetime.date.today().strftime("%U"))
				weekid = str(auInfo.key.id())+"_"+str(gType)+"_"+str(nowweek)
				
				weeklydata = DB_AppWeeklyScores.get_or_insert(weekid)

				##findmaxdata = DB_AppMaxScore.query(ndb.AND(DB_AppMaxScore.auInfo==auInfo.key,DB_AppMaxScore.gType==gType)).fetch(1)
				##if findmaxdata:
				##	maxdata = findmaxdata[0]
				##else:
				##	maxdata = DB_AppMaxScore(score=0,gType=gType,auInfo=auInfo.key,flag=auInfo.flag,nick=auInfo.nick)

				##result['alluser']=DB_AppMaxScore.query(DB_AppMaxScore.gType==gType).count()
				##result['myrank']=result.get('alluser')-DB_AppMaxScore.query(ndb.AND(DB_AppMaxScore.gType==gType,DB_AppMaxScore.score<=maxdata.score)).count()+1

				result['alluser']=DB_AppWeeklyScores.count("WHERE gType='%s' and week=%s"%(gType,nowweek))
				result['myrank']=DB_AppWeeklyScores.count("WHERE gType='%s' and week=%s and score<%s"%(gType,nowweek,weeklydata.score))
				notinten=False
				if(result.get('myrank')<=10):
					##maxlist = DB_AppMaxScore.query(ndb.AND(DB_AppMaxScore.gType==gType)).order(-DB_AppMaxScore.score).fetch(10)
					weeklylist = DB_AppWeeklyScores.query("WHERE gType='%s' and week=%s ORDER BY score desc LIMIT 10"%(gType,nowweek))
				else:
					_offset = result.get('myrank')-5
					weeklylist = DB_AppWeeklyScores.query("WHERE gType='%s' and week=%s ORDER BY score desc LIMIT 3"%(gType,nowweek))
					weeklylist += DB_AppWeeklyScores.query("WHERE gType='%s' and week=%s ORDER BY score desc LIMIT %s,7"%(gType,nowweek,_offset))

					##maxlist = DB_AppMaxScore.query(ndb.AND(DB_AppMaxScore.gType==gType)).order(-DB_AppMaxScore.score).fetch(3)
					##maxlist+= DB_AppMaxScore.query(ndb.AND(DB_AppMaxScore.gType==gType)).order(-DB_AppMaxScore.score).fetch(offset=result.get('myrank')-5,limit=7)
					notinten=True
				result['list']=[]
				r=1

				for minfo in weeklylist:
					_result = DB_AppWeeklyScores.set(minfo)
					resultdata = _result.to_dict()
					
					ofs=0
					if r>3 and notinten:
						ofs =result['myrank']-8

					resultdata['rank']=r+ofs

					if resultdata['auid']==auInfo.key.id():
						resultdata['isme']=True

					result['list'].append(resultdata)
					r+=1

				result['state']='ok'
				sqlClose()
	##			gType = param.get('type')
	##			if not gType:
	##				gType = 'default'
	##
	##			# find my info
	##			findweeklydata = DB_AppWeeklyScore.query(ndb.AND(DB_AppWeeklyScore.auInfo==auInfo.key,DB_AppWeeklyScore.gType==gType)).fetch(1)
	##			weeklydata = {}
	##			nowweek = int(datetime.date.today().strftime("%U"))
	##			if findweeklydata:
	##				weeklydata = findweeklydata[0]
	##			else:
	##				weeklydata = DB_AppWeeklyScore(score=0, week=0, gType=asInfo.gType, auInfo=auInfo.key)
	##
	##			#2. alluser
	##			result['alluser'] = DB_AppWeeklyScore.query(ndb.AND(DB_AppWeeklyScore.gType==gType,DB_AppWeeklyScore.week == nowweek)).count()
	##			#1. myrank
	##			result['myrank'] =  DB_AppWeeklyScore.query(ndb.AND(DB_AppWeeklyScore.score>weeklydata.score,DB_AppWeeklyScore.gType==gType,DB_AppWeeklyScore.week == nowweek)).count()+1
	##
	##
	##			#asInfo = future.get_result()
	##			checkme = False
	##			if result['myrank']<=10:
	##				scorelist = DB_AppWeeklyScore.query(ndb.AND(DB_AppWeeklyScore.gType==gType,DB_AppWeeklyScore.week == nowweek)).order(-DB_AppWeeklyScore.score).fetch(10)
	##				result['list']=[]
	##				rank=1
	##				for sinfo in scorelist:
	##					_new = sinfo.toResult()
	##					_new['rank']=rank
	##
	##					if _new['auid']==auInfo.key.id():
	##						_new['isme']=True
	##						checkme=True
	##
	##					result['list'].append(_new)
	##					rank=rank+1
	##			else:
	##				scorelist = DB_AppWeeklyScore.query(ndb.AND(DB_AppWeeklyScore.gType==gType,DB_AppWeeklyScore.week == nowweek)).order(-DB_AppWeeklyScore.score).fetch(3)
	##				scorelist += DB_AppWeeklyScore.query(ndb.AND(DB_AppWeeklyScore.gType==gType,DB_AppWeeklyScore.week == nowweek)).order(-DB_AppWeeklyScore.score).fetch(offset=result.get('myrank')-5,limit=7)
	##
	##				result['list']=[]
	##				rank=1
	##
	##				for sinfo in scorelist:
	##					_new = sinfo.toResult()
	##					ofs=0
	##					if rank>3:
	##						ofs =result['myrank']-8
	##
	##					_new['rank']=rank+ofs
	##
	##					if _new['auid']==auInfo.key.id():
	##						_new['isme']=True
	##						checkme=True
	##
	##					result['list'].append(_new)
	##					rank=rank+1


			if 'getnotices' in actions: #######################################################################################
				# param - lastNoticeID, 
				#          limit = true, false
				lastNoticeID = param.get('lastnoticeid')
				limit = param.get('limit')
				if not limit:
					limit = 10
				if not lastNoticeID :
					lastNoticeID=0
				#DB_AppNotice.key.id>lastNoticeID
				noticeList = DB_AppNotice.query().order(-DB_AppNotice.key).fetch(limit)
				result['list']=[]
				for notice in noticeList:
					noticedict = {}
					noticedict['id']=notice.key.id()
					noticedict['title']=notice.title
					noticedict['content']=notice.content
					noticedict['userdata']=notice.userdata
					noticedict['platform']=notice.platform
					noticedict['createtime']=notice.createTime
					result['list'].append(noticedict)
				result['state']='ok'
			
			if 'getrequests' in actions: #######################################################################################
				limit = param.get('limit')
				category = param.get('category')
				categorys = ['all','cpievent','notice','housead','update','defalut']
				autoremoves=[]

				if type(param.get('autoremove')) == bool:
					autoremove = param.get('autoremove')
					if autoremove==True:
						autoremoves=['all','cpievent','notice','housead','update','defalut']
					else:
						autoremoves = []
				elif type(param.get('autoremove')) == str:
					autoremoves = [param.get('autoremove')]
				elif type(param.get('autoremove')) == list:
					autoremoves = param.get('autoremove')
				

				if category:
					if type(category)==list:
						logging.info('category is list')
						categorys = category
					elif category!='all':
							categorys = [category]
							logging.info('category is str')


				if not limit:
					limit = 10
				
				logging.info(categorys)

				if type(auInfo.requests) != list:
					auInfo.requests=[]
				
				#rlist = DB_AppRequest.query(ndb.AND(DB_AppRequest.receiver==auInfo.key,DB_AppRequest.category.IN(category))).fetch(limit)
				#for request in rlist:
				#	requestDict = {}
				#	requestDict['rid']=request.key.id()
				#	requestDict['category']=request.category
				#	requestDict['content']=request.content
				#	requestDict['userdata']=json.loads(request.userdata)
				#	requestDict['autoremove']=False
				#	result['list'].append(requestDict)

				platformlist = ['all',tokens.get('platform')]
				

				if not auInfo.lastNID:
					auInfo.lastNID=0

				where = ndb.AND(DB_AppNotice.createTime>auInfo.lastNID,DB_AppNotice.platform.IN(platformlist),DB_AppNotice.category.IN(categorys))

				nlist = DB_AppNotice.query(where).fetch(1)

				if nlist:
					auInfo.lastNID = cTime

				for notice in nlist:
					#notice = nlist[0]
					#여기에 조건(appversion, osversion) 검사 후 진짜 넘길지 말지 결정
					requestDict={}
					requestDict['rid']=notice.key.id()
					requestDict['category']=notice.category
					requestDict['content']=notice.content
					requestDict['userdata']=notice.userdata
					auInfo.requests.insert(0,requestDict)
					logging.info('add notice')
					logging.info(requestDict)

					if notice.count:
						notice.count+=1
					else:
						notice.count=1
					notice.put()
					
				if type(auInfo.requests) == list and len(auInfo.requests)>0:
					logging.info('auto remove')
					resultList = []
					for request in auInfo.requests:
						if request.get('category') in categorys:
							resultList.append(copy.deepcopy(request))

							if request.get('category') in autoremoves:
								auInfo.requests.remove(request)
								logging.info(request)
					
					auInfo.putOn()
					result['list']=resultList
				else:
					result['list']=[]

				result['state']='ok'

			if 'removerequest' in actions: #######################################################################################
				rids = []
				if type(param.get('rid'))!=list:
					rids = [param.get('rid')]
				else:
					rids = param.get('rid')

				result['state']='error'
				removecheck=False

				for rid in rids:
					for request in auInfo.requests:			
						if request.get('rid')==rid:
							auInfo.requests.remove(request)
							removecheck = True
							break

				if removecheck==True:
					auInfo.putOn()
					result['state']='ok'
					

						
				#request = DB_AppRequest.get_by_id(int(self.session.get('rid')))
				#if request:
				#	request.delete()
				#	result['state']='ok'
				#else:
				#	result['state']='error'

			if 'getcpilist' in actions: #######################################################################################
				namespace_manager.set_namespace(gdNamespace)
				limit = param.get('limit')
				if not limit:
					limit = 10
				cpiList = DB_App.query(ndb.AND(DB_App.useCPI== True,DB_App.group==aInfo.group)).fetch(limit)
				result['list']=[]

				cpiReward = aInfo.cpiReward
				user = auInfo.uInfo.get()

				if type(cpiReward) != dict:
					cpiReward = {'defalut':1000}

				for cpi in cpiList:
					logging.info(cpi.key.id())

					if cpi.key.id() == aID:
						logging.info('self app continue')
						continue

					# 1. 이미설치된 앱인가 검사
					if cpi.key.id() in user.installs:
						logging.info('installed app continue')
						continue

					# 2. cpievent 중인가 검사
					#iscping = False
					#if type(user.CPIEvents)==list:
					#	for cping in user.CPIEvents:
					#		if cping.get('eventAppID')==cpi.key.id():
					#			iscping=True
					#			break

					#if iscping:
					#	logging.info('cping  app continue')
					#	continue

					logging.info('add cpievent')
					cpidict = {}
					cpidict['id']=cpi.key.id()
					cpidict['title']=cpi.title
					cpidict['bannerimg']=cpi.bannerImg
					cpidict['iconimg']=cpi.iconImg
					cpidict['reward']=cpiReward.get(cpi.key.id(),cpiReward.get('default',1000))
					cpidict['store']=cpi.store.get(tokens.get('platform'))
					descript = cpi.descript.get(tokens.get('lang'),cpi.descript.get('default','no descript'))
					cpidict['descript']=descript

					result['list'].append(cpidict)
				
				namespace_manager.set_namespace(appNamespace)
				
				if type(auInfo.requests)==list and len(auInfo.requests)>0:
					for request in auInfo.requests:
						if request.get('category')=='cpievent':
							result['reward']=True
							break
				else:
					result['reward']=False
				#result['completelist']=[]

				#for com in completeList:
				#	_new = com.to_dict()
				#	_new['id']=com.key.id()
				#	del _new['receiver']
				#	del _new['sender']
				#	result['completelist'].append(_new)

				result['state']='ok'

			if 'addcpievent' in actions: #######################################################################################
				namespace_manager.set_namespace(gdNamespace)
				
				
				cpiappid = param.get('aid')


				user = auInfo.uInfo.get()
				
				result['state']='ok'

				# 1. 이미설치된 앱인가 검사
				if cpiappid in user.installs:
					allresult[commandID]=self.createError('installed event',660)
					continue

				# 2. cpievent 중인가 검사
				if type(user.CPIEvents)==list:
					for cpi in user.CPIEvents:
						if cpi.get('eventAppID')==cpiappid:
							allresult[commandID]=self.createError('ing event',670)
							continue

				
				cpiReward=aInfo.cpiReward
				reward = cpiReward.get(cpiappid,cpiReward.get('default',1000))
				newCpiEvent={'eventAppID':cpiappid,'fromAppID':aID,'fromAppUserID':auInfo.key.id(),'reward':reward,'time':cTime}
				if type(user.CPIEvents)==list:
					user.CPIEvents.append(newCpiEvent)
				else:
					user.CPIEvents=[newCpiEvent]

				user.put()
				logging.info(newCpiEvent)

				namespace_manager.set_namespace(appNamespace)

			if 'usegiftcode' in actions:#######################################################################################
				
				if param.get('giftcode'):
					giftcode = DB_AppGiftcode.get_by_id(param.get('giftcode').upper())
					result['resultcode']=100
					
					if not giftcode:
						result['resultcode']=880
						result['resultmsg']="don't find giftcode"

					elif giftcode.user:
						result['resultcode']=890
						result['resultmsg']="this giftcode was used"

					elif self.session.get('giftcodeTime'):
						gifttime = cTime-int(self.session.get('giftcodeTime'))
						if gifttime < 3600:
							result['resultcode']=870
							result['resultmsg']="you don't use giftcode for 1H"


				else:
					result['resultcode']=880
					result['resultmsg']="don't find giftcode"
					
				
				result['state']='ok'
				if result.get('resultcode')==100:
					result['category']=giftcode.category
					result['value']=giftcode.value
					giftcode.useTime = int(cTime)
					giftcode.user = auInfo.key
					giftcode.put()
					self.session['giftcodeTime']=int(cTime)

			if 'addmail' in actions:#######################################################################################
				namespace_manager.set_namespace(gdNamespace)
				uInfo =  auInfo.uInfo.get()
				uInfo.mail = param.get('mail')
				uInfo.put()
				namespace_manager.set_namespace(appNamespace)

				result['state']='ok'
				auInfo.mail = param.get('mail')
				auInfo.putOn()

			if 'writelog' in actions:#######################################################################################
				newlog = DB_AppLog()
				category = param.get('category')
				if not category:
					category = 'defalut'
				newlog.text = param.get('log')
				newlog.category = category
				newlog.auInfo = auInfo.key
				newlog.put()
				result['state']='ok'
			
			if 'setuserdata' in actions:#######################################################################################
				if not type(param.get('userdata')):
					result['state']='error'
				else:
					if type(auInfo.userdata)==dict:
						auInfo.userdata.update(param.get('userdata'))
					else:
						auInfo.userdata = param.get('userdata')
					auInfo.putOn()
					result['state']='ok'

			if 'getuserdata' in actions:#######################################################################################
				result['userdata']=auInfo.userdata
				result['state']='ok'

			logging.info(result)
			allresult[commandID]=copy.deepcopy(result)
			result.clear()
			logging.info('########################### end command ###############################')
		namespace_manager.set_namespace(appNamespace)
		#put
		auInfo.doPut()
		#uInfo.doPut()
		#결과리턴
		resultStr = json.dumps(allresult,encoding="utf-8",ensure_ascii=False)
		logging.info("version 4")
		resultStr = CommandHandler.strToDesInBase64(resultStr,aInfo.secretKey)
		self.response.write(resultStr.strip())
		logging.info(resultStr)
		
	


	def get(self):
		self.post()		

	@classmethod
	def decParam(cls,param):
		re={}
		try:
			re = base64.decodestring(param)
			#re = re.decode('utf-8')
			#logging.info('decParam type')
			#logging.info(str(type(to)))
			re = json.loads(re) #json.dumps
		except Exception, e:
			return re
		return re
	
	@classmethod
	def strToDesInBase64(cls,text,skey):
		logging.info("str to desinbase64")
		logging.info("text type is")
		logging.info(type(text))

		obj = DES.new(skey,DES.MODE_ECB)
		
		if type(text) == unicode:	
			text = text.encode('utf-8')

		if len(text)%8>0:
			text = text + ' '*(8-len(text)%8)

		text=obj.encrypt(text)

		text=base64.b64encode(text)
		return text

	@classmethod
	def DesInBase64ToStr(cls,text,skey):
		logging.info("desinbase64 to str "+skey)
		text=text.replace(" ","+")
		logging.info(text)
		logging.info('repr')
		logging.info(repr(text))
		text=base64.b64decode(text)
		obj = DES.new(skey,DES.MODE_ECB)
		rStr=obj.decrypt(text)
		return rStr

	@classmethod	
	def encParam(cls,paramstr,skey):
		re = cls.DesInBase64ToStr(paramstr,skey) #base64.encodestring(paramstr)
		re = re.decode('utf-8')
		return re

	@classmethod
	def decToken(cls,token,skey):
		re={}
		try:
			token=token.replace(" ","+")
			to = base64.b64decode(token)
			#to = to.decode('uft-8')
			#logging.info('decToken type')
			#logging.info(str(type(to)))
			if len(token)%8>0:
				token = token + ' '*(8-len(token)%8)			

			if len(skey)%8>0:
				skey = skey + ' '*(8-len(skey)%8)

			obj = DES.new(skey,DES.MODE_ECB)
			to=obj.decrypt(to)
			#to=to.decode('utf-8')
			to=to.split("||")
			
			if to[0]:
				re['auID']=int(to[0])
			else:
				re['auID']=0

			re['udid']=to[1]
			re['flag']=to[2]
			re['lang']=to[3]
			re['nick']=to[4]
			re['email']=to[5]
			re['platform']=to[6]
			re['createTime']=to[7]
		except Exception, e:
		 	return re
		return re
	
	@classmethod
	def encToken(cls,auID,udid,flag,lang,nick,email,platform,createTime,skey):
		token = str(auID)+'||'+str(udid)+'||'+str(flag)+'||'+str(lang)+'||'+str(nick)+'||'+str(email)+'||'+str(platform)+'||'+str(createTime)+'||'
		
		if len(token)%8>0:
			token = token + ' '*(8-len(token)%8)			

		if len(skey)%8>0:
			skey = skey + ' '*(8-len(skey)%8)
		
		obj = DES.new(skey,DES.MODE_ECB)
		token = obj.encrypt(token)
		token = base64.b64encode(token)
		return token

	def printError(self,msg,code,skey):
		logging.info("print error"+msg)
		logging.info("print error"+str(code))
		re = {'state':'ok','error':msg, 'errorcode':code}
		text = CommandHandler.strToDesInBase64(json.dumps(re),skey)
		self.response.write(text.strip())

	def createError(self,msg,code):
		re = {'state':'ok','error':msg, 'errorcode':code}
		return re

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'hsgraphdogsessionsk',
}

app = webapp2.WSGIApplication([
	('/command', CommandHandler),
	('/command/.*', CommandHandler)
],
config=config,
debug=True)