# -*- coding: utf-8 -*-
import hashlib
import web
import lxml
import time
import os
import urllib2,json
import md5
import random
from lxml import etree


    


class WeixinInterface:

    def __init__(self):
        self.app_root = os.path.dirname(__file__)
        self.templates_root = os.path.join(self.app_root, 'templates')
        self.render = web.template.render(self.templates_root)
    
   
    
    def GET(self):
        #获取输入参数
        data = web.input()
        signature=data.signature
        timestamp=data.timestamp
        nonce=data.nonce
        echostr=data.echostr
        #自己的token
        token="chen" #这里改写你在微信公众平台里输入的token
        #字典序排序
        list=[token,timestamp,nonce]
        list.sort()
        sha1=hashlib.sha1()
        map(sha1.update,list)
        hashcode=sha1.hexdigest()
        #sha1加密算法

        #如果是来自微信的请求，则回复echostr
        if hashcode == signature:
            return echostr
        
    def POST(self):
        str_xml = web.data()  # 获得post来的数据
        xml = etree.fromstring(str_xml)  # 进行XML解析
        msgType = xml.find("MsgType").text
        fromUser = xml.find("FromUserName").text
        toUser = xml.find("ToUserName").text
        if msgType == 'text':
            content = xml.find("Content").text
            if content == 'help':
                return self.render.reply_text(fromUser, toUser, int(time.time()), "随便看看？（对不起我功能有限QAQ）")
            else:
                if type(content).__name__ == "unicode":
                    content = content.encode('UTF-8')
                    trans=self.Youdao(content,1)
                else:
                    trans=self.Youdao(content,2)
                return self.render.reply_text(fromUser,toUser,int(time.time()),trans)
        if msgType == 'event':
            if xml.find("Event").text == 'subscribe':  # 关注的时候的欢迎语
                return self.render.reply_text(fromUser, toUser, int(time.time()), u"谢谢你的关注，我是良仔")
        
    def Youdao(self,word,transto):
        appKey = '2c2cccda71d727ce'
        secretKey = 'jSZ1B960SXhJS0vq70ig6h7r09QiPX5t'
        myurl = 'http://openapi.youdao.com/api'
        salt = random.randint(1, 65536)
        sign = appKey + word + str(salt) + secretKey
        m1 = md5.new()
        m1.update(sign)
        sign = m1.hexdigest()
        if transto == 1:
            url = myurl + '?appKey=' + appKey + '&q=' + urllib2.quote(word) + '&from=zh-CHS&to=EN'+ '&salt=' + str(salt) + '&sign=' + sign
        else:
            url=myurl + '?appKey=' + appKey + '&q=' + urllib2.quote(word) +  '&from=EN&to=zh-CHS' + '&salt=' + str(salt) + '&sign=' + sign
        resp = urllib2.urlopen(url)
        fanyi = json.loads(resp.read())      
        if  fanyi['errorCode'] == '0':           
            if 'basic' in fanyi.keys():
                trans = u'%s:\n%s\n%s\n网络释义：\n%s'%(fanyi['query'],''.join(fanyi['translation']),' '.join(fanyi['basic']['explains']),''.join(fanyi['web'][0]['value']))
                return trans               
            '''else:
                trans =u'%s:\n基本翻译:%s\n'%(fanyi['query'],''.join(fanyi['translation']))        
                return trans  '''              
        elif fanyi['errorCode'] == '103':
             return u'对不起，要翻译的文本过长'
        elif fanyi['errorCode'] == '113':
             return u'对不起，请输入翻译文本'
        elif fanyi['errorCode'] == '102':
             return u'对不起，不支持的语言类型'
        else:
             return u'对不起，您输入的单词%s无法翻译,请检查拼写'% word