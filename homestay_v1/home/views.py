#coding=utf-8
from django.shortcuts import render,redirect
from django.http import HttpResponse

# Create your views here.
from .common import sendEmail,getRandom,getPasswdHash,getNow,getInter
from .models import people,HouseAttr,Img,CollectionHouse,HouseBook,houseCommentInfor,idCard
import json,datetime

"""
1.新用户注册
    昵称存在？
    邮箱存在？

    成功
    未成功

"""

def register(request):
    msg = ""
    if request.method == "POST":
        nichen = request.POST.get('nichen', None)
        email = request.POST.get('email', None)
        if nichen and email:
            ###1.检查nichen,email 是否已经注册过(successstatus =1) 前端处理，后台也处理

            nichenobj = people.objects.filter(nichen=nichen)
            if nichenobj:
                nichenStatus = 1
            else:
                nichenStatus = 0

            emailobj = people.objects.filter(email=email)
            if emailobj:
                emailStatus = 1
            else:
                emailStatus = 0

            if nichenStatus == 0 and emailStatus == 0:
                randString = getRandom()
                people_obj = people(
                    nichen=nichen,
                    email=email,
                    sendEmailRandom=randString,
                )
                people_obj.save()
                mailText = """ 
                         <p>彭芽丽民宿网站欢迎你...</p>
                          <p><a href="http://192.168.164.40:9000/home/searchPassword/?mail=%s&randString=%s">请点击这个链接完成账户注册任务！</a></p>
                           """ % (email, randString)

                sendEmailResult = sendEmail(email, mailText)

                if sendEmailResult:
                    msg = "email发送成功，请登陆到邮箱，完成后续的操作"
                else:
                    msg = "email发送失败，请核实您的邮箱或设置邮箱的代理开启"
                ##发送邮件

            elif nichenStatus == 0 and emailStatus == 1:
                msg = "邮箱已注册"

            elif nichenStatus == 1 and emailStatus == 0:
                msg = "昵称已注册"
            else:
                peopleObj = people.objects.filter(nichen=nichen, email=email)
                if peopleObj:
                    peopleObj = peopleObj[0]
                    if peopleObj.registerStatus == 1:
                        msg = "账号已经注册成功，请直接登陆"
                    else:
                        randString = getRandom()
                        peopleObj.sendEmailRandom = randString
                        peopleObj.save()

                        mailText = """
                        <p>彭芽丽民宿网站欢迎你...</p>
                        <p><a href="http://192.168.164.40:9000/home/searchPassword/?mail=%s&randString=%s">请点击这个链接完成账户注册任务！</a></p>
                        """ % (email, randString)

                        sendEmailResult = sendEmail(email, mailText)
                        if sendEmailResult:
                            msg = "email发送成功，请登陆到邮箱，完成后续的操作"
                        else:
                            msg = "email发送失败，请核实您的邮箱或设置邮箱的代理开启"
        else:
            msg = "昵称/email不能为空"
        return render(request, "register.html", {"error": msg})
    return render(request, "register.html")


def login(request):
    msg=""
    user=""
    if request.method=="POST":
        email=request.POST.get('email',None)
        passwd=request.POST.get('passwd',None)

        if email and passwd:
            peopleObj=people.objects.filter(email=email)
            if peopleObj:
                peopleObj=peopleObj[0]
                if peopleObj.password==getPasswdHash(passwd.encode('utf-8')):
                    ##登陆成功，设置session
                    # print (peopleObj.nichen)
                    request.session['is_login']={"email":peopleObj.email}

                    ##如果认证通过跳转到index页面，否则跳转到认证选择页面
                    # print (peopleObj.registerStatus)
                    if peopleObj.authInformation==0:
                        return redirect('/home/loginAfter/')
                    else:
                        return redirect('/home/index/')
                else:
                    msg="密码不正确"
            else:
                msg="账户不存在"
        else:
            msg="email 或 密码不能为空"

    return render(request,"login.html",{'msg':msg,"user":user})






def updatePassword(request):
    user=""
    msg=""
    loginObj=request.session.get('is_login',None)
    if loginObj!=None:
        user=loginObj.get('user')

    if request.method=="POST":
        email=request.POST.get('email',None)
        if  email:
            ###1.检查nichen,email 是否已经注册过(successstatus =1) 前端处理，后台也处理

            randString = getRandom()
            ##没注册成功
            peopleObj=people.objects.get(email=email)
            if peopleObj:
                randString=getRandom()
                peopleObj.sendEmailRandom=randString
                peopleObj.save()

                mailText = """
                        <p>Python 邮件发送测试...</p>
                        <p><a href="http://192.168.164.40:9000/home/searchUpdatePassword/?mail=%s&randString=%s">请点击这个链接，！</a></p>
                        """ % (email, randString)

                sendEmailResult = sendEmail(email, mailText)

                # sendEmailResult = sendEmail(email, randString)
                if sendEmailResult:
                    msg = "email发送成功，请登陆到邮箱，完成后续的操作"
                else:
                    msg = "email发送失败，请核实您的邮箱或设置邮箱的代理开启"
            else:
                msg="账户不存在！"

        else:
            error="email不能为空"
        return render(request,"register.html",{"error":msg})

    return render(request,'updatePassword.html',{'user':user})

