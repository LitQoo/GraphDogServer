
$(document).ready(function() {
			var jsonForm_typeSelector = function(formid,selectorName,defaultValue){
				console.log('selectname:'+selectorName)
				typelist = ["string","number","boolean","object","array","image","delete"]
				rString = '<select id="type_'+selectorName+'" formid="'+formid+'" class="jsonFormselect" valueinput="value_'+selectorName+'">'
				for(key in typelist){
					if(typelist[key]==defaultValue){
						rString += '<option value="'+typelist[key]+'" selected>'+typelist[key]+'</option>'	
					}else{
						rString += '<option value="'+typelist[key]+'">'+typelist[key]+'</option>'
					}
				}
				rString += '</select>'
				return rString
			}
			var jsonToForm = function(parentKey,jsonObj,formid){
				isFirst = false
				header=''
				if(formid=='' || formid==null){
					formid=parentKey
				}
				if(jsonObj==null && typeof(jsonObj)!='object'){
					isFirst = true
					parentForm = $('#'+formid)
					console.log('jsonToForm')
					console.log(parentForm.attr('value'))

					if(parentForm.attr('value'))
						jsonObj = JSON.parse(parentForm.attr('value'))

					if(jsonObj==null)jsonObj={}

					//header+='<div style="display:none"><textarea row=10 cols=10 id="jsonvalue_'+formid+'" name="'+formid+'"></textarea></div>'
				}

				header += '<table border=1 id="table_'+parentKey+'" formid="'+formid+'"><tr><td colspan=2><a href="#a" id="div_'+parentKey+'" class="addnew" formid="'+formid+'">add row</a></td></tr>'
				footer = '</table>'
				rString=''
				if(typeof(jsonObj)=='object' && jsonObj!=null && jsonObj[0]==null){
					rString = header
					for (var key in jsonObj){
						divid = parentKey+'_'+key
						rString +='<tr id="'+parentKey+'_'+key+'" isvalue="true" formid="'+formid+'"><td>'
						rString +='<input type="text" id="key_'+parentKey+'_'+key+'" value="'+key+'" class="jsonForminput" formid="'+formid+'">'
						rString +=jsonForm_typeSelector(formid,parentKey+'_'+key,typeof(jsonObj[key]))
						rString +='</td><td>'
						rString += jsonToForm(divid,jsonObj[key],formid)
						rString +='</td></tr>'
					}
					rString += footer
				}else if(typeof(jsonObj)=='object' && jsonObj!=null && jsonObj[0]!=null){
					rString = header
					for (var key in jsonObj){
						divid = parentKey+'_'+key
						rString +='<tr id="'+parentKey+'_'+key+'" isvalue="true" formid="'+formid+'"><td>'
						rString +='<input type="text" id="key_'+parentKey+'_'+key+'" value="'+key+'" class="jsonForminput" formid="'+formid+'" keytype="number" size=3 readonly>'
						rString +=jsonForm_typeSelector(formid,parentKey+'_'+key,typeof(jsonObj[key]))
						rString +='</td><td>'
						rString += jsonToForm(divid,jsonObj[key],formid)
						rString +='</td></tr>'
					}
					rString += footer
				}else if(typeof(jsonObj)=='boolean'){
					rString +='<select id="value_'+parentKey+'" class="jsonForminput" formid="'+formid+'">'
					if(jsonObj==true)rString +='<option>true</option><option>false</option>'
					else rString +='<option>false</option><option>true</option>'
					rString +='</select>'
				}else{
					rString +='<input type="text" id="value_'+parentKey+'" value="'+jsonObj+'" class="jsonForminput" formid="'+formid+'">'
				}

				console.log('chagne5')
				return rString
			}

			var JsonFormData=function(formid,jsondata){
				if(jsondata!=null){
					console.log('chagne3:'+$('#jsonvalue_'+formid).val())
					$('#'+formid).attr('value',JSON.stringify(jsondata))
					$('#jsonvalue_'+formid).val(JSON.stringify(jsondata))
					console.log('jsonvalue_'+formid)
					console.log(JSON.stringify(jsondata))
					console.log('chagne4:'+$('#jsonvalue_'+formid).val())


				}
				console.log('jsonFormData:'+formid)
				valueData = JSON.parse($('#'+formid).attr('value'))
				console.log('chagne9')
				return valueData;
			}
			var formToJson = function (jsonTableName,parentTable){
				console.log('formToJson')
				var newDict = {}
				var newlist = []
				isFirst=false
				if(parentTable==null){
					isFirst=true
					parentTable=jsonTableName
				}
				$('#'+jsonTableName+' > tbody > tr[isvalue=true]').each(function(index,item){
					type = $('#type_'+$(item).attr('id')).val()
					path = '#table_'+$(item).attr('id')
					valueid = '#value_'+$(item).attr('id')
					keyid = '#key_'+$(item).attr('id')
					keyname = $(keyid).val()
					keytype = $(keyid).attr('keytype')
					value=""

					//alert(path)
					if(String($(valueid).val())!="-:#:DELETE:#:-"){
						if(keytype=='number'){
							keyname=Number(keyname)
							console.log('keyname is number ,'+keyname)
							if(type=='string'){
								newlist[keyname]  = String($(valueid).val())
							}else if(type=='number'){
								newlist[keyname] = Number($(valueid).val())
							}else if(type=='boolean'){
								if ($(valueid).val()=="true")
									newlist[keyname] = true
								else
									newlist[keyname] = false
							}else if (type=='object'){
									newlist[keyname] = formToJson('table_'+$(item).attr('id'),parentTable)
							}
						}else{
							if(type=='string'){
								newDict[keyname]  = String($(valueid).val())
							}else if(type=='number'){
								newDict[keyname] = Number($(valueid).val())
							}else if(type=='boolean'){
								if ($(valueid).val()=="true")
									newDict[keyname] = true
								else
									newDict[keyname] = false
							}else if (type=='object'){
									newDict[keyname] = formToJson('table_'+$(item).attr('id'),parentTable)
							}

						}
							

					}


				})
				console.log('formToJson:'+JSON.stringify(newDict))
				if(newlist[0]!=null)
					return newlist
				else
					return newDict
			}

			var jsonForm_addField = function (e){
				console.log($(this).attr('id'))
				findkey = $(this).attr('id').split("_")
				keystr = ""
				formpass = 0
				for (key in findkey){
					if(formpass>1)
						keystr += '["'+findkey[key]+'"]'

					formpass++
				}

				console.log('addField')
				valueData = JsonFormData($(this).attr('formid'))
				//JSON.parse($('#'+$(this).attr('formid')).attr('value'))
				evalstring1 = 'valueData'+keystr+'[0]'
				check = eval(evalstring1)
				if(check != null)
					evalstring2 = 'valueData'+keystr+'.push(valueData'+keystr+'[0])'
				else
					evalstring2 = 'valueData'+keystr+'["newkey"]='+'"newValue"'
				
				console.log(evalstring2)
				eval(evalstring2)

				JsonFormData($(this).attr('formid'),valueData)
				//$('#'+$(this).attr('formid')).attr('value',JSON.stringify(valueData))
				
				console.log($('#'+$(this).attr('formid')).attr('value'))
				console.log(JSON.stringify(valueData))

				r = jsonToForm($(this).attr('formid'))
				$('#'+$(this).attr('formid')+'_value').html(r)
				$('.addnew').click(jsonForm_addField);

				JsonFormData($(this).attr('formid'),valueData)
			}

			var jsonForm_changeValue = function(e){
				valueData = formToJson('table_'+$(this).attr('formid'))
				JsonFormData($(this).attr('formid'),valueData)
				//$('#'+$(this).attr('formid')).attr('value',JSON.stringify(ValueData))
				r = jsonToForm($(this).attr('formid'))
				$('#'+$(this).attr('formid')+'_value').html(r)
				$('.addnew').click(jsonForm_addField);
				console.log('chagne1')
				JsonFormData($(this).attr('formid'),valueData)
				console.log('chagne2')
			}

			var jsonForm_changeType = function (e){
				findkey = $(this).attr('id').split("_")
				keystr = ""
				formpass = 0
				nowkey = ""
				for (key in findkey){
					console.log(key)
					if(findkey.length-1==formpass)nowkey = findkey[key]
					if(formpass>1 && findkey.length-1 > formpass)
						keystr += '["'+findkey[key]+'"]'

					formpass++
				}
				console.log(nowkey)

				valueData = JSON.parse($('#'+$(this).attr('formid')).attr('value'))
				evalstring=""
				if($(this).val()=="object"){
					evalstring = 'valueData'+keystr+'["'+nowkey+'"]='+'{"newkey":"newvalue"}'
				}else if($(this).val()=="string"){
					evalstring = 'valueData'+keystr+'["'+nowkey+'"]='+'"string"'
				}else if($(this).val()=="number"){
					evalstring = 'valueData'+keystr+'["'+nowkey+'"]='+'123'
				}else if($(this).val()=="boolean"){
					evalstring = 'valueData'+keystr+'["'+nowkey+'"]='+'false'
				}else if($(this).val()=="array"){
					evalstring = 'valueData'+keystr+'["'+nowkey+'"]=["newvalue"]'
				}else if($(this).val()=="image"){
					evalstring = 'valueData'+keystr+'["'+nowkey+'"]='+'"images"'
					window.open('/developcenter/imageselector/?input='+$(this).attr('valueinput'),'imageselector','width=500 height=500 menubar=no status=no')
				}else if($(this).val()=="delete"){
					evalstring = 'valueData'+keystr+'["'+nowkey+'"]="-:#:DELETE:#:-"'
				}
				console.log(evalstring)
				eval(evalstring)
				console.log(JSON.stringify(valueData))
				formid = '#'+$(this).attr('formid')
				
				console.log('chagne11')
				//$(formid).attr('value',JSON.stringify(valueData))
				JsonFormData($(this).attr('formid'),valueData)

				console.log('chagne22')
				r = jsonToForm($(this).attr('formid'))
				$(formid+'_value').html(r)

				console.log('chagne33')
				valueData = formToJson('table_'+$(this).attr('formid'))
				//$(formid).attr('value',JSON.stringify(valueData))
				JsonFormData($(this).attr('formid'),valueData)
				r = jsonToForm($(this).attr('formid'))
				$(formid+'_value').html(r)
				$('.addnew').click(jsonForm_addField);

				console.log('chagne55')
				JsonFormData($(this).attr('formid'),valueData)
				console.log('chagne66')
			}



			//$('.jsonForm').each(function(index,item){
			//	divname = 'jsonForm'
			//	r = jsonToForm(loadData,divname)
			//	$('#'+divname).html(r)
			//})
			
			/*
				parentForm = $('#'+formid)
				alert(parentForm.attr('value'))
				jsonObj = JSON.parse(parentForm.attr('value'))

				isFirst = true
					parentForm = $('#'+formid)
					console.log('jsonToForm')
					console.log(parentForm.attr('value'))
					jsonObj = JSON.parse(parentForm.attr('value'))
					header+='<div style="display:none"><textarea row=10 cols=10 id="jsonvalue_'+formid+'" name="'+formid+'"></textarea></div>'
			*/

			$('.jsonForm').each(function(index,item){
				divname = $(item).attr('id')
				$('#'+divname).html('<div id="'+divname+'_text" style="display:none"><textarea row=10 cols=10 class="jsonFormText" id="jsonvalue_'+divname+'" name="'+divname+'" formid="'+divname+'"></textarea></div><div id="'+divname+'_value"></div>')
				r = jsonToForm(divname)
				$('#'+divname+'_value').html(r)
				JsonFormData($(item).attr('id'),JSON.parse($('#'+divname).attr('value')))
			})
			$('.addnew').click(jsonForm_addField);
			$('body').on('change','.jsonForminput',jsonForm_changeValue)
			$('body').on('change','.jsonFormselect',jsonForm_changeType)
			$('body').on('change','.jsonFormText',function(e){
				formid=$(this).attr('formid')
				$('#'+formid).attr('value',$(this).val())
				r = jsonToForm(formid)
				$('#'+formid+'_value').html(r)
				JsonFormData(formid,JSON.parse($('#'+formid).attr('value')))
				//alert('change')
			})
			$('body').on('change','.jsonForm',function(e){
				console.log('##############################')
				//alert('change')
			})

			//alert($('#type_jsonForm_stringkey').val())
			
		});