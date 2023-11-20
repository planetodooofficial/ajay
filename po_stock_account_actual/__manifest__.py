{
    "name": "Actual Costing Method",
    "summary": "Costing at item level (Lot/serial No), Actual Costing Method, Real Costing Method, Product costing, Compute the cost of product, Inventory Valuation, Stock Valuation, Stock Removal Strategy, Material Costing, Calculate Real Cost, Lot, Serial Number, FIFO",
    "version": "16.0.0.2",
    'category': 'Warehouse',
    "website": "https://planet-odoo.com/",
	"description": """
		Actual Costing Method		 
		Costing at item level (Lot/serial No)
    """,
	'images':[
        'static/description/cover.png'
	],
    "author": "PlanetOdoo",
    "license": "OPL-1",
    # "price" : 299.9,
    # "currency": 'USD',
    
    "installable": True,
    "depends": [
        'stock_account'
    ],
    "data": [
        'view/product_category.xml',
        'view/stock_move.xml',
        'view/stock_valuation_layer.xml',
        'view/stock_valuation_layer_revaluation.xml',
    ],
    'qweb' : [
           
        ],
    'odoo-apps' : True                   
}