def searchUpdatePassword(request):
    msg = ""
    mail=""
    if request.method=="POST":
        email=request.POST.get('mail',None)
        passwd1=request.POST.get('passwd1',None)
        passwd2 = request.POST.get('passwd2',None)
        print (passwd1,passwd2,mail)
        if email and passwd1 and passwd1==passwd2:
            passwdMd5=getPasswdHash(passwd1.encode('utf-8'))
            peopleObj=people.objects.get(email=email)
            peopleObj.password = passwdMd5
            peopleObj.save()

            msg="用户密码更新成功"
            # return redirect('/home/index/')

        else:
            msg="2次密码不匹配"
    else:
        email=request.GET.get('mail')
        randString=request.GET.get('randString')
        if email and randString:
            # sendEmailRandom = people.objects.get(email=email).values('sendEmailRandom')
            sendEmailRandom=people.objects.get(email=email)
            if sendEmailRandom:
                if randString==sendEmailRandom.sendEmailRandom:
                    msg="修改成功"
                    return render(request,"searchUpdatePassword.html",{"mail":email,"msg":msg})
                else:
                    return HttpResponse("你的地址有误...")
            else:
                return HttpResponse("你的地址有误,请到官方网站完成注册")

    return render(request, "searchUpdatePassword.html", {"mail": mail, "msg": msg})





def logout(request):
    loginObj=request.session.get('is_login',None)
    print (loginObj)
    if  loginObj!=None:
        del request.session['is_login']
        return redirect('/home/login/')
    else:
        return HttpResponse("用户未登陆")

def searchPassword(request):
    msg = ""
    if request.method=="POST":
        email=request.POST.get('mail',None)
        passwd1=request.POST.get('passwd1',None)
        passwd2 = request.POST.get('passwd2',None)
        print (passwd1,passwd2,email)
        if email and passwd1 and passwd1==passwd2:
            passwdMd5=getPasswdHash(passwd1.encode('utf-8'))
            peopleObj=people.objects.get(email=email)
            peopleObj.password = passwdMd5
            peopleObj.registerStatus = 1
            peopleObj.successCreateTime = getNow()
            peopleObj.save()

            msg="用户注册成功"
            return redirect('/home/login/')

        else:
            msg="2次密码不匹配"

    else:
        email=request.GET.get('mail',None)
        randString=request.GET.get('randString',None)
        if email and randString:
            sendEmailRandom=people.objects.filter(email=email).values('sendEmailRandom')
            if sendEmailRandom:
                sendEmailRandom=sendEmailRandom[0].get('sendEmailRandom')
                print (email,randString,sendEmailRandom)
                if sendEmailRandom and randString==sendEmailRandom:
                    return render(request,"searchPassword.html",{"mail":email})
                else:
                    return HttpResponse("你的地址有误...")
            else:
                return HttpResponse("你的地址有误,请到官方网站完成注册")

    return render(request, "searchPassword.html", {"mail": email,"msg":msg})

def userAuth(request):
    loginObj = request.session.get('is_login', None)
    if loginObj != None:
        msg=""
        email = loginObj['email']
        userObj = people.objects.get(email=email)
        if request.method=="POST":
            name=request.POST.get('name')
            sex = request.POST.get('sex')
            birthday = request.POST.get('birthday')
            idcardAdress = request.POST.get('idcardAdress')
            idcardnums = request.POST.get('idCard')

            idObj=idCard(
                name=name,
                sex=sex,
                dateBirth=birthday,
                address=idcardAdress,
                idnumber=idcardnums,
                people=userObj
            )
            idObj.save()
            msg="信息提交成功"
            userObj.authInformation=1
            userObj.save()

        return render(request, "userAuth.html",{"userobj":userObj,"msg":msg})
    else:
        return redirect('/home/login/')



def index(request):
    """
    如果登陆：对自己点赞的标记
    原网页显示

    :param request:
    :return:
    """
    userObj=""
    house=HouseAttr.objects.all()

    loginObj=request.session.get('is_login',None)
    if loginObj!=None:
        email=loginObj['email']
        userObj=people.objects.get(email=email)

        return render(request,'index.html',{"userobj":userObj,"houses":house})
    return render(request, 'index.html', {"userobj": userObj, "houses": house})
