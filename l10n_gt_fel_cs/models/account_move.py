import logging

from odoo import models, api,fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _post(self,soft=True):
        posted = super()._post(soft=soft)
        for move in posted:
            if(move.move_type =='out_invoice'):
                _logger.info(" >>> Posted Invoice Edit %s is from Guatemala", move.name) 
        return posted    

    fel_fecha_emi = fields.Datetime(string="Fecha emision", readonly=True)
    fel_status = fields.Integer(string="Estado Certificacion", readonly=True)
    #fel_tipo = fields.Char(string="Tipo Documento",related="journal_id.fel_tipo",readonly=True)


    #def action_post(self):
    #    res = super(AccountMove, self).action_post()
    #    if self.move_type == 'out_invoice' and self.state=='posted':
    #        for move in self:
    #           # if move.partner_id.country_id.code == 'GT':
    #            _logger.info(" >>> Invoice %s is from Guatemala", move.name) 
    #    return res