#encoding = utf-8#
import os
import sys
import re
import shutil
import time
import xlwt
import subprocess
import concurrent.futures
from PIL import Image
import argparse
'''
网店工商信息图片文字提取
@Hypo
2018-06-20
'''
#get parse
parse=argparse.ArgumentParser()
parse.add_argument("--search_dir",type=str,default="./",help="dir to search '天猫工商信息执照'")
parse.add_argument("--tmp_dir",type=str,default="./tmp"+'/',help="dir to save temp images")
parse.add_argument("--model",type=str,default="chi_sim_fast",help="tesseract OCR per_train model:chi_sim_fast,chi_sim_best,chi_sim_vert")
parse.add_argument("--workers",type=int,default=3,help="OCR workers")
parse.add_argument("--sort",type=str,default="int",help="output sort model,'int' for nummber,'str' for string")
args , _ = parse.parse_known_args(sys.argv[1:])

searchdir = args.search_dir
imgtmpdir = args.tmp_dir+'/'
model = args.model
WORKER = args.workers
sortmod = args.sort

def findimgdir(rootdir):
    file_list=[]
    for root,dirs,files in os.walk(rootdir): 
        for file in files:
            file_list.append(os.path.join(root,file))
        for dir in dirs:
            findimgdir(dir)

    for file in file_list:
        if re.search(r'天猫工商信息执照.*png$|天猫工商信息执照.*jpg$|天猫工商信息执照.*jpeg$|天猫工商信息执照.*bmp$', file, re.I):
            return os.path.split(file)[0]


def findimg(filedir):
    imgnamelist=[]
    filenamelist=os.listdir(filedir)
    for filename in filenamelist:
        if re.search(r'png$|jpg$|jpeg$|bmp$', filename, re.I):
            imgnamelist.append(filename)
    return imgnamelist

#images preproccess
def ImgPreDeal(path,newdir):
    #Get filepath,filename and extension
    (filepath,tempfilename) = os.path.split(path)
    (filename,extension) = os.path.splitext(tempfilename)
    if re.search(r'png$', path, re.I):
        try: #Try to open then handle the images
            img = Image.open(path)
            x,y = img.size 
            newimage = Image.new('RGBA', img.size, (255,255,255))  #get a white backgrund
            newimage.paste(img, (0, 0, x, y), img)   #Turn png backgrund into white then save
            newimage=newimage.crop((0,0,int(x*0.5),int(y/5)))    #Crop the image
            newimage.save(newdir+filename+extension)
        except:   #if can't open ,it maybe a jpg
            try:
                shutil.copyfile(path,newdir+filename+".jpg")
                newimage = Image.open(newdir+filename+".jpg")
                x,y = newimage.size
                newimage = newimage.convert('L')    #Gray
                if (x>3000)|(y>3000):    #Resize and crop
                    newimage=newimage.resize((int(x/4),int(y/4)))
                    newimage=newimage.crop((0,0,int(x/4),int(y/8)))
                else:
                    newimage=newimage.crop((0,0,x,int(y/2)))
                newimage.save(newdir+filename+".jpg")
                print(filename+extension+" maybe a jpg photo")
            except:
                print(path,'Pre-Processing Failed!')   
    else:   #Copy others
        try:
            img = Image.open(path)
            x,y = img.size
            newimage = img.convert('L')    #Gray
            if (x>3000)|(y>3000):    #Resize and crop
                newimage=newimage.resize((int(x/4),int(y/4)))
                newimage=newimage.crop((0,0,int(x/4),int(y/8)))
            else:
                newimage=newimage.crop((0,0,x,int(y/2)))
            newimage.save(newdir+filename+extension)
        except:
            shutil.copyfile(path,newdir+filename+extension)
            print(path,'Pre-Processing Failed!')