"""
判断当前用户是否收藏显示的房屋，
"""
def  myCollectionStatus(request):
    """

        2.取出当前用户收藏的所有房子
            if 存在
            ，，遍历传过来的每个房子，如果在这个列表，给1{status:"success",data:{“houseID”,"1"}}
            else：
            空{status:"false",data:{}}
    :param request:
    :return:
    """
    if request.method=="POST":
        idlist=request.POST.get('hID',None)
        # print (request.body)
        if idlist!=None:
            idlist=json.loads(idlist)
            print (idlist,type(idlist))
            email=request.session.get('is_login')['email']
            print (email)
            userobj=people.objects.get(email=email)
            print ((userobj.nichen))

            Collecs=CollectionHouse.objects.filter(peopleId=userobj)
            print(Collecs)
            data=[]
            for Collec in Collecs:
                print (Collec.houseId.id)
                if str(Collec.houseId.id) in idlist:
                    data.append(Collec.houseId.id)

            print (data)
            return HttpResponse(json.dumps({"houseIdList":data}))
        else:
            return HttpResponse(None)



def Collection(request):
    msg=""
    loginObj = request.session.get('is_login', None)
    if loginObj!=None:
        email=loginObj.get('email')
        userobj=people.objects.get(email=email)
        if request.method=="POST":
            houesid=request.POST.get('houes')
            print(houesid,type(houesid))
            userCollect=CollectionHouse.objects.filter(peopleId=userobj,houseId_id=houesid)


            houseobj = HouseAttr.objects.get(id=houesid)
            ##标记当前用户是否关注 0未关注
            status=0
            ##查看用户收藏夹，如果已经收藏，乃么取消，并在房间收藏列-1
            if userCollect:
                userCollect=userCollect[0]
                userCollect.delete()
                houseobj.Like_num=houseobj.Like_num-1
                houseobj.save()


            ##查看收藏夹，如果没收藏，乃么添加，并在房间收藏列加1
            else:

                collectHobj=CollectionHouse(
                    peopleId=userobj,
                    houseId=houseobj,
                )
                collectHobj.save()
                houseobj.Like_num=houseobj.Like_num+1
                houseobj.save()
                status = 1
            data={
                "num":houseobj.Like_num,
                "sign":status,
                }
            return HttpResponse(json.dumps(data))

    else:
        return redirect('/home/index/')

def myPublishHouse(request):
    """
            功能1  展示已经发布的房源
                2  对其中的内容修改
                3  对发布的房源信息删除
            :param request:
            :return:
            """

    loginObj=request.session.get('is_login',None)
    if loginObj!=None:
        email=loginObj.get('email')
        userobj=people.objects.get(email=email)

        houses=HouseAttr.objects.filter(people=userobj)

        return render(request,'myPublishHouse.html',{"userobj":userobj,"houses":houses})
    else:
        return render('/home/login/')

def myPublishHouseDelete(request):
    loginObj=request.session.get('is_login',None)
    if loginObj!=None:
        email=loginObj.get('email')
        userobj=people.objects.get(email=email)

        houseid=request.GET.get("houseid",None)
        houseobj=HouseAttr.objects.get(id=houseid)
        houseobj.delete()

        houses=HouseAttr.objects.filter(people=userobj)

        return render(request,'myPublishHouse.html',{"houses":houses})
    else:
        return render('/home/login/')

