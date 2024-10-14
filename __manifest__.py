# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Suicide_GR',
    'version' : '1.1',
    'sequence': 5,
    'author': 'GR',
    'summary' : """
    Suicide_GR:
    """,
    'category': 'autre',
    'website': 'https://www.gr.com',
    'depends' : ['base','mail'],
    'data': [
            'security/security.xml',
            'security/ir.model.access.csv',
            
            'gr/company/company.xml',
            'gr/camera/camera.xml',
            'gr/notification/notification.xml',
            'gr/zabbix/host.xml',
            
            'gr/administration/administration.xml',
            
            'gr/zmenu.xml',
    ],
    'css': ['static/src/css/report.scss'],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
