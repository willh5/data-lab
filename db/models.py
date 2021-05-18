from django.db import models
from django.db.models import F



class Source(models.Model):
    name = models.CharField(max_length=100)
    url=models.CharField(max_length=200, blank=True, null=True)
    description=models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name


class Unit(models.Model):
    name = models.CharField(max_length=100)
    default_unit=models.ForeignKey('Unit', on_delete=models.SET_NULL, null=True, blank=True, default=None)
    coeff=models.DecimalField(max_digits=10, decimal_places=6, default=1, blank=True, null=True )
    const = models.DecimalField(max_digits=10, decimal_places=6, default=0, blank=True, null=True)

    def get_default_value(self,value):
        return float(self.coeff)*value+self.const

    def val_from_default(self, default_value):
        return float(1/self.coeff)*(default_value-self.const)

    def convert(self, value, unit):
        default=self.get_default_value(value)
        return unit.val_from_default(default)

    def __str__(self):
        return self.name

class Metric(models.Model):
    name = models.CharField(max_length=100)
    description =models.CharField(max_length=200, blank=True)
    units=models.ManyToManyField('Unit')
    parent=models.ForeignKey('Metric', on_delete=models.SET_NULL, default=None, blank=True, null=True)

    def __str__(self):
        return self.name

class Location(models.Model):
    name=models.CharField(max_length=40)
    parent=models.ForeignKey('self', on_delete=models.SET_NULL, default=None, blank=True, null=True)
    def __str__(self):
        return self.name


class Data(models.Model):
    value=models.DecimalField(max_digits=50, decimal_places=2)

    DATATYPE_CHOICES=[
        ('PERCENT','%'),
        ('RATIO', ':'),
        ('TOTAL', 'total')
    ]

    datatype=models.CharField(max_length=10,choices=DATATYPE_CHOICES, default='TOTAL')

    start=models.DateTimeField()
    end = models.DateTimeField()
    timescale=models.CharField(max_length=20, default="annual", blank=True)

    unit=models.ForeignKey('Unit', on_delete=models.SET_NULL, default=None, null=True, blank=True)
    source = models.ForeignKey('Source', on_delete=models.SET_NULL, default=None, null=True, blank=True)
    #many-to-one relationships with Location, Metric, Source
    #if any of the associated objects are deleted, Data object is deleted

    location=models.ForeignKey('Location', on_delete=models.CASCADE, default=None)
    metric=models.ForeignKey('Metric', on_delete=models.CASCADE, default=None)

    forecast = models.BooleanField(default=False)
    publication_date=models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        #sets indexes on commonly filtered fields - probably should add more
        indexes = [
            models.Index(fields=['location', ]),
            models.Index(fields=['metric', ]),
            models.Index(fields=['start', ]),

        ]


        #groups by location
        ordering = ('location', 'metric', 'start',)
        constraints = [
            models.UniqueConstraint(fields=[ 'metric', 'location', 'timescale', 'start', 'source' ,'publication_date'], name='unique-datapoint')
        ]



    def per_capita(self):
        return float(self.value)/float(Data.objects.get(location=self.location, source=self.source, timescale=self.timescale, start=self.start, metric="Population").value)

    def first_difference(self):
        year=int(self.start.year)
        return float(self.value) - float(Data.objects.get(location=self.location, source=self.source, metric=self.metric, start__year=str(year-1)).value)

    @property
    def total(self):
        if(self.datatype != "TOTAL"):
            try:
                return float(Data.objects.get(location=self.location, source=self.source, timescale=self.timescale, start=self.start, metric = self.metric.parent).value)*self.value
            except:
                return

    def growth_rate(self):
        year = int(self.start.year)
        return float(self.value)/float(Data.objects.get(location=self.location, source=self.source, metric=self.metric, start__year=str(year - 1)).value)



    def __str__(self):
        return str(self.value)

    def get_field(self):
        return [(field.name, field.value_to_string(self)) for field in Data._meta.fields]