def myPublishHouseUpdate(request):
    loginObj = request.session.get('is_login', None)
    if loginObj!=None:
        email=loginObj.get('email')
        print (email)
        userobj=people.objects.get(email=email)
        print (userobj)


        houseid = request.GET.get("houseid", None)
        print (houseid)
        houseObj = HouseAttr.objects.get(id=houseid)

        if request.method=="POST":
            # houseobj=request.GET.get('houseid')
            ##公寓类型
            houseType = request.POST.get('houseType', None)
            print(houseType)

            ##住房类型
            zhufangType = request.POST.get('zhufangType', None)
            print(zhufangType)

            ##房客人数
            houseMaxPeople = request.POST.get('houseMaxPeople')
            print(houseMaxPeople)

            ##卧室数目
            woShiNum = request.POST.get('woShiNum')
            print(woShiNum)

            ##双人床的数目
            towBed = request.POST.get('towBed')
            print(towBed)

            ##单人床的数目
            oneBed = request.POST.get('oneBed')
            print(oneBed)

            ##浴室的数目
            showerNum = request.POST.get('showerNum')
            print(showerNum)

            ##房屋住址
            houseAddr = request.POST.get('houseAddr', None)
            print(houseAddr)

            ##房屋所在城市
            cityAddr = request.POST.get('cityAddr', None)
            print(cityAddr)

            ##提供的设备
            Sheprovided = request.POST.getlist('Sheprovided', None)
            Sheprovided = ';'.join(Sheprovided)
            print(Sheprovided)

            ##提供的额外区域
            userArea = request.POST.getlist('userArea', None)
            userArea = ';'.join(userArea)
            print(userArea)

            ##房屋详细描述
            houseDescript = request.POST.get("houseDescript", None)
            print(houseDescript)

            ##
            ##房屋特色描述
            houseFeatureDescript = request.POST.get("houseFeatureDescript", None)
            print(houseFeatureDescript)

            ##房客需要了解的信息
            knowInformation = request.POST.getlist('knowInformation', None)
            knowInformation = ';'.join(knowInformation)

            ##房客需要了解的信息补充信息
            otherknowInformation = request.POST.get('otherknowInformation', None)
            knowInformation = knowInformation + ";" + otherknowInformation
            print(knowInformation)

            ##房屋守则banrules
            banrules = request.POST.getlist("banrules", None)
            banrules = ";".join(banrules)

            ##房屋守则banrules 补充
            otherbanrules = request.POST.get('otherbanrules', None)
            banrules = banrules + ";" + otherbanrules
            # print(banrules)

            ##获取图片  cover
            coverPicture = request.FILES.get('coverPicture', None)
            keTingPicture = request.FILES.get('keTingPicture', None)
            zhuWoPicture = request.FILES.get('zhuWoPicture', None)
            ciWoPicture = request.FILES.get('ciWoPicture', None)
            chuFangPicture = request.FILES.get('chuFangPicture', None)
            showerPicture = request.FILES.get('showerPicture', None)
            otherPicture = request.FILES.get('otherPicture', None)
            paypictrue = request.FILES.get('paypictrue', None)

            # print (keTingPicture,zhuWoPicture,ciWoPicture,chuFangPicture,showerPicture,otherPicture)
            print("paypictrue:", paypictrue,type(paypictrue))
            ##价格
            price = request.POST.get('price', None)
            print(price)


            # print (houseObj)
            # print (houseObj.people.nichen)

            houseObj.houseType="公寓型住宅"
            houseObj.zhufangType = zhufangType
            houseObj.houseMaxPeople = houseMaxPeople
            houseObj.woShiNum = woShiNum
            houseObj.towBed = towBed
            houseObj.oneBed = oneBed
            houseObj.showerNum = showerNum
            houseObj.houseAddr = houseAddr
            houseObj.cityAddr = cityAddr
            houseObj.Sheprovided = Sheprovided
            houseObj.banrules = banrules
            houseObj.userArea = userArea
            houseObj.houseDescript = houseDescript
            houseObj.houseFeatureDescript = houseFeatureDescript
            houseObj.knowInformation = knowInformation
            houseObj.price = price
            houseObj.createTime = datetime.datetime.now()
            # houseObj.people=userobj
            houseObj.imgPath = coverPicture
            houseObj.erWeiPath=paypictrue
            houseObj.save()

            img1 = Img.objects.filter(houseId=houseObj, imgDescript="客厅美照")
            if img1:
                if keTingPicture!=None:
                    img1.imgPath=keTingPicture,
                    img1.save()
                else:
                    img1.delete()
            else:
                if keTingPicture!=None:
                    Imgobj1 = Img(
                        imgPath=keTingPicture,
                        imgDescript="客厅美照",
                        houseId=houseObj
                    )
                    Imgobj1.save()

            img2 = Img.objects.filter(houseId=houseObj, imgDescript="主卧美照")
            if img2:
                if zhuWoPicture != None:
                    img2.imgPath = zhuWoPicture,
                    img2.save()
                else:
                    img2.delete()
            else:
                if zhuWoPicture != None:
                    img2 = Img(
                        imgPath=zhuWoPicture,
                        imgDescript="客厅美照",
                        houseId=houseObj
                    )
                    img2.save()

            img3 = Img.objects.filter(houseId=houseObj, imgDescript="次卧美照")
            if img3:
                if ciWoPicture != None:
                    img3.imgPath = ciWoPicture,
                    img3.save()
                else:
                    img3.delete()
            else:
                if ciWoPicture != None:
                    img3 = Img(
                        imgPath=ciWoPicture,
                        imgDescript="次卧美照",
                        houseId=houseObj
                    )
                    img3.save()

            img4 = Img.objects.filter(houseId=houseObj, imgDescript="厨房美照")
            if img4:
                if chuFangPicture != None:
                    img4.imgPath = chuFangPicture,
                    img4.save()
                else:
                    img4.delete()
            else:
                if chuFangPicture != None:
                    img4 = Img(
                        imgPath=chuFangPicture,
                        imgDescript="厨房美照",
                        houseId=houseObj
                    )
                    img4.save()

            img5= Img.objects.filter(houseId=houseObj, imgDescript="浴室美照")
            if img5:
                if showerPicture != None:
                    img5.imgPath = showerPicture,
                    img5.save()
                else:
                    img5.delete()
            else:
                if showerPicture != None:
                    img5 = Img(
                        imgPath=showerPicture,
                        imgDescript="浴室美照",
                        houseId=houseObj
                    )
                    img5.save()

            img6 = Img.objects.filter(houseId=houseObj, imgDescript="其他美照")
            if img6:
                if otherPicture != None:
                    img6.imgPath = otherPicture,
                    img6.save()
                else:
                    img6.delete()
            else:
                if otherPicture != None:
                    img6 = Img(
                        imgPath=otherPicture,
                        imgDescript="其他美照",
                        houseId=houseObj
                    )
                    img6.save()


            msg="房屋信息更新成功"
            return render(request, 'publishHouseInfmat.html', {"userobj": houseObj,"msg":msg})


            # return render(request,)
        else:
             return render(request,'publishHouseUpate.html',{"userobj":houseObj,"house":houseObj})
    else:
        return render('/home/login/')

