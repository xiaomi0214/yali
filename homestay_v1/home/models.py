#coding=utf-8
from django.db import models

# Create your models here.
import datetime
class people(models.Model):
    nichen=models.CharField(max_length=40,unique=True)
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=40)
    registerStatus=models.IntegerField(default=0)
    authStatus=models.IntegerField(default=0)
    authInformation = models.IntegerField(default=0)
    sendEmailRandom=models.CharField(max_length=60,default="")
    successCreateTime=models.DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table="people"

class idCard(models.Model):
    name=models.CharField(max_length=30)
    sex=models.CharField(max_length=10)
    dateBirth=models.CharField(max_length=30)
    address=models.CharField(max_length=50)
    idnumber=models.CharField(max_length=30)
    people=models.OneToOneField(people)

    class Meta:
        db_table="idCard"

class HouseAttr(models.Model):
    houseType=models.CharField(max_length=50)
    zhufangType=models.CharField(max_length=50)
    houseMaxPeople=models.IntegerField()
    woShiNum=models.IntegerField()
    towBed=models.IntegerField()
    oneBed=models.IntegerField()
    showerNum=models.IntegerField()
    houseAddr=models.CharField(max_length=150)
    cityAddr=models.CharField(max_length=50)
    Sheprovided=models.TextField()
    banrules=models.TextField()
    userArea=models.CharField(max_length=50)
    houseDescript=models.TextField()
    houseFeatureDescript=models.CharField(max_length=70)
    knowInformation=models.TextField()
    price=models.IntegerField(default=0)
    createTime=models.DateTimeField()
    Like_num=models.IntegerField(default=0)

    people=models.ForeignKey(people)

    imgPath = models.ImageField(upload_to='cover')
    erWeiPath = models.ImageField(upload_to='erWei')

    class Meta:
        db_table="houseAttr"


class Img(models.Model):
    imgPath=models.ImageField(upload_to='img')
    imgDescript=models.CharField(max_length=30)


    houseId=models.ForeignKey(HouseAttr)
    class Meta:
        db_table="houseImg"

class CollectionHouse(models.Model):
    peopleId=models.ForeignKey(people)
    houseId=models.ForeignKey(HouseAttr)

    class Meta:
        db_table="collectionHouse"

##预定

class HouseBook(models.Model):
    """
     userobj houseObj  startDate    endDate  创建日期 allprice
    """
    people=models.ForeignKey(people)
    house=models.ForeignKey(HouseAttr)
    startDate=models.DateTimeField()
    endDate=models.DateTimeField()
    createTime=models.DateTimeField()
    allprice=models.FloatField(default=0)
    oneprice=models.FloatField(default=0)


    status=models.IntegerField(default=0) ##0默认是未出租  1代表出租

    class Meta:
        db_table="houseBook"


class houseCommentInfor(models.Model):
    house=models.ForeignKey(HouseAttr)
    people=models.ForeignKey(people)
    content=models.TextField()

    class Meta:
        db_table="houseComment"