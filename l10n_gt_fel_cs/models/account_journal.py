from odoo import _,api,fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    tipos = [
        ('FACT','Factura'),
        ('FCAM','Factura Cambiaria'),
    ]

    fel_tipo =  fields.Selection(tipos,string="Tipo FEL")
    fel_establecimiento = fields.Many2one('res.company.establishment',string="Establecimiento")


class AccountJournalPhrases(models.Model):
    _name = 'res.company.phrases'
    _description = 'Frases y Escenarios Fel'

    fel_frase = fields.Integer(string="Frase")
    fel_escenario = fields.Integer(string="Escenario")
    fel_detalle = fields.Char(string="Detalle de la frase y escenario a incluir")    