def localHouse(request):
    msg=""
    userobj = ""
    houses=""
    loginObj = request.session.get('is_login', None)
    if loginObj != None:
        email = loginObj.get('email')
        userobj = people.objects.get(email=email)
        if request.method=="POST":
            searchCity=request.POST.get('searchCity','西安')
            if searchCity=="":
                searchCity="西安"
            # print(searchCity)


            # print(searchCity)
        else:
            searchCity=request.GET.get('address')

        cityHouses = HouseAttr.objects.filter(cityAddr=searchCity)
        if cityHouses:
            houses = cityHouses
        else:
            msg = "未搜到"
    return render(request,'localHouse.html',{"msg":msg,"houses":houses,"userobj":userobj,"searchCity":searchCity})


def publishHouseInfmat(request):
    msg=""
    loginObj=request.session.get('is_login',None)
    if loginObj!=None:

        ##判读用户是否认证，认证可以操作，没认证不恩呢该操作


        email=loginObj.get('email')
        userObj=people.objects.get(email=email)
        print (userObj.authStatus)
        if userObj.authStatus==0:
            msg="您目前认证还未通过，不能发布房源信息，请您先去进行认证操作或耐心等待认证审查"
            return HttpResponse(msg)
            # return render(request, 'publishHouseInfmat.html', {"userobj": userObj, "msg": msg})
        else:
            if request.method=="POST":
                # print (request.body)
                ##公寓类型
                houseType=request.POST.get('houseType',None)
                print (houseType)

                ##住房类型
                zhufangType=request.POST.get('zhufangType',None)
                print(zhufangType)

                ##房客人数
                houseMaxPeople=request.POST.get('houseMaxPeople')
                print(houseMaxPeople)

                ##卧室数目
                woShiNum=request.POST.get('woShiNum')
                print(woShiNum)

                ##双人床的数目
                towBed=request.POST.get('towBed')
                print(towBed)

                ##单人床的数目
                oneBed=request.POST.get('oneBed')
                print(oneBed)

                ##浴室的数目
                showerNum=request.POST.get('showerNum')
                print(showerNum)

                ##房屋住址
                houseAddr=request.POST.get('houseAddr',None)
                print(houseAddr)

                ##房屋所在城市
                cityAddr=request.POST.get('cityAddr',None)
                print(cityAddr)

                ##提供的设备
                Sheprovided=request.POST.getlist('Sheprovided',None)
                Sheprovided=';'.join(Sheprovided)
                print(Sheprovided)

                ##提供的额外区域
                userArea = request.POST.getlist('userArea',None)
                userArea = ';'.join(userArea)
                print(userArea)

                ##房屋详细描述
                houseDescript=request.POST.get("houseDescript",None)
                print(houseDescript)

                ##
                ##房屋特色描述
                houseFeatureDescript = request.POST.get("houseFeatureDescript", None)
                print(houseFeatureDescript)


                ##房客需要了解的信息
                knowInformation = request.POST.getlist('knowInformation',None)
                knowInformation = ';'.join(knowInformation)


                ##房客需要了解的信息补充信息
                otherknowInformation=request.POST.get('otherknowInformation',None)
                knowInformation=knowInformation+";"+otherknowInformation
                print(knowInformation)


                ##房屋守则banrules
                banrules = request.POST.getlist("banrules",None)
                banrules=";".join(banrules)

                ##房屋守则banrules 补充
                otherbanrules=request.POST.get('otherbanrules',None)
                banrules=banrules+";"+otherbanrules
                print(banrules)

                ##获取图片  cover
                coverPicture = request.FILES.get('coverPicture', None)
                keTingPicture=request.FILES.get('keTingPicture',None)
                zhuWoPicture = request.FILES.get('zhuWoPicture', None)
                ciWoPicture = request.FILES.get('ciWoPicture', None)
                chuFangPicture=request.FILES.get('chuFangPicture',None)
                showerPicture = request.FILES.get('showerPicture', None)
                otherPicture = request.FILES.get('otherPicture', None)
                paypictrue = request.FILES.get('paypictrue', None)

                # print (keTingPicture,zhuWoPicture,ciWoPicture,chuFangPicture,showerPicture,otherPicture)

                ##价格
                price=request.POST.get('price',None)
                print(price)

                houseObj=HouseAttr(
                    houseType=houseType,
                    zhufangType=zhufangType,
                    houseMaxPeople=houseMaxPeople,
                    woShiNum=woShiNum,
                    towBed=towBed,
                    oneBed=oneBed,
                    showerNum=showerNum,
                    houseAddr=houseAddr,
                    cityAddr=cityAddr,
                    Sheprovided=Sheprovided,
                    banrules=banrules,
                    userArea=userArea,
                    houseDescript=houseDescript,
                    houseFeatureDescript=houseFeatureDescript,
                    knowInformation=knowInformation,
                    price=getInter(price),
                    createTime=datetime.datetime.now(),
                    people=userObj,
                    imgPath=coverPicture,
                    erWeiPath =paypictrue,
                )
                houseObj.save()

                if keTingPicture!=None:
                    Imgobj1=Img(
                        imgPath=keTingPicture,
                        imgDescript="客厅美照",
                        houseId=houseObj
                    )
                    Imgobj1.save()
                if zhuWoPicture!=None:
                    Imgobj2=Img(
                        imgPath=zhuWoPicture,
                        imgDescript="主卧美照",
                        houseId=houseObj
                    )
                    Imgobj2.save()
                if ciWoPicture!=None:
                    Imgobj3=Img(
                        imgPath=ciWoPicture,
                        imgDescript="次卧美照",
                        houseId=houseObj
                    )
                    Imgobj3.save()
                if chuFangPicture!=None:
                    Imgobj4=Img(
                        imgPath=chuFangPicture,
                        imgDescript="厨房美照",
                        houseId=houseObj
                    )
                    Imgobj4.save()
                if showerPicture!=None:
                    Imgobj5=Img(
                        imgPath=showerPicture,
                        imgDescript="浴室美照",
                        houseId=houseObj
                    )
                    Imgobj5.save()
                if otherPicture!=None:
                    Imgobj6=Img(
                        imgPath=otherPicture,
                        imgDescript="其他美照",
                        houseId=houseObj
                    )
                    Imgobj6.save()
                msg="房屋发布成功"
                return render(request, 'publishHouseInfmat.html', {"userobj": userObj,"msg":msg})


        return render(request,'publishHouseInfmat.html',{"userobj":userObj})
    else:
        return redirect('/home/login/')

