///////////////////////////////////////////////////////////////////////////////
//jsonform 
///////////////////////////////////////////////////////////////////////////////
window.changeJsonFormInput = function(input,value) {
  $(input).val(value).change();
}


var keycount = 1

var jsonForm_typeSelector = function(formid,selectorName,defaultValue){
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
		for (var keyo in jsonObj){
			divid = parentKey+'_'+keyo
			rString +='<tr id="'+parentKey+'_'+keyo+'" isvalue="true" formid="'+formid+'"><td>'
			rString +='<input type="text" id="key_'+parentKey+'_'+keyo+'" value="'+keyo+'" class="jsonForminput" formid="'+formid+'">'
			rString +=jsonForm_typeSelector(formid,parentKey+'_'+keyo,typeof(jsonObj[keyo]))
			rString +='</td><td>'
			rString += jsonToForm(divid,jsonObj[keyo],formid)
			rString +='</td></tr>'
		}
		rString += footer
	}else if(typeof(jsonObj)=='object' && jsonObj!=null && jsonObj[0]!=null){
		rString = header
		for (var keyo in jsonObj){
			divid = parentKey+'_'+keyo
			rString +='<tr id="'+parentKey+'_'+keyo+'" isvalue="true" formid="'+formid+'"><td>'
			rString +='<input type="text" id="key_'+parentKey+'_'+keyo+'" value="'+keyo+'" class="jsonForminput" formid="'+formid+'" keytype="number" size=3 readonly>'
			rString +=jsonForm_typeSelector(formid,parentKey+'_'+keyo,typeof(jsonObj[keyo]))
			rString +='</td><td>'
			rString += jsonToForm(divid,jsonObj[keyo],formid)
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
	return rString
}

var JsonFormData=function(formid,jsondata){
	if(jsondata!=null){
		$('#'+formid).attr('value',JSON.stringify(jsondata))
		$('#jsonvalue_'+formid).val(JSON.stringify(jsondata))
	}
	valueData = JSON.parse($('#'+formid).attr('value'))
	return valueData;
}
var formToJson = function (jsonTableName,parentTable){
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
	if(newlist[0]!=null)
		return newlist
	else
		return newDict
}

var jsonForm_addField = function (e){
	findkey = $(this).attr('id').split("_")
	keystr = ""
	formpass = 0
	for (key in findkey){
		if(formpass>1)
			keystr += '["'+findkey[key]+'"]'

		formpass++
	}

	valueData = JsonFormData($(this).attr('formid'))
	//JSON.parse($('#'+$(this).attr('formid')).attr('value'))
	evalstring1 = 'valueData'+keystr+'[0]'
	check = eval(evalstring1)
	if(check != null)
		evalstring2 = 'valueData'+keystr+'.push(valueData'+keystr+'[0])'
	else
		evalstring2 = 'valueData'+keystr+'["newkey'+keycount+'"]='+'"newValue"'
		keycount++

	eval(evalstring2)

	JsonFormData($(this).attr('formid'),valueData)
	//$('#'+$(this).attr('formid')).attr('value',JSON.stringify(valueData))
	
	r = jsonToForm($(this).attr('formid'))
	$('#'+$(this).attr('formid')+'_value').html(r)
	
	JsonFormData($(this).attr('formid'),valueData)
}

var jsonForm_changeValue = function(e){
	valueData = formToJson('table_'+$(this).attr('formid'))
	JsonFormData($(this).attr('formid'),valueData)
	//$('#'+$(this).attr('formid')).attr('value',JSON.stringify(ValueData))
	r = jsonToForm($(this).attr('formid'))
	$('#'+$(this).attr('formid')+'_value').html(r)
	JsonFormData($(this).attr('formid'),valueData)
}

var jsonForm_changeType = function (e){
	findkey = $(this).attr('id').split("_")
	keystr = ""
	formpass = 0
	nowkey = ""
	for (key in findkey){
		if(findkey.length-1==formpass)nowkey = findkey[key]
		if(formpass>1 && findkey.length-1 > formpass)
			keystr += '["'+findkey[key]+'"]'

		formpass++
	}

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
	eval(evalstring)
	formid = '#'+$(this).attr('formid')
	
	//$(formid).attr('value',JSON.stringify(valueData))
	JsonFormData($(this).attr('formid'),valueData)

	r = jsonToForm($(this).attr('formid'))
	$(formid+'_value').html(r)

	valueData = formToJson('table_'+$(this).attr('formid'))
	//$(formid).attr('value',JSON.stringify(valueData))
	JsonFormData($(this).attr('formid'),valueData)
	r = jsonToForm($(this).attr('formid'))
	$(formid+'_value').html(r)
	
	JsonFormData($(this).attr('formid'),valueData)
}


var chageToJsonForm = function(){
	$('.jsonForm').each(function(index,item){
		divname = $(item).attr('id')
		$('#'+divname).html('<div id="'+divname+'_text" style="display:none"><textarea row=10 cols=10 class="jsonFormText" id="jsonvalue_'+divname+'" name="'+divname+'" formid="'+divname+'"></textarea></div><div id="'+divname+'_value"></div>')
		r = jsonToForm(divname)
		$('#'+divname+'_value').html(r)
		JsonFormData($(item).attr('id'),JSON.parse($('#'+divname).attr('value')))
	})
}

$(document).ready(function() {
			$('body').on('click','.addnew',jsonForm_addField)
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

			chageToJsonForm()
			//alert($('#type_jsonForm_stringkey').val())
			
		});























///////////////////////////////////////////////////////////////////////////////
//datalist 
///////////////////////////////////////////////////////////////////////////////


var timeToDate = function (timestamp, fmt) {
	fmt = fmt || "%Y/%M/%d %H:%m:%s"

	var date = new Date(Number(timestamp)*1000)

    function pad(value) {
        return (value.toString().length < 2) ? '0' + value : value;
    }

    return fmt.replace(/%([a-zA-Z])/g, function (_, fmtCode) {
        switch (fmtCode) {
        case 'Y':
            return date.getUTCFullYear();
        case 'M':
            return pad(date.getUTCMonth() + 1);
        case 'd':
            return pad(date.getUTCDate());
        case 'H':
            return pad(date.getUTCHours());
        case 'm':
            return pad(date.getUTCMinutes());
        case 's':
            return pad(date.getUTCSeconds());
        default:
            throw new Error('Unsupported format code: ' + fmtCode);
        }
    });
}

var jsonToStatsTable = function(stats){
	text = "<table border=1><tr><td>hour</td>"
	for(num=0;num<24;num++)
		text+="<td width=40>"+num+"</td>"
	text += "<td>total</td></tr>"
	for(keyx in stats){
		if(stats[keyx][0] == null)continue

		text += "<tr><td>"+keyx+"</td>"
		total=0
		for(num=0;num<24;num++){
			text+="<td>"+stats[keyx][num]+"</td>"
			total+=stats[keyx][num]
		}
		text +="<td>"+total+"</td></tr>"
	}
	text+="</table>"
	
	text+="<table border=1><tr>"
	for(keyx in stats){
		if(stats[keyx][0] != null)continue
		text+="<td><table border=1><tr><td colspan=2>"+keyx+"</td></tr>"
		for(subkey in stats[keyx]){
			text+="<tr><td>"+subkey+"</td><td>"+stats[keyx][subkey]+"</td></tr>"	
		}
		text+="</table></td>"
	}
	text+="</tr></table>"
	return text
}

var tddataConvert= function(tddata,convert){
	convertData =""
	if(convert=="timeToDate"){
		convertData=timeToDate(tddata,"%Y/%M/%d %H:%m:%s")
	}else if(convert=="jsonToStatsTable"){
		convertData=jsonToStatsTable(tddata)
	}else if(convert=="jsondata"){
		convertData=JSON.stringify(tddata)
	}else{
		convertData=tddata   							
	}
	return convertData
}

var setAttrValue = function(obj,value){
	if(typeof(value)=='object'){
		obj.attr('value',JSON.stringify(value))
		obj.attr('valueType','object')
	}else if(typeof(value)=='string'){
		obj.attr('value',value)
		obj.attr('valueType','string')
	}else if(typeof(value)=='number'){
		obj.attr('value',value)
		obj.attr('valueType','number')
	}
}

var getAttrValuePost = function(obj){
	valuetype = obj.attr('valueType')
	if(valuetype=="object"){
		return obj.attr('value')
	}else if(valuetype=="string"){
		return String(obj.attr('value'))
	}else if(valuetype=="number"){
		return Number(obj.attr('value'))
	}
}
var getAttrValue = function(obj){
	valuetype = obj.attr('valueType')
	if(valuetype=="object"){
		return JSON.parse(obj.attr('value'))
	}else if(valuetype=="string"){
		return String(obj.attr('value'))
	}else if(valuetype=="number"){
		return Number(obj.attr('value'))
	}
}

$(document).ready(function(){               //ajax실행중 loading글씨 보이기 
	

	var nextlist = function(){
		source = $('.datalist').attr('source')
		info = JSON.parse($('.datalist').attr('info'))
		db = $('.datalist').attr('db')
		info['db']=db

		$('.nexttd').html("wait")

   		$.getJSON(source, info, function(data){ 
				var viewlist = []
				var fieldcount = 0
				$(".datalist > thead > tr > th").each(function(index,item){
					viewtitle = {}
					if($(this).attr('computeField')=="on"){
						viewtitle["type"]="compute"
					}else if($(this).attr('deletebutton')=="on"){
						viewtitle["type"]="delete"
					}else{
						viewtitle["type"]="value"
					}

					viewtitle["func"]=$(this).attr('computeFunc')
					viewtitle["field"]=$(this).attr('field')
					viewtitle["convert"]=$(this).attr('convert')
					viewtitle["editor"]=$(this).attr('editor')
					viewtitle["index"]=$(this).attr('index')
					viewtitle["class"]=$(this).attr('class')

					viewlist.push(viewtitle)		
					fieldcount++
				})	

   				datalist = data['list']
   				resultcode = ""
   				for(i in datalist){
   					resultcode+='<tr id="'+datalist[i]['id']+'">'
   					for (key in viewlist){
   						if(viewlist[key]['type']=='value'){
   							tddata = datalist[i][viewlist[key]['field']]

   							tdvalue = ""
   							tdvaluetype=""
							if(typeof(tddata)=='object'){
								tdvalue = JSON.stringify(tddata)
								tdvaluetype='object'
							}else if(typeof(tddata)=='number'){
								tdvalue=tddata
								tdvaluetype='number'
							}else{
								tdvalue=tddata
								tdvaluetype='string'
							}

   							resultcode+='<td class="datafield '+viewlist[key]['class']+'" info=\'{"aID":"'+data['aID']+'","id":"'+datalist[i]['id']+'","db":"'+$('.datalist').attr('db')+'","field":"'+viewlist[key]['field']+'"}\' editor="'+viewlist[key]['editor']+'" convert="'+viewlist[key]['convert']+'" valueType="'+tdvaluetype+'" value=\''+tdvalue+'\'>'
   								
   							
	   						//if(viewlist[key]['index']=="on"){
	   						//	filename = location.pathname.split('/').slice(-1)[0]
	   						//	resultcode+='<a href='+filename+'?aID='+data['aID']+'&'+'limit='+data['limit']+'&filterfield='+viewlist[key]['field']+'&filtervalue='+datalist[i][viewlist[key]['field']]+'>'
	   						//}

	   						resultcode+=tddataConvert(tddata,viewlist[key]['convert'])

	   						//if(viewlist[key]['index']=="on")resultcode+='</a>'


   							resultcode+="</td>"
   						}else if(viewlist[key]['type']=='compute'){
   							funcname = viewlist[key]['func']
   							resultcode+=eval(funcname+"(datalist[i],viewlist[key]['class'])");
   						}else if(viewlist[key]['type']=='delete'){
   							resultcode+='<td><a href="#a" class="deletebtn '+viewlist[key]['class']+'" info=\'{"aID":"'+data['aID']+'","id":"'+datalist[i]['id']+'","db":"'+$('.datalist').attr('db')+'"}\' rowid="'+datalist[i]['id']+'">del</a></td>'
   						}

   					}

   					resultcode+="</tr>"
   				}

   				if(data['more']==true)
   					resultcode+='<tr><td class="nexttd" colspan='+fieldcount+'><a href="#a" class="nextbtn">NEXT</a></td></tr>'

				$('.nexttd').remove()
				$('.datalist > tbody:last').append(resultcode)     //div1에 내용 넣기  
				$('.datalist > tbody > tr:odd').addClass('datalistodd');
				
				delete data["list"]
				newinfo = JSON.stringify(data)
				$('.datalist').attr('info',newinfo)
   				

			 }  
		); 
		
   }

   $('body').on('click','.nextbtn',nextlist)


   $('body').on('dblclick','.datafield',function(){
   		if($('td[isEditing=on]').length>0) return
   		if($(this).attr('editor')=="undefined") return
   		if ($(this).attr('isEditing')!="on"){

   			if($(this).attr('editor')=="text")
   				$(this).html('<input value=\''+$(this).html()+'\' id="valueeditor" style="width:100%"><br><input type="button" value="edit" class="editbtn"><input type="button" value="cancel" class="cancelbtn">')
   			else
   				$(this).html('<div id="valueeditor" class="jsonForm" value=\''+$(this).html()+'\'></div><br><input type="button" value="edit" class="editbtn"><input type="button" value="cancel" class="cancelbtn">')
   				chageToJsonForm()

   			$(this).attr('isEditing',"on")
   		}
   })



   $('body').on('click','.deletebtn',function(){

		if (!confirm("delete?")){
			return
		}

   		var rowid = $(this).attr('rowid')
   		info = JSON.parse($(this).attr('info'))
   		source = $('.datalist').attr('source')
   		info['mode']="delete"
   		$.getJSON(source, info, function(data){ 
   			if(data['result']=="ok"){
   				$('#'+rowid).remove()
   			}
   		});
   })

   $('body').on('click','.cancelbtn',function(){
   		edittr = $('td[isEditing=on]').last()
   		
   		edittr.html(tddataConvert(getAttrValue(edittr),edittr.attr('convert')))
   		
   		edittr.removeAttr('isEditing')
   })
   
   $('body').on('click','.editbtn',function(){

   		edittd = $('td[isEditing=on]').last()

		
		veditor = $('#valueeditor').last()
   		if(edittd.attr('valueType')=="object"){
   			edittd.attr('value',veditor.attr('value'))
   		}else{
   			
   			edittd.attr('value',veditor.val())
   		}
   		//edittd.html(edittd.attr('value'))
   		//edittd.attr('isEditing','off')
   		//edittd.attr('oData','')

   		info = JSON.parse(edittd.attr('info'))
   		source = $('.datalist').attr('source')
   		info['mode']="edit"
   		info['value']=getAttrValuePost(edittd)
   		$.getJSON(source, info, function(data){ 
   			if(data['result']=="ok"){
   				edittr = $('td[isEditing=on]').last()
   				edittr.html(tddataConvert(getAttrValue(edittr),edittr.attr('convert')))
   				edittr.attr('isEditing','off')
   			}
   		});
   })

   if($('.datalist').length>0)nextlist()

   $(".datalist > thead > tr > th").each(function(index,item){
   		datatable = $('.datalist').attr('info')
		info = JSON.parse(datatable)

   		if($(this).attr('index')=="on"){
   			headname = $(this).html()
   			$(this).attr('view',headname)

   			clearbtn=""
   			if(info['filterfield']==$(this).attr('field')){
				clearbtn = " <input type=button value='clear filter' class='clearfilter'>"
			}
   			$(this).html("<a href=#a class='filterlink'>"+headname+"</a>"+clearbtn)	
   		}
   		

   });

	$('body').on('click','.filterlink',function(){
		head = $(this).parent("th")
		datatable = $('.datalist').attr('info')
		info = JSON.parse(datatable)
		ftvalue = ""
		if(info['filterfield']==head.attr('field')){
			ftvalue = info['filtervalue']
		}
		head.html(head.attr('view')+"<br><input type=text class='filtervalue' value='"+ftvalue+"'><input type=button value='filter' class='dofilter'><input type=button value='x' class='cancelfilter'>")
   })

	$('body').on('click','.cancelfilter',function(){
		head = $(this).parent("th")
   		datatable = $('.datalist').attr('info')
		info = JSON.parse(datatable)

		clearbtn=""
   		if(info['filterfield']==head.attr('field')){
			clearbtn = " <input type=button value='clear filter' class='clearfilter'>"
		}

		head.html("<a href=#a class='filterlink'>"+head.attr('view')+"</a>"+clearbtn)	
	})

	$('body').on('click','.dofilter',function(){
		head = $(this).parent("th")
		datatable = $('.datalist').attr('info')
		info = JSON.parse(datatable)

		filename= location.pathname.split('/').slice(-1)[0]
		url = filename+'?aID='+info['aID']+'&filterfield='+head.attr('field')+'&filtervalue='+head.children('.filtervalue').val()
		
		$(location).attr('href',url);

	})

	$('body').on('click','.clearfilter',function(){
		head = $(this).parent("th")
		datatable = $('.datalist').attr('info')
		info = JSON.parse(datatable)

		filename= location.pathname.split('/').slice(-1)[0]
		url = filename+'?aID='+info['aID']
		
		$(location).attr('href',url);

	})
});  










































