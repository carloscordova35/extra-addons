from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class ResCompany(models.Model):
    _inherit = 'res.company'

    fel_user = fields.Char(string="Usuario")
    fel_apikey = fields.Char(string="Clave API")
    fel_pfxkey = fields.Char(string="Clave PFX")
    fel_gface = fields.Selection([('infile','Infile'),('megaprint','Megaprint')],string="GFace")
    fel_entorno = fields.Selection([('pruebas','Pruebas'),('produccion','Produccion')])
    fel_establishment_ids = fields.One2many('res.company.establishment','company_id',string="Establecimientos")

class ResCompanyEstablishment(models.Model):
    _name = 'res.company.establishment'
    _description = 'Establecimiento'


    fel_comercial = fields.Char(string = "Nombre comercial")
    fel_numero = fields.Integer(string = "Numero establecimiento")
    fel_direccion = fields.Char(string="Direccion")
    fel_ciudad = fields.Char(string="Ciudad")
    company_id = fields.Many2one('res.company',string = "Compañia")
