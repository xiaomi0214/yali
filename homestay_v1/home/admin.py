from django.contrib import admin

# Register your models here.
from .models import people,idCard,HouseAttr,Img


"""
class Img(models.Model):
    imgPath=models.ImageField(upload_to='img')
    imgDescript=models.CharField(max_length=30)


    houseId=models.ForeignKey(HouseAttr)
"""
class ImgAdmin(admin.TabularInline):
    model = Img

class HouseAttrAdmin(admin.ModelAdmin):
    list_display = ['houseFeatureDescript','cityAddr','price']
    search_fields = ('cityAddr',)
    inlines = [ImgAdmin,]


admin.site.register(HouseAttr,HouseAttrAdmin)

class idCardLine(admin.TabularInline):
    model = idCard

class PeopleAdmin(admin.ModelAdmin):
    list_display = ['nichen','email','registerStatus',"authInformation",'authStatus','successCreateTime',]
    search_fields = ('nichen',)
    inlines = [idCardLine,]


admin.site.register(people,PeopleAdmin)

