import logging
import pytz

from xml.etree import ElementTree as ET
from io import BytesIO
from odoo import models, api,fields
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta

from controller.infile import infile

_infile = infile.infile()


_logger = logging.getLogger(__name__)

tipos = [
        ('FACT','Factura'),
        ('FCAM','Factura Cambiaria'),
        ('FPEQ','Factura Pequeño Contribuyente'),

    ]

class AccountMove(models.Model):
    _inherit = 'account.move'

    fel_fecha_emi = fields.Datetime(string="Fecha emision", readonly=True)
    fel_status = fields.Selection([('0', 'Sin enviar'), ('1', 'Enviado'), ('2', 'Con Error'), ('3', 'Certificado'), ('4', 'Anulado')], copy=False, default='0')
    fel_tipo = fields.Selection(tipos, string="Tipo Documento",related="journal_id.fel_tipo",readonly=True)

    fel_uuid = fields.Char(string="Numero de autorizacion",readonly=True)
    fel_serie = fields.Char(string="Serie",readonly=True)
    fel_numero = fields.Char(string="Numero",readonly=True)
    fel_fecha_cert = fields.Datetime(string="Fecha certificacion",readonly=True)
    fel_fecha_anu =fields.Datetime(string="Fecha anulacion",readonly=True)

    fel_xml_error = fields.Text(string="XML Error",readonly=True)


    #inicia el proceso de envio al confirmar la factura
    def _post(self,soft=True):
        posted = super()._post(soft=soft)
        for move in posted:
            if(move.journal_id.fel_certifica and move.move_type in ('out_invoice','in_invoice')):
                if not move.fel_fecha_emi:
                    move.fel_fecha_emi = move.create_date
                _logger.info(" >>> Posted Invoice Certificat %s is from Guatemala (%s)" % (move.name,move.fel_fecha_emi)) 
                self.sudo().write({'fel_status': '1'})
                self._createxml()

                _infile._testapi()

        return posted    

   

    def _createxml(self):
        
        f = BytesIO()

        root = ET.Element('dte:GTDocumento', {
            'xmlns:ds': "http://www.w3.org/2000/09/xmldsig#",
            'xmlns:dte': "http://www.sat.gob.gt/dte/fel/0.2.0",
            'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
            'Version': "0.1"
        })
        
        SAT = ET.SubElement(root, 'dte:SAT', {'ClaseDocumento': "dte"})
        DTE = ET.SubElement(SAT, 'dte:DTE', {'ID': "DatosCertificados"})

        DatosEmision = ET.SubElement(DTE, 'dte:DatosEmision', {'ID': "DatosEmision"})
        DatosGenerales = {
            'CodigoMoneda': self.currency_id.name,
            'FechaHoraEmision':(self.fel_fecha_emi-timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M:%S-06:00"), #(self.fel_fecha_emi-timedelta(hours=6)).isoformat(timespec='seconds')+'-06:00',
            'Tipo': self.fel_tipo
        }

        ET.SubElement(DatosEmision, 'dte:DatosGenerales', DatosGenerales)
        Emisor = ET.SubElement(DatosEmision, 'dte:Emisor', {
            'AfiliacionIVA': "GEN",
            'CodigoEstablecimiento': str(self.journal_id.fel_establecimiento_ids.fel_numero) or '1',
            'CorreoEmisor': self.company_id.email or '',
            'NITEmisor': self.company_id.vat or '',
            'NombreComercial': self.journal_id.fel_establecimiento_ids.fel_comercial or '',
            'NombreEmisor': self.company_id.name or ''
        })

        DireccionEmisor = ET.SubElement(Emisor, 'dte:DireccionEmisor')

        ET.SubElement(DireccionEmisor, 'dte:Direccion').text = self.journal_id.fel_establecimiento_ids.fel_direccion or ''           
        ET.SubElement(DireccionEmisor, 'dte:CodigoPostal').text = self.journal_id.fel_establecimiento_ids.fel_posta or ''
        ET.SubElement(DireccionEmisor, 'dte:Municipio').text = self.journal_id.fel_establecimiento_ids.fel_ciudad or ''
        ET.SubElement(DireccionEmisor, 'dte:Departamento').text = self.journal_id.fel_establecimiento_ids.fel_depto or ''
        ET.SubElement(DireccionEmisor, 'dte:Pais').text = 'GT'

        DatosReceptor = {'CorreoReceptor': self.partner_id.email or '',
                       'IDReceptor': self.partner_id.vat,
                       'NombreReceptor': self.partner_id.name
                       }

        if self.fel_tipo in ['FESP', 'FACT', 'FCAM', 'NCRE', 'NABN'] and len(self.partner_id.vat) == 13:
            DatosReceptor['TipoEspecial'] = 'CUI'
        elif self.fel_tipo in ['FAEX']:
            DatosReceptor['TipoEspecial'] = 'EXT'

        Receptor = ET.SubElement(DatosEmision, 'dte:Receptor', DatosReceptor)
        DireccionReceptor = ET.SubElement(Receptor, 'dte:DireccionReceptor')

        ET.SubElement(DireccionReceptor, 'dte:Direccion').text = self.partner_id.street or ''
        ET.SubElement(DireccionReceptor, 'dte:CodigoPostal').text = self.partner_id.zip or ''
        ET.SubElement(DireccionReceptor, 'dte:Municipio').text = self.partner_id.city or ''
        ET.SubElement(DireccionReceptor, 'dte:Departamento').text = self.partner_id.state_id.name or ''
        ET.SubElement(DireccionReceptor, 'dte:Pais').text = self.partner_id.country_id.code or ''

        if self.fel_tipo in ('FACT', 'FCAM', 'NCRE'):

            Frases = ET.SubElement(DatosEmision, 'dte:Frases')

            for frase in self.journal_id.fel_frases_ids:
                ET.SubElement(Frases, 'dte:Frase', {'TipoFrase': str(frase.fel_frase),'CodigoEscenario': str(frase.fel_escenario)})

        Items = ET.SubElement(DatosEmision, 'dte:Items')
        
        #variables para total de descuento
        factotal = 0
        facdesc = 0
        porcdesc= 0  

        #Para buscar descuentos    
        for line in self.invoice_line_ids:
            if line.product_id:                
                if (line.price_unit < 0):
                    facdesc-=line.price_total
                else:
                    factotal+=line.price_total
        if(facdesc!=0):
            porcdesc = (facdesc/factotal)*100       

        count = 1
        for line in self.invoice_line_ids:
            if line.product_id and line.price_unit>0:

                preciot=0

                preciot = line.price_total * ((100-porcdesc)/100)

                Item = ET.SubElement(Items, 'dte:Item',{'BienOServicio': 'B' if line.product_id.type in ('consu', 'product') else 'S',
                                      'NumeroLinea': str(count)})
                ET.SubElement(Item, 'dte:Cantidad').text = str(round(line.quantity, 4))
                ET.SubElement(Item, 'dte:UnidadMedida').text = line.product_uom_id.name.upper()[
                                                               0:3] if line.product_uom_id else 'UND'
                if line.product_id.barcode:                    
                    ET.SubElement(Item, 'dte:Descripcion').text = line.product_id.barcode + '|' + line.name
                elif line.product_id.default_code:
                    ET.SubElement(Item, 'dte:Descripcion').text = line.product_id.default_code + '|' + line.name
                else:    
                    ET.SubElement(Item, 'dte:Descripcion').text = line.name

                ET.SubElement(Item, 'dte:PrecioUnitario').text = str(round(line.price_unit, 6))
                ET.SubElement(Item, 'dte:Precio').text = str(round(line.price_unit * line.quantity, 6))
                
                discountl = 0.0

                if line.discount!=0:
                    discountl = round((line.quantity * line.price_unit) * (line.discount / 100),2)
                    ET.SubElement(Item, 'dte:Descuento').text = str(discountl) if line.discount != 0 else "0.00"
                elif (porcdesc!=0):
                    discountl = round((line.quantity * line.price_unit) * (porcdesc / 100),2)  
                    ET.SubElement(Item, 'dte:Descuento').text = str(discountl) if porcdesc!= 0 else "0.00"
                else:
                    ET.SubElement(Item, 'dte:Descuento').text = str(discountl) if line.discount != 0 else "0.00"

                if self.fel_tipo != 'NABN':
                    Impuestos = ET.SubElement(Item, 'dte:Impuestos')
                    if line.tax_ids:
                        for tax in line.tax_ids:
                            Impuesto = ET.SubElement(Impuestos, 'dte:Impuesto')
                            ET.SubElement(Impuesto, 'dte:NombreCorto').text = tax.description
                            ET.SubElement(Impuesto,
                                          'dte:CodigoUnidadGravable').text = "2" if self.fel_tipo == 'FAEX' else "1"        
                            if self.fel_tipo != 'FAEX':                   
                                ET.SubElement(Impuesto, 'dte:MontoGravable').text = str(round((line.quantity * line.price_unit - discountl) - ((line.quantity * line.price_unit - discountl) / 1.12 * 0.12), 5))
                                ET.SubElement(Impuesto, 'dte:MontoImpuesto').text = str(
                                round(preciot / 1.12 * 0.12, 5))
                            else:
                                ET.SubElement(Impuesto, 'dte:MontoGravable').text = str(round((line.quantity * line.price_unit  - discountl) - ((line.quantity * line.price_unit - discountl) / 1 * 0), 5))
                                ET.SubElement(Impuesto, 'dte:MontoImpuesto').text = str(
                                round(preciot / 1 * 0, 5))
                    else:
                        Impuesto = ET.SubElement(Impuestos, 'dte:Impuesto')
                        ET.SubElement(Impuesto, 'dte:NombreCorto').text = 'IVA'
                        ET.SubElement(Impuesto,
                                      'dte:CodigoUnidadGravable').text = "2" if self.fel_tipo == 'FAEX' else "1"
                        if self.fel_tipo != 'FAEX':
                            ET.SubElement(Impuesto, 'dte:MontoGravable').text = str(round((line.quantity * line.price_unit -discountl) - ((line.quantity * line.price_unit - discountl) / 1.12 * 0.12), 5))
                            ET.SubElement(Impuesto, 'dte:MontoImpuesto').text = str(
                            round(preciot / 1.12 * 0.12, 5))
                        else:
                            ET.SubElement(Impuesto, 'dte:MontoGravable').text = str(round((line.quantity * line.price_unit - discountl) - ((line.quantity * line.price_unit - discountl) / 1 * 0), 5))
                            ET.SubElement(Impuesto, 'dte:MontoImpuesto').text = str(
                            round(preciot / 1 * 0, 5)) 

                ET.SubElement(Item, 'dte:Total').text = str(round(preciot, 3))
                count += 1 

        Totales = ET.SubElement(DatosEmision, 'dte:Totales')
        ET.SubElement(Totales, 'dte:GranTotal').text = str(round(self.amount_total, 3))

        #Agregar adendas

        Adenda = ET.SubElement(SAT, 'dte:Adenda')
        ET.SubElement(Adenda,'Refencia').text = self.name

        
        
        fe = ET.ElementTree(root)
        fe.write(f, encoding='utf-8', xml_declaration=True)
        arch_dte = f.getvalue()
        _logger.info("xml creado %s",str(arch_dte,'utf-8'))

        return arch_dte


    #def action_post(self):
    #    res = super(AccountMove, self).action_post()
    #    if self.move_type == 'out_invoice' and self.state=='posted':
    #        for move in self:
    #           # if move.partner_id.country_id.code == 'GT':
    #            _logger.info(" >>> Invoice %s is from Guatemala", move.name) 
    #    return res