def useInformationUpdate(request):

    user = ""
    msg=""
    userDict = request.session.get('is_login', None)
    print (userDict)
    if userDict != None:
        email = userDict.get('email')
        userObj = people.objects.get(email=email)
        if request.method == "POST":
            nichen=request.POST.get('nichen')
            userObj.nichen=nichen
            userObj.save()
            # userObj = people.objects.get(email=email)
            msg="修改完成"
            return render(request, 'useInformationUpdate.html', {"userobj": userObj,"msg":msg})
        else:
            idObj=idCard.objects.filter(people=userObj)
            if idObj:
                idObj=idObj[0]
            else:
                idObj=""
            # print (idObj.dateBirth,type(idObj.dateBirth))
            return render(request, 'useInformationUpdate.html', {"userobj": userObj,"idCard":idObj})
    else:
        return redirect("/home/login/")



def likeCollection(request):
    msg=""
    collectobj=""
    loginobj=request.session.get('is_login',None)
    if loginobj!=None:
        email=loginobj.get('email')
        userobj=people.objects.get(email=email)
        collectObj=CollectionHouse.objects.filter(peopleId=userobj)
        if collectObj:
            ##收藏过，展示
            collectobj=collectObj
        else:
            #没有收藏，给与说明
            msg="收藏记录为空"
        return render(request,"likeCollection.html",{"msg":msg,"userobj":userobj,"collectobjs":collectobj})
    else:
        return redirect('/home/login/')

