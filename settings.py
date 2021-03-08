from os import environ

SESSION_CONFIGS = [
    dict(
       name='corr',
       display_name="corr",
       num_demo_participants=1,
       app_sequence=['corr']
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = 't(zn5aln)w5)u+wj5wcqdj=0)z6lv%6#k1mg-r!&3kuec6vlb&'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']