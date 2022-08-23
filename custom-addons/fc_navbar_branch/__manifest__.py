{
    'name': "Company name in Navbar",
    'version': '15.0.1.0.0',
    'summary': """pos session access cashier does not show a session button 
                  and session closs button also""",
    'category': 'Point Of Sale',
    'depends': ['base'],
    'data': [
#               'views/records.xml'
    ],
     'assets': {
        'web.assets_qweb': [
              'fc_navbar_branch/static/src/xml/navbar.xml',

        ],
    },
    
    'installable': True,
    'auto_install': False,
    
    
}