def houseDetailShow(request):

    houseid=request.GET.get('houseid')
    loginObj=request.session.get('is_login',None)
    if loginObj!=None:

        email=loginObj.get('email')
        userobj=people.objects.get(email=email)

    else:
        userobj=None
    houseobj=HouseAttr.objects.get(id=houseid)

    ##提供的设施
    Sheprovided=houseobj.Sheprovided.split(';')



    ##取其中的4个图片
    pictureobj=Img.objects.filter(houseId=houseobj)[0:3]

    ##房屋守则
    banrules=houseobj.banrules.split(';')

    ##房客须知
    knowInformation=houseobj.knowInformation.split(';')

    ##提示
    userArea=houseobj.userArea.split(';')

    comments=houseCommentInfor.objects.filter(house=houseobj)

    # print (userobj.nichen)
    data={
        "userobj": userobj,
        "houseobj": houseobj,
        "pictureobjs": pictureobj,
        "Sheprovideds": Sheprovided,
        "banrules":banrules,
        "knowInformations":knowInformation,
        "userAreas":userArea,
        "comments":comments,
    }
    return render(request,'houseDetailShow.html',data)
    # return render(request,'houseDetailShow.html',{})

def bookSubmit(request):
    """
    people=models.ForeignKey(people)
    house=models.ForeignKey(HouseAttr)
    startDate=models.DateTimeField()
    endDate=models.DateTimeField()
    createTime=models.DateTimeField()
    allprice=models.FloatField(default=0)

    :param request:
    :return:
    """
    msg=""
    loginobj = request.session.get('is_login', None)
    if loginobj != None:
        if request.method=="POST":
            email = loginobj.get('email')
            userobj = people.objects.get(email=email)

            houseid=request.GET.get('houseid')
            house=HouseAttr.objects.get(id=houseid)

            ###预定房间与12306类似，预定后别人就不能预定
            alreadyBookHouseid=HouseBook.objects.filter(house_id=houseid)
            if alreadyBookHouseid:
                msg="房间已经被预定"
                return HttpResponse(msg)
            else:
                startDate = request.POST.get('startData')
                startDate=datetime.datetime.strptime(startDate,"%Y-%m-%d")
                endData = request.POST.get('endData')
                endData = datetime.datetime.strptime(endData, "%Y-%m-%d")
                eachPrice=request.POST.get('eachPrice')
                print (eachPrice)
                datenumInt=(endData-startDate).days

                bookobj=HouseBook(
                    people=userobj,
                    house=house,
                    startDate=startDate,
                    endDate=endData,
                    createTime=datetime.datetime.now(),
                    oneprice=int(eachPrice),
                    allprice=int(eachPrice)*datenumInt,
                )
                bookobj.save()

                ###预定成功给房东发个邮件
                #房东的邮箱
                houseEmail=house.people.email
                ##内容
                emailText="用户%s 已经预定了你的房间 --%s. 用户的 email是 %s"%(userobj.nichen,house.houseFeatureDescript,userobj.email)
                sendEmail(houseEmail,emailText)

                ##给用户发邮件提示尽快的支付
                userEmailText="你已经成功预定房间%s，请尽快完成支付"%(house.houseFeatureDescript)
                sendEmail(email, userEmailText)
                return redirect('/home/myBookHourse/')


            # msg="房间预定成功！"
            # return render(request,'houseDetailShow.html',{"userobj":userobj,"msg":msg})
            # return HttpResponse()
            # datenumStr=datetime.datetime.strftime(datenum,"%d days, 0:00:00")

            # print(startDate,endData,type(endData),datenumStr)


    else:
        return redirect('/home/login/')

def myBookHourse(request):
    loginobj = request.session.get('is_login', None)
    if loginobj != None:
        houseBobj=""
        email = loginobj.get('email')
        userobj = people.objects.get(email=email)

        houseBobj=HouseBook.objects.filter(people=userobj)


        return render(request,'myBookHourse.html',{"userobj":userobj,"houseBobjs":houseBobj})


    else:
        return redirect('/home/login/')

def myBookHourseDelete(request):
    loginobj = request.session.get('is_login', None)
    if loginobj != None:


        houseBobj = ""
        email = loginobj.get('email')
        userobj = people.objects.get(email=email)
        houseBookId=request.GET.get('houseBookId')
        houseBookObj=HouseBook.objects.get(id=houseBookId)
        houseBookObj.delete()

        houseBobj = HouseBook.objects.filter(people=userobj)

        return render(request, 'myBookHourse.html', {"userobj": userobj, "houseBobjs": houseBobj})


    else:
        return redirect('/home/login/')


