# -*- coding: utf-8 -*-
from odoo import models,fields
from datetime import timedelta




class aa_unite_type(models.Model):# models.TransientModel
    _name = 'aa.unite_type'
    
    name = fields.Char("Type Unite",required=True)
    selected = fields.Boolean("selected")

    # active = fields.Boolean(string='Active',default=True)
    
    
    def import_unite_type(self):
        import json
        file_path = '/home/dgh/eclipse-workspace/odoo_12/gr_addons/gr_suicide/data/refOrgan'
    
        # Function to read JSON data from file
        def read_json_file(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
            return data
        
        json_data = read_json_file(file_path)
        for unite_line in json_data:
            
            if unite_line['TYPE_REF_ORGAN_ID']:
                unite_typeId = int(unite_line['TYPE_REF_ORGAN_ID'])
                unite_type_id = self.search([('id','=',unite_typeId)])
                if not unite_type_id:
                    vals={'id':unite_typeId,'name':unite_line['ref_organ_name']}
                    try:
                        unite_type_id = self.create(vals)
                        query="UPDATE aa_unite_type SET id = %s WHERE id = %s"%(unite_typeId,unite_type_id.id);
                        self._cr.execute(query)
                        self._cr.commit()
                    except :
                        print(unite_line['TYPE_REF_ORGAN_ID'],unite_line['ref_organ_name'])
                        print(1)
                # else:
                #     unite_type_id.update(vals)
            
            
        # print('importing other unites')
        # for i in range(1,4):
        #     for unite_line in json_data:
        #         if unite_line['_id'] != '17':
        #             parent_id = self.search([('id','=',int(unite_line['prefOrgan']))])
        #             if parent_id:
        #                 import_unite_line(unite_line,parent_id)
        #

        
    
class aa_unite(models.Model):# models.TransientModel
    _inherit = 'res.company'
    # _rec_name='name'
    # _order = 'sequence'
    
    # name = fields.Char("Nom",required=True)
    # sequence = fields.Integer('Sequence')
    # company_id = fields.Many2one('res.company', string='Company')#,required=True, related='voucher_id.company_id'
    camera_ids = fields.One2many('aa.camera', 'company_id', 'Cameras')
    
    active = fields.Boolean(string='Active',default=True)
    
    
    type_id = fields.Many2one('aa.unite_type', 'Type',required=True)
    import_id = fields.Integer('import_id')
     # fields.Selection([
     #    ('bt', 'Brigade'),
     #    ('cie', 'Companie'),
     #    ('reg', 'Région'),
     #    ], 'Type', default='bt')
    
    
    # parent_id  = fields.Many2one('aa.unite', 'Unité Parent')
    children_ids = fields.One2many('res.company', 'parent_id', 'Children')
    
    def get_presence_rate(self,datet_start,datet_end):
        if self.id == 86:
            print(1)
        result_rate=100
        if self.children_ids:
            childs_rate = []
            for child_id in self.children_ids:
                childs_rate.append(child_id.get_presence_rate(datet_start,datet_end))
            return int(sum(childs_rate)/len(childs_rate)+ 0.5)
        elif not self.camera_ids:
            return result_rate
        domain = [
            ('company_id', '=', self.id),
            ('type', '=', 'absence'),   # Filter by id=12
            '|',  # Logical OR operator
            '&',  # Logical AND operator (optional, if needed)
            ('date_s', '>=', datet_start),
            ('date_s', '<=', datet_end),
            '&',  # Logical AND operator (optional, if needed)
            ('date_e', '>=', datet_start),
            ('date_e', '<=', datet_end)
        ]
        abs_duration=timedelta()
        not_ids = self.env['aa.notification'].search(domain)
        for not_id in not_ids.filtered(lambda x:x.date_e != False):
            """"adapt_date_for calculate absence duration"""
            dt_s=not_id.date_s
            if dt_s<datet_start:
                dt_s=datet_start
                
            dt_e=not_id.date_e
            if dt_e>datet_end:
                dt_e=datet_end
                
            abs_duration += dt_e - dt_s
        
        if abs_duration:
            delta = datet_end - datet_start
            result_rate=int((1 - abs_duration.seconds/delta.total_seconds())*100+0.5)
        return result_rate
    
    
# "TYPE_REF_ORGAN_ID": "46",
# "ref_organ_name": "Region Rabat",

# "TYPE_REF_ORGAN_ID": "12",
#   "ref_organ_name": "Compagnie Jorf Lasfar",
  
  #   "TYPE_REF_ORGAN_ID": "10",
  # "ref_organ_name": "BT Ahfir",
  
  
  
    

    
    
    
    