#Find informations (change it can improve successful rate)
def findinfos(txtpath):
    #Read results and save in String
    try:
        fp = open(txtpath,'rb')
        txt = fp.read().decode()#change byte into String
        fp.close
    except:
        return "None","None",0
    #Find "注册号" and "名称"  (change it can improve successful rate),don't try to change it into RE.
    #for example: 企业注册号913302055612570177企业名称宁波中哲藏尚电子裴务有限公司
    txt=txt.replace(" ","")
    txt=txt.replace('\n',"")
    txt=txt.replace(':',"")

    ID_location=txt.find("号")+1
    name_location=txt.find("称")+1
    ID_location_end=name_location-4
    name_location_end=txt.find("限")+3
    #(change it can improve successful rate)
    if (ID_location-1>0)&(name_location-1>0)&(name_location_end-3>0):
        return txt[ID_location:ID_location_end],txt[name_location:name_location_end].replace(":",""),1
    else:       
        try:
            ID = re.search('\d+', txt).group()
            name_location_end=txt.find("限")+3
            name_location=name_location_end-13
            return str(ID),txt[name_location:name_location_end],1
        except Exception as e:
            print('\n',e,'\n')
            return "None","None",0 

def runOCR(name):#Run OCR in Popen
    # imgtmpdir="./tmp"+'/'
    # model="chi_sim_old"
    OCR=subprocess.Popen("tesseract "+imgtmpdir+name+" "+imgtmpdir+name+" -l "+model, shell=True)
    OCR.wait()
    return findinfos(imgtmpdir+name+".txt")

def main():
    start = time.time()
    IDlist=[]
    CompanyNamelist=[]
    successcnt=0
    #Search image
    imgdir = findimgdir(searchdir)+'/'
    imgnamelist=findimg(imgdir)
    print('The dir of 天猫工商信息执照 is:',imgdir)
    print("Find images: "+str(len(imgnamelist)))    
    #image preproccess and save
    if not os.path.exists(imgtmpdir):
        os.makedirs(imgtmpdir)
    for imgname in imgnamelist:
        ImgPreDeal(imgdir+imgname,imgtmpdir)    
    #Search image again
    imgnamelist.clear()
    imgnamelist=findimg(imgtmpdir)
    if sortmod == "int":
        try:
            imgnamelist = sorted(imgnamelist,key = lambda i:int(re.match(r'(\d+)',i).group()))
        except Exception as e:
            print(e)
            imgnamelist.sort()
    elif sortmod == "str":
        imgnamelist.sort()
    print('name of images:\n',imgnamelist)

    #Run OCR
    with concurrent.futures.ProcessPoolExecutor(max_workers=WORKER) as executor:
        for imgname,(ID,CompanyName,cnt) in zip(imgnamelist,executor.map(runOCR,imgnamelist)):
            print(imgname,'is processing!')
            IDlist.append(ID)
            CompanyNamelist.append(CompanyName)
            successcnt+=cnt

    # Save Excel book
    book = xlwt.Workbook(encoding='utf-8')
    sheet1 = book.add_sheet('Sheet 1')
    sheet1.write(0,0,"图片名称")
    sheet1.write(0,1,"企业名称")
    sheet1.write(0,2,"企业注册号")
    for i in range(0,len(imgnamelist)):    
        sheet1.write(i+1,0,imgnamelist[i])
        sheet1.write(i+1,1,CompanyNamelist[i])
        sheet1.write(i+1,2,IDlist[i])
    book.save('./result.xls')

    # Save Excel book (no image name)
    book = xlwt.Workbook(encoding='utf-8')
    sheet1 = book.add_sheet('Sheet 1')
    sheet1.write(0,0,"企业名称")
    sheet1.write(0,1,"企业注册号")
    for i in range(0,len(imgnamelist)):    
        sheet1.write(i+1,0,CompanyNamelist[i])
        sheet1.write(i+1,1,IDlist[i])
    book.save('./result_no_image_name.xls')
    
    #Print result
    print(CompanyNamelist)
    print(IDlist)
    print(str(successcnt)+" images success!")
    shutil.rmtree(imgtmpdir)
    end = time.time()
    print('cost time:','%.2f' % (end-start+0.2),'s')

if __name__ == '__main__':
    main()
