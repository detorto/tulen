from twill import get_browser
from bs4 import BeautifulSoup
import urllib
import urllib2
from PIL import Image                                                                                
b = get_browser()

from twill.commands import *
go("https://yandex.ru/showcaptcha?retpath=https%3A//yandex.ru/images/search%3Ftext%3Dasdasd_4a45f2c23ad1f84bbfdd653df8ea0c58&t=0/1477587791/d43bb1f476116a7a81765e7f9154f7ba&s=55f886314676bd1a3375c4ddd0991033")

html = b.get_html()

s = BeautifulSoup(html,"html.parser")

i = s.find("img", { "class" : "form__captcha" })
capthca_url = i.get("src")

#print dir (b)
#print dir()

rep = b.get_form_field(b.get_all_forms()[0],"0").value
key = b.get_form_field(b.get_all_forms()[0],"1").value
retpath = b.get_form_field(b.get_all_forms()[0],"2").value

req = urllib2.Request(capthca_url, None)

raw_img = urllib2.urlopen(req).read()
path = "1.jpg"
f = open(path, 'wb')
f.write(raw_img)
f.close()

img = Image.open('1.jpg')
img.show() 

url = "https://yandex.ru/checkcaptcha?"
i = raw_input()

getVars = {'key': key, "rep": i, "retpath":retpath }
print url + urllib.urlencode(getVars)
go(url + urllib.urlencode(getVars))
#b.showforms()
#formclear('1')
#fv("1","rep","hello")
#formaction('1', 'https://yandex.ru/checkcaptcha')
#submit('0')
