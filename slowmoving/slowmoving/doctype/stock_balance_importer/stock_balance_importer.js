// Copyright (c) 2022, frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Balance Importer', {
	refresh: function(frm) {
		frm.add_custom_button("Import ISE Data", 
	 		() => frm.events.import_data(frm)
        );
	},
	 import_data : function(frm) {
	 	frappe.call({
				"method":"slowmoving.slowmoving.doctype.stock_balance_importer.stock_balance_importer.make_entries",
				"args":{
					"file_name": frm.doc.ise_file,
					"warehouse_name" : frm.doc.warehouse,
					"doc" : frm.doc.name
				},
				freeze: true,
				callback:function(r){
					if(!r.exc) {
    					if(r.message) {
   							frappe.msgprint("done")
                         }}
						}
        	   })

	 }
});