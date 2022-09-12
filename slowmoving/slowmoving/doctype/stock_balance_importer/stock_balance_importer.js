// Copyright (c) 2022, frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Balance Importer', {
	refresh: function(frm) {
		frm.add_custom_button("Stock Balance Data", 
	 		() => frm.events.import_data(frm)
        );
	},
	 import_data : function(frm) {
		frappe.msgprint('HIIIII')
	 	frappe.call({
				"method":"slowmoving.slowmoving.doctype.stock_balance_importer.stock_balance_importer.make_entries",
				"args":{
					"file_name": frm.doc.ise_file,
					"warehouse_name" : frm.doc.warehouse,
					"doc" : frm.doc.name
				},
				freeze: true,
				callback:function(r){
					frappe.msgprint('HELLLOOO')
					if(!r.exc) {
    					if(r.message) {
   							frappe.msgprint("done")
                         }}
						}
        	   })

	 }
});