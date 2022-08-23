# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Initial Setup Tools',
    'version': '1.0',
    'category': 'Hidden',
    'description': """
This module helps to configure the system at the installation of a new database.
================================================================================

Shows you a list of applications features to install from.

    """,
    'depends': ['base', 'web','base_setup','mail','mail_bot'],
    
    'demo': [],
    'installable': True,
    'auto_install': False,
    'data': [

        'views/reset_config.xml', ],
    'assets': {
       
        'web.assets_qweb': [
            'hide_community_edition/static/src/xml/**/*',
        ],
    },
    'license': 'LGPL-3',
}
