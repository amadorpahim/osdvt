from django.db import models
from django.contrib import admin

VIDEO_CHOICES	= ((0, 'SPICE'), (1, 'VNC'))
OS_CHOICES	= ((0, 'Linux'), (1, 'Windows'))
BITS_CHOICES	= ((0, '32'), (1, '64'))

class User(models.Model):
        Name = models.CharField(max_length=200)
        Description = models.CharField(max_length=200)
        Token = models.CharField(max_length=20, blank=True, null=True, editable=False)
        def __unicode__(self):
                return u'%s (%s)' % (self.Name, self.Description)

class Ip(models.Model):
        IP = models.CharField(max_length=15)
        Description = models.CharField(max_length=200)
        Token = models.CharField(max_length=20, blank=True, null=True, editable=False)
        def __unicode__(self):
                return u'%s (%s)' % (self.IP, self.Description)

class Disk(models.Model):
        Path = models.CharField(max_length=200)
        Description = models.CharField(max_length=200)
	Size = models.CharField(max_length=4, null=True)
        def __unicode__(self):
                return u'%s (%s)' % (self.Path, self.Description)

class Bridge(models.Model):
        Name = models.CharField(max_length=20)
        Description = models.CharField(max_length=200)
        def __unicode__(self):
                return u'%s (%s)' % (self.Name, self.Description)

class OsVariant(models.Model):
	OsType = models.BooleanField(choices=OS_CHOICES,default=0)
	OsVariant = models.CharField(max_length=200)
        def __unicode__(self):
                return u'%s %s' % (self.OsType, self.OsVariant)

class Vm(models.Model):
        Name = models.CharField(max_length=200)
        Description = models.CharField(max_length=200)
        Core = models.CharField(max_length=2)
        Socket = models.CharField(max_length=2)
        Memory = models.CharField(max_length=4)
	Disk = models.ManyToManyField(Disk, through='VmDisk')
        Immutable = models.BooleanField(default=0)
	UsbRedirect = models.BooleanField(default=0)
        MAC = models.CharField(max_length=17, unique=True)
        Bridge = models.ForeignKey(Bridge, default=1, null=False)
	Video = models.BooleanField(choices=VIDEO_CHOICES,default=0)
        Users = models.ManyToManyField(User, blank=True, null=True)
        Ips = models.ManyToManyField(Ip, blank=True, null=True)
	OsVariant = models.ForeignKey(OsVariant, blank=True, null=True)
	Bits = models.BooleanField(choices=BITS_CHOICES,default=0)

class VmDisk(models.Model):
	Disk = models.ForeignKey(Disk)
	Vm = models.ForeignKey(Vm)
	Virtio = models.BooleanField(default=0)
	Cdrom = models.BooleanField(default=0)  
	Boot = models.BooleanField(default=0)
        def __unicode__(self):
                return u'%s (%s)' % (self.Vm, self.Disk)

class VideoPorts(models.Model):
        Port = models.CharField(max_length=5)
        Available = models.BooleanField(default=1)
	Vm = models.ForeignKey(Vm, blank=True, null=True)
        def __unicode__(self):
                return u'%s (%s)' % (self.Name, self.Description)

#ADMIN STUFF
class VmDiskInline(admin.TabularInline):
	model = VmDisk
	extra = 0

class VmAdmin(admin.ModelAdmin):
       	list_display	= ('Name', 'Description', 'OsVariant', 'Core', 'Socket', 'Memory', 'MAC')
        list_filter	= ['Core', 'Socket', 'Memory', 'OsVariant', 'Users', 'Ips']
        ordering	= ['Name', 'Description']
        search_fields	= ['Name', 'Description', 'MAC', 'Memory', 'Users__Name', 'Users__Description', 'OsVariant__OsType', 'OsVariant__OsVariant']
    	inlines		= [ VmDiskInline, ]

admin.site.register(User)
admin.site.register(Ip)
admin.site.register(VideoPorts)
admin.site.register(Disk)
admin.site.register(Bridge)
admin.site.register(Vm, VmAdmin)
admin.site.register(VmDisk)
admin.site.register(OsVariant)
