from odoo import _,api,fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    tipos = [
        ('FACT','Factura'),
        ('FCAM','Factura Cambiaria'),
    ]

    fel_tipo =  fields.Selection(tipos,string="Tipo FEL")
    fel_establecimiento = fields.Many2one('res.company.establishment',string="Establecimiento")