def myPublishHouseStatus(request):
    loginobj = request.session.get('is_login', None)
    if loginobj != None:

        houseBobj = ""
        """
        "houseBookId": houseBookId,
					"status":status,
        """
        email = loginobj.get('email')
        userobj = people.objects.get(email=email)

        houseobj=request.POST.get('houseBookId')
        status = request.POST.get('status')
        print (houseobj,status)


        HouseBookobj=HouseBook.objects.filter(house_id=houseobj)
        if HouseBookobj:
            HouseBookobj=HouseBookobj[0]
            print(status)
            if status=="true":
                print (1)
                HouseBookobj.status=1
            else:
                print(0)
                HouseBookobj.status = 0

            HouseBookobj.save()
            print (HouseBookobj.status)

            return HttpResponse(True)
        else:
            return HttpResponse("操作错误，房间未被预定")

        # houseBobj = HouseBook.objects.filter(people=userobj)
        #
        # return render(request, 'myBookHourse.html', {"userobj": userobj, "houseBobjs": houseBobj})


    else:
        return redirect('/home/login/')

def setPushHousePayStatus(request):
    loginobj = request.session.get('is_login', None)
    if loginobj != None:

        houseBobj = ""
        """
        "houseBookId": houseBookId,
                    "status":status,
        """
        email = loginobj.get('email')
        userobj = people.objects.get(email=email)

        houseID = request.POST.get('houseBookId')
        print(houseID)

        HouseBookobj = HouseBook.objects.filter(house_id=houseID)
        if HouseBookobj:

            if HouseBookobj[0].status==1:
                print(houseID,"ok")
                return HttpResponse(json.dumps({"status":True}))
            else:
                print(houseID, "not")
                return HttpResponse(json.dumps({"status":False}))


    else:
        return redirect('/home/login/')

def myPayHourse(request):
    msg = ""
    loginobj = request.session.get('is_login', None)
    if loginobj != None:
        email = loginobj.get('email')
        userobj = people.objects.get(email=email)
        HouseBookobj = HouseBook.objects.filter(people=userobj,status=1)
        # print (HouseBookobj[0].oneprice)
        return render(request, 'myPayHourse.html', {"userobj": userobj, "HouseBookobjs": HouseBookobj})


    else:
        return redirect('/home/login/')


def myPayHourseComment(request):
    msg=""
    loginobj = request.session.get('is_login', None)
    if loginobj != None:
        email = loginobj.get('email')
        userobj= people.objects.get(email=email)

        houseBookId = request.GET.get('houseBookId')
        print (houseBookId)
        if request.method=="POST":
            houseBookId=request.POST.get('houseBookId')
            houseObj=HouseAttr.objects.get(id=houseBookId)

            comment=request.POST.get('comtent')

            """
             house=models.ForeignKey(HouseAttr)
            people=models.ForeignKey(people)
            content=models.TextField()
            """
            houseCommetObj=houseCommentInfor(
                people=userobj,
                content=comment,
                house=houseObj,
            )
            houseCommetObj.save()
            msg="发表评论成功"

        return render(request,'myPayHourseComment.html',{"houseBookId":houseBookId,"msg":msg})

        # houseBookObj = HouseBook.objects.get(id=houseBookId)
        #
        # houseBookObj.delete()
        #
        # houseBobj = HouseBook.objects.filter(people=userobj)
        #
        # return render(request, 'myBookHourse.html', {"userobj": userobj, "houseBobjs": houseBobj})


    else:
        return redirect('/home/login/')

def loginAfter(request):
    loginobj = request.session.get('is_login', None)
    if loginobj != None:
        email = loginobj.get('email')
        userobj = people.objects.get(email=email)
        return render(request,'loginAfter.html',{"userobj": userobj})
    else:
        return redirect('/home/login/')

def housePaypicture(request):
    loginobj = request.session.get('is_login', None)
    if loginobj != None:
        email = loginobj.get('email')
        userobj = people.objects.get(email=email)
        houseBookId=request.GET.get('houseBookId')
        print (houseBookId)
        houseObj=HouseAttr.objects.get(id=houseBookId)
        return render(request, 'housePaypicture.html', {"userobj": userobj,"houseObj":houseObj})
    else:
        return redirect('/home/login/')

def sendEmailHousePeopel(request):
    msg=""
    loginobj = request.session.get('is_login', None)
    if loginobj != None:
        email = loginobj.get('email')
        userobj = people.objects.get(email=email)
        houseId=request.GET.get('houseId')

        if request.method=="POST":
            houseId = request.POST.get('houseId')
            print (houseId)
            houseObj = HouseAttr.objects.get(id=houseId)

            comment = request.POST.get('comtent')

            comment="<p>昵称：%s</p><p>email: %s</p>\n\n<p>内容:%s</p>"%(userobj.nichen,userobj.email,comment)

            sendResult=sendEmail(houseObj.people.email,comment)
            if sendResult:
                msg="发送成功"
            else:
                msg="发送失败"
            return render(request, 'sendEmailHousePeopel.html', {"userobj": userobj,"msg":msg})


        else:
            return render(request, 'sendEmailHousePeopel.html', {"userobj": userobj,"houseId":houseId})
    else:
        return redirect('/home/login/')