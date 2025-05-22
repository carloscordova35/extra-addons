from odoo import fields,models,api

class CompanyEstablishment(models.Model):
    _name = 'res.company.establishment'
    _description = 'Establecimiento'


    fel_comercial = fields.Char(string = "Nombre comercial")
    fel_numero = fields.Integer(string = "Numero establecimiento")
    fel_direccion = fields.Char(string="Direccion")
    fel_ciudad = fields.Char(string="Ciudad")
    company_id = fields.Many2one('res.company',string = "Compañia")


