import logging

from odoo import models, api,fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.move_type == 'out_invoice' and self.state=='posted':
            for move in self:
                if move.partner_id.country_id.code == 'GT':
                   _logger.info("Invoice %s is from Guatemala", move.name) 
        return res