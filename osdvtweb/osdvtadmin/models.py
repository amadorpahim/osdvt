from django.db import models
from django.contrib import admin

VIDEO_CHOICES	= (('0', 'SPICE'), ('1', 'VNC'))
OS_CHOICES	= (('Linux', 'Linux'), ('Windows', 'Windows'))
BITS_CHOICES	= (('32', '32'), ('64', '64'))
USB_CHOICES	= (('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'))

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
	OsType = models.CharField(max_length=20,choices=OS_CHOICES)
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
	UsbRedirect = models.CharField(max_length=1,choices=USB_CHOICES,default=0)
        MAC = models.CharField(max_length=17, unique=True, blank=True, null=True)
        Bridge = models.ForeignKey(Bridge, default=1, null=False)
	Video = models.CharField(max_length=2,choices=VIDEO_CHOICES)
        Users = models.ManyToManyField(User, blank=True, null=True)
        Ips = models.ManyToManyField(Ip, blank=True, null=True)
	OsVariant = models.ForeignKey(OsVariant, blank=True, null=True)
	Bits = models.CharField(max_length=2,choices=BITS_CHOICES)
        VideoPort = models.CharField(max_length=5, blank=True, null=True, editable=False)
        VideoToken = models.CharField(max_length=20, blank=True, null=True, editable=False)
        StartedVideo = models.CharField(max_length=1, blank=True, null=True, editable=False)
        def __unicode__(self):
                return u'%s' % (self.Name)

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
       	list_display	= ('Name', 'Description', 'OsVariant', 'Core', 'Socket', 'Memory', 'Video','MAC')
        list_filter	= ['Core', 'Socket', 'Memory', 'OsVariant', 'Video', 'Users', 'Ips']
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
