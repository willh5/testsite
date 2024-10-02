from django.db import models
import datetime
from django.utils import timezone





class Source(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', ]



class Currency(models.Model):
    # making CAD the base currency here.
    name = models.CharField(max_length=100)
    # base_currency=models.CharField(max_length=100)
    conversion_rate = models.DecimalField(
        max_digits=10, decimal_places=6, blank=True, null=True)
    last_update = models.DateTimeField(default=None, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', ]


class Unit(models.Model):
    name = models.CharField(max_length=100)
    default_unit = models.ForeignKey(
        'Unit', on_delete=models.SET_NULL, null=True, blank=True, default=None)
    coeff = models.DecimalField(
        max_digits=10, decimal_places=6, default=1, blank=True, null=True)
    const = models.DecimalField(
        max_digits=10, decimal_places=6, default=0, blank=True, null=True)

    def get_default_value(self, value):
        return float(self.coeff) * value + self.const

    def val_from_default(self, default_value):
        return float(1 / self.coeff) * (default_value - self.const)

    def convert(self, value, unit):
        default = self.get_default_value(value)
        return unit.val_from_default(default)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', ]


class Metric(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    units = models.ManyToManyField('Unit')

    class Meta:
        ordering = ['name', ]
        constraints = [models.UniqueConstraint(
            fields=['name', ], name='unique-metric')]

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(
        max_length=100, default=None, null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, default=None, blank=True, null=True,
                               related_name='children')
    code = models.CharField(max_length=10, default=None, null=True, blank=True)
    currency = models.ForeignKey(
        'Currency', on_delete=models.SET_NULL, default=None, null=True, blank=True)

    LOC_CHOICES = [
        ('COUNTRY', 'country'),
        ('REGION', 'region'),
        ('MULTI', 'multi'),
        ('OTHER', 'other'),
        ('EXCEPT', 'except'),
    ]

    loctype = models.CharField(
        max_length=20, choices=LOC_CHOICES, default="COUNTRY", blank=True)
    components = models.ManyToManyField('Location', default=None, blank=True)

    class Meta:
        ordering = ['name', ]
        constraints = [models.UniqueConstraint(
            fields=['name', ], name='unique-location')]

    def __str__(self):
        return self.name


class Firm(models.Model):
    name = models.CharField(max_length=100)

    hq_location = models.ForeignKey('Location', on_delete=models.SET_NULL, default=None, blank=True, null=True,
                                    related_name='firm_loc')
    account_number = models.IntegerField(default=None, blank=True, null=True)
    sector = models.ForeignKey('Sector', on_delete=models.SET_NULL, default=None, blank=True, null=True)
    subsector = models.ForeignKey('SubSector', on_delete=models.SET_NULL, default=None, blank=True, null=True)
    industry = models.ForeignKey('Industry', on_delete=models.SET_NULL, default=None, blank=True, null=True)
    subindustry = models.ForeignKey('SubIndustry', on_delete=models.SET_NULL, default=None, blank=True, null=True)
    currency = models.ForeignKey('Currency', on_delete=models.SET_NULL, default=None, blank=True, null=True)
    hasScope1 = models.BooleanField(default=False)
    hasScope2 = models.BooleanField(default=False)
    hasScope3 = models.BooleanField(default=False)
    hasTargets = models.BooleanField(default=False)

    cdp_industry = models.ForeignKey('CDPIndustry', on_delete=models.SET_NULL, default=None, blank=True, null=True,
                                     related_name='firms')
    cdp_sector = models.ForeignKey('CDPSector', on_delete=models.SET_NULL, default=None, blank=True, null=True,
                                   related_name='firms')
    cdp_activity = models.ForeignKey('CDPActivity', on_delete=models.SET_NULL, default=None, blank=True, null=True,
                                     related_name='firms')
    
    site = models.CharField(max_length=500, default=None, blank=True, null=True,
                                    )


    def __str__(self):
        return self.name


    class Meta:
        ordering = ['name', ]
        constraints = [models.UniqueConstraint(
            fields=['name', ], name='unique-firm')]

    @property
    def isin(self):
        return self.isins.all()[-1]


class ISIN(models.Model):
    name = models.CharField(max_length=100)
    # firm = models.ForeignKey('Firm', on_delete=models.CASCADE, default=None, blank=True, null=True, related_name='isins')
    firm = models.ForeignKey(
        'Firm', on_delete=models.CASCADE, related_name='isins')
    last_used = models.DateTimeField(blank=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['last_used', ]
        constraints = [models.UniqueConstraint(
            fields=['name', ], name='unique-isin')]
    # @property
    # def default(self):
    #     total=0


class Ticker(models.Model):
    name = models.CharField(max_length=100)
    firm = models.ForeignKey('Firm', on_delete=models.SET_NULL, default=None, blank=True, null=True,
                             related_name='tickers')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', ]
        constraints = [models.UniqueConstraint(
            fields=['name', 'firm'], name='unique-ticker')]


class Sector(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class SubSector(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'Sector', on_delete=models.SET_NULL, null=True, related_name='children')


    def __str__(self):
        return self.name

class Industry(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'SubSector', on_delete=models.SET_NULL, null=True, related_name='children')

    def __str__(self):
        return self.name

class SubIndustry(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'Industry', on_delete=models.SET_NULL, null=True, related_name='children')

    def __str__(self):
        return self.name
    


class CDPIndustry(models.Model):
    name = models.CharField(max_length=100)


class CDPSector(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'CDPIndustry', on_delete=models.SET_NULL, null=True, related_name='children')


class CDPActivity(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'CDPSector', on_delete=models.SET_NULL, null=True, related_name='children')
    

class Quant(models.Model):
    date = models.DateTimeField()

    location_based = models.BooleanField(default='False', blank=True)
    location = models.ForeignKey(
        'Location', on_delete=models.CASCADE, default=None, null=True, related_name='data2')

    firm = models.ForeignKey(
        'Firm', on_delete=models.CASCADE, default=None, related_name='firm_quant')

    native_currency = models.BooleanField(default=False, null=True, blank=True)

    currency = models.ForeignKey(
        'Currency', on_delete=models.SET_NULL, default=None, null=True, blank=True)

    unit = models.ForeignKey(
        'Unit', on_delete=models.SET_NULL, default=None, null=True, blank=True)

    # sector=models.ForeignKey('Sector', on_delete=models.CASCADE, default=None, related_name='data2')
# # should prob add default set to false
    last_available = models.BooleanField(null=True, blank=True)

    metric = models.ForeignKey(
        'Metric', on_delete=models.CASCADE, default=None)
    source = models.ForeignKey(
        'Source', on_delete=models.SET_NULL, default=None, null=True, blank=True)

    TIMESCALE_CHOICES = [
        ('annual', 'annual'),
        ('quarterly', 'quarterly'),
        ('monthly', 'monthly'),
        ('weekly', 'weekly'),
        ('daily', 'daily'),
        ('irregular', 'irregular'),

    ]

    timescale = models.CharField(
        max_length=20, choices=TIMESCALE_CHOICES, default="annual", blank=True)
    forecast = models.BooleanField(default=False)
    most_recent = models.BooleanField(default=False, blank=True)
    publication_date = models.DateTimeField(
        default=None, null=True, blank=True)

    class Meta:

        # sets indexes on commonly filtered fields - probably should add more
        indexes = [
            models.Index(fields=['location', ]),
            models.Index(fields=['metric', ]),
            models.Index(fields=['date', ]),

        ]

        # groups by location, then metric, then date
        ordering = ('date',)
        constraints = [
            # add unit and more
            models.UniqueConstraint(
                fields=['unit', 'location_based', 'metric', 'location', 'timescale', 'date', 'source',
                        'publication_date', 'firm'], name='unique-data-num')
        ]

    value = models.DecimalField(max_digits=50, decimal_places=2, null=True)

    DATATYPE_CHOICES = [
        ('PERCENT', '%'),
        ('RATIO', ':'),
        ('TOTAL', 'total'),
        ('BINARY', 'binary')
    ]
    datatype = models.CharField(
        max_length=10, choices=DATATYPE_CHOICES, default='TOTAL')

    def __str__(self):
        return str(self.value)


class Qual(models.Model):
    date = models.DateTimeField()

    location = models.ForeignKey(
        'Location', on_delete=models.CASCADE, default=None, null=True, related_name='data1')
    firm = models.ForeignKey(
        'Firm', on_delete=models.CASCADE, default=None, related_name='data1')
    metric = models.ForeignKey(
        'Metric', on_delete=models.CASCADE, default=None)
    source = models.ForeignKey(
        'Source', on_delete=models.SET_NULL, default=None, null=True, blank=True)

    TIMESCALE_CHOICES = [
        ('annual', 'annual'),
        ('quarterly', 'quarterly'),
        ('monthly', 'monthly'),
        ('weekly', 'weekly'),
        ('daily', 'daily'),
        ('irregular', 'irregular'),

    ]

    timescale = models.CharField(
        max_length=20, choices=TIMESCALE_CHOICES, default="annual", blank=True)
    forecast = models.BooleanField(default=False)
    publication_date = models.DateTimeField(
        default=None, null=True, blank=True)

    class Meta:
        # sets indexes on commonly filtered fields - probably should add more
        indexes = [
            models.Index(fields=['location', ]),
            models.Index(fields=['metric', ]),
            models.Index(fields=['date', ]),

        ]

        # groups by location, then metric, then date
        ordering = ('location', 'metric', 'date',)
        constraints = [
            # add unit and more
            models.UniqueConstraint(fields=['metric', 'location', 'timescale', 'date', 'source', 'publication_date'],
                                    name='unique-data')
        ]

    value = models.CharField(max_length=2500, null=True)


# class Portfolio(models.Model):
#     name = models.CharField(max_length=250, default=None, blank=True)
#     user = models.ForeignKey(NewUser,
#                              on_delete=models.CASCADE)
#     creation_date = models.DateTimeField(auto_now_add=True, blank=True)
#     firms = models.ManyToManyField('Firm', through='Holding')


# class Holding(models.Model):
#     upload_date = models.DateTimeField(default=datetime.date.today, blank=True)
#     value = models.DecimalField(max_digits=50, decimal_places=2)
#     currency = models.ForeignKey(
#         'Currency', on_delete=models.SET_NULL, default=None, null=True, blank=True)
#     firm = models.ForeignKey('Firm', on_delete=models.CASCADE)
#     portfolio = models.ForeignKey('Portfolio', on_delete=models.CASCADE)

#     class Meta:
#         db_table = "api_portfolio_firms"


# new models

class Scope1(models.Model):
    date = models.DateTimeField()
    location_based = models.BooleanField(default='False')
    location = models.ForeignKey(
        'Location', on_delete=models.CASCADE, default=None, null=True, related_name='scope1')

    firm = models.ForeignKey(
        'Firm', on_delete=models.CASCADE, default=None, related_name='scope1')

    metric = models.ForeignKey(
        'Metric', on_delete=models.CASCADE, default=None)
    source = models.ForeignKey(
        'Source', on_delete=models.SET_NULL, default=None, null=True, blank=True)

    TIMESCALE_CHOICES = [
        ('annual', 'annual'),
        ('quarterly', 'quarterly'),
        ('monthly', 'monthly'),
        ('weekly', 'weekly'),
        ('daily', 'daily'),
        ('irregular', 'irregular'),

    ]

    interpolation = models.BooleanField(default=False, blank=True)
    amendment = models.BooleanField(default=False, blank=True)

    timescale = models.CharField(
        max_length=20, choices=TIMESCALE_CHOICES, default="annual", blank=True)
    forecast = models.BooleanField(default=False)
    most_recent = models.BooleanField(default=False, blank=True)
    publication_date = models.DateTimeField(
        default=None, null=True, blank=True)
    last_available = models.BooleanField(blank=True, default=False)

    class Meta:
        # sets indexes on commonly filtered fields - probably should add more
        indexes = [
            models.Index(fields=['location', ]),
            models.Index(fields=['metric', ]),
            models.Index(fields=['date', ]),

        ]

        # groups by location, then metric, then date
        ordering = ('date',)
        constraints = [
            # add unit and more
            models.UniqueConstraint(
                fields=['unit', 'location_based', 'metric', 'location', 'timescale', 'date', 'source',
                        'publication_date', 'firm'], name='unique-scope1')
        ]

    value = models.DecimalField(max_digits=50, decimal_places=2, null=True)
    unit = models.ForeignKey(
        'Unit', on_delete=models.SET_NULL, default=None, null=True, blank=True)
    DATATYPE_CHOICES = [
        ('PERCENT', '%'),
        ('RATIO', ':'),
        ('TOTAL', 'total'),
        ('BINARY', 'binary')
    ]
    datatype = models.CharField(
        max_length=10, choices=DATATYPE_CHOICES, default='TOTAL')

    def __str__(self):
        return str(self.value)


class Scope2(models.Model):
    date = models.DateTimeField()
    location_based = models.BooleanField(default='False')
    location = models.ForeignKey(
        'Location', on_delete=models.CASCADE, default=None, null=True, related_name='scope2')
    firm = models.ForeignKey(
        'Firm', on_delete=models.CASCADE, default=None, related_name='scope2')

    metric = models.ForeignKey(
        'Metric', on_delete=models.CASCADE, default=None)
    source = models.ForeignKey(
        'Source', on_delete=models.SET_NULL, default=None, null=True, blank=True)

    TIMESCALE_CHOICES = [
        ('annual', 'annual'),
        ('quarterly', 'quarterly'),
        ('monthly', 'monthly'),
        ('weekly', 'weekly'),
        ('daily', 'daily'),
        ('irregular', 'irregular'),

    ]

    interpolation = models.BooleanField(default=False, blank=True)
    amendment = models.BooleanField(default=False, blank=True)

    timescale = models.CharField(
        max_length=20, choices=TIMESCALE_CHOICES, default="annual", blank=True)
    forecast = models.BooleanField(default=False)
    most_recent = models.BooleanField(default=False, blank=True)
    publication_date = models.DateTimeField(
        default=None, null=True, blank=True)
    last_available = models.BooleanField(blank=True, default=False)

    SCHEME_CHOICES = [
        ('LOC', 'loc'),
        ('MKT', 'mkt'),
        ('NONE', 'none'),
    ]

    scheme = models.CharField(
        max_length=10, choices=SCHEME_CHOICES, default='NONE')

    class Meta:
        # sets indexes on commonly filtered fields - probably should add more
        indexes = [
            models.Index(fields=['location', ]),
            models.Index(fields=['metric', ]),
            models.Index(fields=['date', ]),

        ]

        # groups by location, then metric, then date
        ordering = ('date',)
        constraints = [
            # add unit and more
            models.UniqueConstraint(
                fields=['unit', 'location_based', 'metric', 'location', 'timescale', 'date', 'source',
                        'publication_date', 'firm', 'scheme'], name='unique-scope2')
        ]

    value = models.DecimalField(max_digits=50, decimal_places=2, null=True)
    unit = models.ForeignKey(
        'Unit', on_delete=models.SET_NULL, default=None, null=True, blank=True)
    DATATYPE_CHOICES = [
        ('PERCENT', '%'),
        ('RATIO', ':'),
        ('TOTAL', 'total'),
        ('BINARY', 'binary')
    ]
    datatype = models.CharField(
        max_length=10, choices=DATATYPE_CHOICES, default='TOTAL')

    def __str__(self):
        return str(self.value)


class Scope3(models.Model):
    date = models.DateTimeField()

    location_based = models.BooleanField(default='False')
    location = models.ForeignKey(
        'Location', on_delete=models.CASCADE, default=None, null=True, related_name='scope3')

    firm = models.ForeignKey(
        'Firm', on_delete=models.CASCADE, default=None, related_name='scope3')

    # sector=models.ForeignKey('Sector', on_delete=models.CASCADE, default=None, related_name='data2')

    metric = models.ForeignKey(
        'Metric', on_delete=models.CASCADE, default=None)
    source = models.ForeignKey(
        'Source', on_delete=models.SET_NULL, default=None, null=True, blank=True)

    TIMESCALE_CHOICES = [
        ('annual', 'annual'),
        ('quarterly', 'quarterly'),
        ('monthly', 'monthly'),
        ('weekly', 'weekly'),
        ('daily', 'daily'),
        ('irregular', 'irregular'),

    ]

    interpolation = models.BooleanField(default=False, blank=True)
    amendment = models.BooleanField(default=False, blank=True)

    timescale = models.CharField(
        max_length=20, choices=TIMESCALE_CHOICES, default="annual", blank=True)

    forecast = models.BooleanField(default=False)
    most_recent = models.BooleanField(default=False, blank=True)
    publication_date = models.DateTimeField(
        default=None, null=True, blank=True)
    last_available = models.BooleanField(blank=True, default=False)

    # specialized scope 3 attributes
    scope_source = models.CharField(max_length=100, null=True, blank=True)
    calculation_method = models.CharField(
        max_length=300, null=True, blank=True)
    most_common_scope_source = models.BooleanField(default=False, blank=True)
    scope_source_cleaned = models.CharField(
        max_length=100, null=True, blank=True)

    # in full the below is equal to : "Percentage of emissions calculated using data obtained from suppliers or value chain partners"
    scp3_pcnt_from_other_sources = models.DecimalField(
        max_digits=10, decimal_places=2, null=True)
    scp3_most_common_source = models.BooleanField(default=False, blank=True)

    value = models.DecimalField(max_digits=50, decimal_places=2, null=True)
    unit = models.ForeignKey(
        'Unit', on_delete=models.SET_NULL, default=None, null=True, blank=True)
    DATATYPE_CHOICES = [
        ('PERCENT', '%'),
        ('RATIO', ':'),
        ('TOTAL', 'total'),
        ('BINARY', 'binary')
    ]
    datatype = models.CharField(
        max_length=10, choices=DATATYPE_CHOICES, default='TOTAL')

    class Meta:
        # sets indexes on commonly filtered fields - probably should add more
        indexes = [
            models.Index(fields=['location', ]),
            models.Index(fields=['metric', ]),
            models.Index(fields=['date', ]),

        ]

        # groups by location, then metric, then date
        ordering = ('date',)
        constraints = [
            # add unit and more
            models.UniqueConstraint(
                fields=['unit', 'location_based', 'metric', 'location', 'timescale', 'date', 'source',
                        'publication_date', 'firm'], name='unique-scope3')
        ]

    def __str__(self):
        return str(self.value)


class Target(models.Model):

    # # NEW: to deal with the fact that accenture reference numbers are wrong.
    # covered_base = models.DecimalField(max_digits=50, decimal_places=2)

    reference_number = models.IntegerField(default='1')
    firm = models.ForeignKey(
        'Firm', on_delete=models.CASCADE, related_name='targets')
    date_set = models.DateTimeField()

    STATUS_CHOICES = [
        ('Achieved', 'achieved'),
        ('Expired', 'expired'),
        ('New', 'new'),
        ('Replaced', 'replaced'),
        ('Retired', 'retired'),
        ('Revised', 'revised'),
        ('Underway', 'underway'),
        ('NONE', 'NONE'),

    ]

    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, blank=True, default='NONE')

    SCOPE_CHOICES = [
        ('1', 'scope 1'),
        ('2', 'scope 2'),
        ('3', 'scope 3'),
        ('1+2', 'scope 1 and scope 2'),
        ('1+3', 'scope 1 and scope 3'),
        ('2+3', 'scope 2 and scope 3'),
        ('1+2+3', 'all scopes'),
        ('NONE', 'NONE'),
    ]

    scope = models.CharField(
        max_length=10, choices=SCOPE_CHOICES, default='NONE')
    SCHEME_CHOICES = [
        ('LOC', 'loc'),
        ('MKT', 'mkt'),
        ('LOC+MKT', 'loc + mkt'),
        ('NONE', 'none'),
    ]

    # scope 2 specific
    scope2_scheme = models.CharField(
        max_length=10, choices=SCHEME_CHOICES, blank=True, default='NONE')

    # scope 3 specific
    scope3_source = models.CharField(
        max_length=100, blank=True, default='NONE')

    class Meta:
        ordering = ('date_set',)

        constraints = [
            models.UniqueConstraint(
                fields=['reference_number', 'firm'], name='unique-target')
        ]


class TargetData(models.Model):
    publication_date = models.DateTimeField()
    target = models.ForeignKey(
        'Target', on_delete=models.CASCADE, related_name='data')

    base_year = models.IntegerField()
    target_year = models.IntegerField()

    covered_base = models.DecimalField(max_digits=50, decimal_places=2)
    targeted_reduction = models.DecimalField(max_digits=10, decimal_places=2)
    covered_target = models.DecimalField(max_digits=50, decimal_places=2)
    covered_pubyear = models.DecimalField(max_digits=50, decimal_places=2)

# new
    percent_of_total = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)

    description = models.TextField(blank=True, default='')

    STATUS_CHOICES = [
        ('Achieved', 'achieved'),
        ('Expired', 'expired'),
        ('New', 'new'),
        ('Replaced', 'replaced'),
        ('Retired', 'retired'),
        ('Revised', 'revised'),
        ('Underway', 'underway'),
        ('NONE', 'NONE'),

    ]
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, blank=True, default='NONE')

    class Meta:

        indexes = [
            models.Index(fields=['publication_date', ]),
        ]

        ordering = ('-publication_date',)
        # constraints = [
        #     models.UniqueConstraint(fields=['target','publication_date', ], name='unique-target-update')
        # ]


class Intensity(models.Model):

    NUMERATOR_CHOICES = [
        ('hq1', 'scope 1 hq based'),
        ('hq2', 'scope 2 hq based'),
        ('hq3', 'scope 3 hq based'),
        ('hq12', 'scope 1 and scope 2 hq based'),
        ('hq13', 'scope 1 and scope 3 hq based'),
        ('hq23', 'scope 2 and scope 3 hq based'),
        ('hq123', 'all scopes hq based'),
        ('loc1', 'scope 1 location based'),
        ('loc2', 'scope 2 location based'),
        ('loc3', 'scope 3 location based'),
        ('loc12', 'scope 1 and scope 2 location based'),
        ('loc13', 'scope 1 and scope 3 location based'),
        ('loc23', 'scope 2 and scope 3 location based'),
        ('loc123', 'all scopes location based'),
    ]

    numerator = models.CharField(max_length=100, choices=NUMERATOR_CHOICES)

    DENOMINATOR_CHOICES = [
        ('currentrevenue', 'current revenue'),
        ('historicalrevenue', 'historical revenue'),
        ('historicalemployees', 'historical number of employees'),
        ('currentemployees', 'current number of employees'),

    ]

    last_available = models.BooleanField(blank=True, default=False)

    denominator = models.CharField(max_length=100, choices=DENOMINATOR_CHOICES)

    date = models.DateTimeField()
    location_based = models.BooleanField(default='False')
    location = models.ForeignKey(
        'Location', on_delete=models.CASCADE, default=None, null=True, related_name='data3')

    firm = models.ForeignKey(
        'Firm', on_delete=models.CASCADE, default=None, related_name='data3')

    source = models.ForeignKey(
        'Source', on_delete=models.SET_NULL, default=None, null=True, blank=True)

    TIMESCALE_CHOICES = [
        ('annual', 'annual'),
        ('quarterly', 'quarterly'),
        ('monthly', 'monthly'),
        ('weekly', 'weekly'),
        ('daily', 'daily'),
        ('irregular', 'irregular'),

    ]

    timescale = models.CharField(
        max_length=20, choices=TIMESCALE_CHOICES, default="annual", blank=True)
    forecast = models.BooleanField(default=False)
    publication_date = models.DateTimeField(
        default=None, null=True, blank=True)

    class Meta:

        ordering = ('date',)

        constraints = [
            models.UniqueConstraint(
                fields=['date', 'numerator', 'denominator', 'firm'], name='unique-intensity')
        ]

    value = models.DecimalField(max_digits=50, decimal_places=2, null=True)

    def __str__(self):
        return str(self.value)
