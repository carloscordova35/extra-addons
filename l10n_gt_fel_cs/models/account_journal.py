from odoo import _,api,fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    tipos = [
        ('FACT','Factura'),
        ('FCAM','Factura Cambiaria'),
        ('FPEQ','Factura Pequeño Contribuyente'),

    ]
    fel_certifica = fields.Boolean(string="Certifica FEL")
    fel_tipo =  fields.Selection(tipos,string="Tipo FEL")
    fel_exportacion = fields.Boolean(string="Es de exportacion?")
    fel_establecimiento_ids = fields.Many2one('res.company.establishment',string="Establecimiento")
    fel_frases_ids = fields.One2many('account.journal.phrases',"journal_id",string="Frases")


class AccountJournalPhrases(models.Model):
    _name = 'account.journal.phrases'
    _description = 'Frases y Escenarios Fel'

    fel_frase = fields.Integer(string="Frase")
    fel_escenario = fields.Integer(string="Escenario")
    fel_detalle = fields.Char(string="Detalle de la frase y escenario a incluir")
    journal_id = fields.Many2one('account.journal',string = "Diario")    