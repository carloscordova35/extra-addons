from odoo import _,api,fields,models
from odoo.exceptions import ValidationError

class ResCompany(models.Model):
    _ihherit = 'res.company'

    fel_user = fields.Char(string="Usuario")
    fel_apikey = fields.Char(string="Clave API")
    fel_pfxkey = fields.Char(String="Clave PFX")
    fel_gface = fields.Selection([('infile','Infile'),('megaprint','Megaprint')],string="GFace")
    fel_entorno = fields.Selection([('pruebas','Pruebas'),('produccion','Produccion')])
    fel_establishment_ids = fields.One2many('res.company.establishment','company_id',string="Establecimientos")
