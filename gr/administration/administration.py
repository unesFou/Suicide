# -*- coding: utf-8 -*-
from odoo import models,fields

from odoo.exceptions import Warning

import json

file_path = '/home/sct/Desktop/workspace-project/odoo-server/my_addons_2/gr_suicide/data/refOrgan'

        # Function to read JSON data from file
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data
        
        
def save_json_file(data, file_path):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"JSON data saved to '{file_path}'.")
    except IOError:
        print(f"Error saving JSON data to '{file_path}'.")
        
class aa_administration(models.TransientModel):# models.TransientModel
    _name = 'aa.administration'
    
    
    old_company_id = fields.Many2one('res.company',"old company_id")
    new_company_id = fields.Many2one('res.company',"new company_id")
    date = fields.Datetime("Date")
    query =  fields.Char("query")
    
    
    def run_query(self):
        self._cr.execute(self.query)
        self._cr.commit()
        
    # def merge_company(self):
    #     print("________________________________________merge_company")
    def archive_not_used_companies(self):
        notification = self.env['aa.notification']
        active_comp_ids=[]
        notification_ids = notification.search([])
        for company_id in notification_ids.mapped("company_id"):
            comp_id=company_id
            active_comp_ids.append(comp_id.id)
            while comp_id.parent_id:
                active_comp_ids.append(comp_id.parent_id.id)
                comp_id=comp_id.parent_id
            # tr=True
        com_ids= self.env['res.company'].search([('id','not in',active_comp_ids)])
        for com_id in com_ids:
            com_id.write({'active':False})
            
        # print(active_comp_ids)
    def recompute_duration(self):
        not_ids = self.env['aa.notification'].search([('duration','=',False)])
        for not_id in not_ids:
            not_id._compute_duration()
            self.env.cr.commit()
            # print(not_id.id)
        print("end recompute_duration")
        
           
    def merge_in_table_by_sql(self,oldid,newid,table_name,field_name):
        table_name=table_name.replace(".","_")
#         try:
        query='update  %s set %s=%s where %s=%s'%(table_name,field_name,newid,field_name,oldid)
        print("________"+query)
        self._cr.execute(query)
#             print('__this_line good updated__',table_name)
#         except:
#             print('__this_query_not updated__',query)
        self._cr.commit()
        
        
    def merge_companies(self):
        oldid=self.old_company_id.id
        newid=self.new_company_id.id
        tables_with_try=["mail_followers"]
        if not oldid or not newid or oldid==newid:
            raise Warning("error des donnes saisie")
#         if self.old_partner_id.user_id or self.new_partner_id.user_id:
#             raise Warning("l'un de ces contacts est un utilisateur du système")
        field_ids=self.env["ir.model.fields"].search([('ttype','=','many2one'),('relation','=','res.company')])
        for field_id in field_ids:
            # if field_id.model =="sale.order":
            #     print(1)
            print("____table1___",field_id.model)
            table =''
            try:
                table=self.env[field_id.model]
            except:
                print("____function__merge_companys_table can't find in python file is__",field_id.model)
            if table != '':
                if table._table=="mail_followers":
                    print(1)
                if field_id.name in table.fields_get_keys() and field_id.store and table._auto:
    #             if table._table not in ['res_partner','res_users','ms_res_partner']:
                    if  table._table in tables_with_try:
                        try:
                            self.merge_in_table_by_sql(oldid, newid, table._table, field_id.name)
                        except:
                            self._cr.commit()
                            pass
                    else:
                        self.merge_in_table_by_sql(oldid, newid, table._table, field_id.name)
                
        field_ids=self.env["ir.model.fields"].search([('ttype','=','many2many'),('relation','=','res.company')])
        for field_id in field_ids:
            print("____table2___",field_id.model)
            table =''
            try:
                table=self.env[field_id.model]
            except:
                print("____function__merge_partners_table can't find in python file is__",field_id.model)
            if table != '':
