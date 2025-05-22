{
    'name': 'Guatemala FEL Invoice',
    'version': '18.0.1.0.0',
    'summary': 'Integrates Odoo with Guatemala FEL CS electronic invoicing service.',
    'author': 'CSISTEMAS - Carlos Cordova',
    'website': 'https://csistemas.com',
    'category': 'Localization',
    'license': 'LGPL-3',
    'depends': ['account','l10n_gt'],
    'data': [
        'data/webservices_data.xml',
        'security/ir.model.access.csv',
        'views/company_views.xml',
        'views/account_journal_views.xml',
        
        # Add your data files here, e.g. 'views/fel_cs_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}