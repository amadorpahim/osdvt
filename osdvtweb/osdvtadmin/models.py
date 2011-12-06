from django.db import models

# Create your models here.
from django.db import models
from django.contrib import admin

# Create your models here.

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

class Spice(models.Model):
        SpicePort = models.CharField(max_length=5)
        Token = models.CharField(max_length=20, blank=True, null=True, editable=False)
        SpiceSsl = models.CharField(max_length=1, blank=True, null=True, editable=False)
        SpiceSslPort = models.CharField(max_length=5, blank=True, null=True, editable=False)
        CertFile = models.CharField(max_length=200, blank=True, null=True, editable=False)
        KeyFile = models.CharField(max_length=200, blank=True, null=True, editable=False)
        CAFile = models.CharField(max_length=200, blank=True, null=True, editable=False)
        def __unicode__(self):
                #return u'%s (%s)' % (self.SpicePort, self.SpiceSslPort)
                return u'%s' % (self.SpicePort)

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

class OsType(models.Model):
	OsType = models.CharField(max_length=200)
        def __unicode__(self):
                return u'%s' % (self.OsType)

class OsVariant(models.Model):
	OsType = models.ForeignKey(OsType, blank=True, null=False)
	OsVariant = models.CharField(max_length=200)
        def __unicode__(self):
                return u'%s %s' % (self.OsType, self.OsVariant)

class ArchBits(models.Model):
	ArchBits = models.CharField(max_length=200)
        def __unicode__(self):
                return u'%s' % (self.ArchBits)


class Vm(models.Model):
        Name = models.CharField(max_length=200)
        Description = models.CharField(max_length=200)
        Smp = models.CharField(max_length=2)
        Memory = models.CharField(max_length=4)
	Disk = models.ManyToManyField(Disk, through='VmDisk')
        Immutable = models.BooleanField(default=0)
        MAC = models.CharField(max_length=17, unique=True)
        Bridge = models.ForeignKey(Bridge, default=1, null=False)
        SpiceEnabled = models.BooleanField(default=1)
        SpicePort = models.ForeignKey(Spice, unique=True, blank=True, null=True)
        Users = models.ManyToManyField(User, blank=True, null=True)
        Ips = models.ManyToManyField(Ip, blank=True, null=True)
	OsVariant = models.ForeignKey(OsVariant, blank=True, null=True)
	ArchBits = models.ForeignKey(ArchBits, blank=True, null=True)

class VmDisk(models.Model):
	Disk = models.ForeignKey(Disk)
	Vm = models.ForeignKey(Vm)
	Virtio = models.BooleanField(default=0)
	Cdrom = models.BooleanField(default=0)  
	Boot = models.BooleanField(default=0)
        def __unicode__(self):
                return u'%s (%s)' % (self.Vm, self.Disk)

#ADMIN STUFF
class VmDiskInline(admin.TabularInline):
	model = VmDisk
	extra = 0

class VmAdmin(admin.ModelAdmin):
       	list_display	= ('Name', 'Description', 'OsVariant', 'ArchBits', 'Smp', 'Memory', 'MAC', 'SpicePort')
        list_filter	= ['Smp', 'Memory', 'OsVariant', 'Users', 'Ips']
        ordering	= ['Name', 'Description']
        search_fields	= ['Name', 'Description', 'MAC', 'Memory', 'Users__Name', 'Users__Description', 'OsVariant__OsType__OsType', 'OsVariant__OsVariant']
    	inlines		= [ VmDiskInline, ]


admin.site.register(User)
admin.site.register(Ip)
admin.site.register(Spice)
admin.site.register(Disk)
admin.site.register(Bridge)
admin.site.register(Vm, VmAdmin)
admin.site.register(VmDisk)
admin.site.register(OsType)
admin.site.register(OsVariant)
admin.site.register(ArchBits)