#             print('________',field_id.relation_table)
#             if field_id.relation_table=="account_reconcile_model_template_res_partner_rel":
#                 print(1)
#             if table._table not in ["mail_channel"]:
                col_name=field_id.column1
                if field_id.column2:
                    if 'company_id' in field_id.column2:
                        col_name=field_id.column2
                if field_id.name in table.fields_get_keys() and field_id.store and table._auto and field_id.relation_table:
                        self.merge_in_table_by_sql(oldid, newid, field_id.relation_table, col_name)
        self.old_company_id.write({'active':False})
        print('_____merge_partners___done___')
        
    def adapt_unite_type(self):
        unite_type=self.env['aa.unite_type']
        res_company=self.env['res.company']
        
        json_data = read_json_file(file_path)
        count=0
        for unite_line in json_data:
            if unite_line['TYPE_REF_ORGAN_ID']=="":
                name = unite_line['ref_organ_name']
                if name[:4].upper() == "PMA ":
                    unite_line['TYPE_REF_ORGAN_ID']="36"
                elif name[:3].upper() in ["PM ","PM_"]:
                    unite_line['TYPE_REF_ORGAN_ID']="35"
                elif name[:3].upper() == "BJ ":
                    unite_line['TYPE_REF_ORGAN_ID']="5"
                elif name[:4].upper() == "PSP ":
                    unite_line['TYPE_REF_ORGAN_ID']="38"
                elif name[:3].upper() == "BT ":
                    unite_line['TYPE_REF_ORGAN_ID']="10"
                elif name[:5].upper() in ["PGTA ","BGTA "]:
                    unite_line['TYPE_REF_ORGAN_ID']="34"
                elif name[:10].upper() == "Compagnie ".upper():
                    unite_line['TYPE_REF_ORGAN_ID']="12"
                else:
                    # unite_line['TYPE_REF_ORGAN_ID']=""
                    print("name ____________ ",name)
                    count+=1
        
        save_json_file(json_data, file_path)
        print("the count of not imported unites is : ",count)
        # for unite_line in json_data:
        #     if unite_line['TYPE_REF_ORGAN_ID'] == "testttt":
        #         unite_line['TYPE_REF_ORGAN_ID']="testttt"  
                       
                             
    def import_unites(self):
        
        unite_type=self.env['aa.unite_type']
        res_company=self.env['res.company']
        
        
        
    

        
        def import_unite_line(unite_line,parent_id=None):
            if unite_line['TYPE_REF_ORGAN_ID']:
                type_id= unite_type.search([('id','=',int(unite_line['TYPE_REF_ORGAN_ID']))])
                if type_id and type_id.selected:
                    vals={'name':unite_line['ref_organ_name'],
                          'type_id':type_id.id,
                          'import_id':int(unite_line['_id'])}
                    if parent_id :
                        vals['parent_id']=parent_id.id
                    else:
                        vals['parent_id']=1
                    company_id = res_company.search([('import_id','=',int(unite_line['_id']))])
                    if not company_id:
                        # if unite_line['_id']=="282":
                        print("creating new unite :",vals)
                        company_id = company_id.sudo().create(vals)
                        # query="UPDATE res_company SET id = %s WHERE id = %s"%(int(unite_line['_id']),company_id.id);
                        # self._cr.execute(query)
                    else:
                        company_id.update(vals)
                    self._cr.commit()
            else:
                print("this line is not imported type_id is empty ",unite_line)
                return False
            
            
        # Reading JSON data from file
        
        json_data = read_json_file(file_path)
        print('importing les Régions')
        imported_unites=[]
        for unite_line in json_data:
            if unite_line['prefOrgan']  =='17' :# only the 
                    import_unite_line(unite_line)
                    
                    imported_unites.append(unite_line["ref_organ_name"])
        
        print("imported rég are : ",imported_unites)
        
        print('importing child unites of region')
        for i in range(1,4):
            for unite_line in json_data:
                # if unite_line['_id'] != '17':
                    parent_id = res_company.search([('import_id','=',int(unite_line['prefOrgan']))])
                    if parent_id:
                        import_unite_line(unite_line,parent_id)
                        if not unite_line['TYPE_REF_ORGAN_ID']:
                            print(1)
                            
        """ add all companies as alowed companies in admin user"""
        comp_ids = res_company.sudo().search([])
        self.env.user.company_ids = comp_ids
        print(json_data)
        
         
         
         
    def add_existing_unites_to_admin(self):
        res_comp = self.env["res.company"]
        unite_ids=res_comp.sudo().search([])
        self.env.user.company_ids = res_comp.search([])
        
    def mark_existing_unites_as_old(self):
        res_comp = self.env["res.company"]
        unite_ids=res_comp.sudo().search([])
        for unite_id in unite_ids:
            unite_id.name = unite_id.name + "_old"
        
    def delete_all_unites(self):
        res_comp = self.env["res.company"]
        unite_ids=res_comp.sudo().search([('id','!=',1)])
        self.env.user.company_ids = res_comp.search([('id','=',1)])
        self._cr.commit()
        for unite_id in unite_ids:
            try:
                unite_id.unlink()
                self._cr.commit()
            except:
                print(1)
        
    def show_last_old_notif(self):
        # domain=[]
        notif_obj = self.env['aa.notification']
        cam_ids = self.env['aa.camera'].search([])
        if not self.date:
            raise Warning("champ date obligatoire")
            # domain.append([('date_s','>',self.date)])
        res_camIds=[]
        for cam_id in cam_ids:
            if not notif_obj.search([('camera_id','=',cam_id.id),('date_s','>',self.date)]):
                res_camIds.append(cam_id.id)
                
        action = self.env.ref('gr_suicide.aa_notification_action').read()[0]
        action['domain']=[('camera_id','in',res_camIds)]
        # action = self.env.ref('gr_suicide.aa_camera_action').read()[0]
        # action['domain']=[('id','in',res_camIds)]
        return action 
    
    def show_camera_no_notif(self):
        # domain=[]
        notif_obj = self.env['aa.notification']
        cam_ids = self.env['aa.camera'].search([])
        res_camIds=[]
        for cam_id in cam_ids:
            if not notif_obj.search([('camera_id','=',cam_id.id)]):
                res_camIds.append(cam_id.id)
                #
        # action = self.env.ref('gr_suicide.aa_notification_action').read()[0]
        # action['domain']=[('camera_id','in',res_camIds)]
        action = self.env.ref('gr_suicide.aa_camera_action').read()[0]
        action['domain']=[('id','in',res_camIds)]
        return action
    
        # action['context'] = {**self.env.context, **{
            # 'default_is_root_directory': True,
            # 'default_root_storage': storage and storage.id
        # }}
        
        
        
        
        
        
        