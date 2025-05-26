from . import models


'''from odoo import api, SUPERUSER_ID

def _post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for product in env['product.template'].search([]):
        env.cr.execute("SELECT to_jsonb(list_price::numeric) as list_price from product_template where id = {}".format(product.id))
        list_price = env.cr.fetchall()[0][0]
        for company in env['res.company'].search([]):
            product.with_company(company.id).list_price = list_price'''