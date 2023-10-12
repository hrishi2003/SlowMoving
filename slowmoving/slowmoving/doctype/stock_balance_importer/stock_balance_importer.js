// Copyright (c) 2022, frappe and contributors
// For license information, please see license.txt

// frappe.ui.form.on('Stock Balance Importer', {
// 	refresh: function(frm) {
// 		frm.add_custom_button("Stock Balance Data", 
// 	 		() => frm.events.import_data(frm)
//         );
// 	},
// 	 import_data : function(frm) {
// 	 	frappe.call({
// 				"method":"slowmoving.slowmoving.doctype.stock_balance_importer.stock_balance_importer.make_st_ent",
// 				"args":{
// 					"file_name": frm.doc.ise_file,
// 					"warehouse_name" : frm.doc.warehouse,
// 					"doc" : frm.doc.name
// 				},
// 				freeze: true,
// 				callback:function(r){
// 					console.log('GHJJHJHJHJBBJ')
// 					if(!r.exc) {
//     					if(r.message) {
//    							frappe.msgprint("done")
//                          }}
// 						}
//         	   })

// 	 },
// 	 download_template(frm) {
// 		open_url_post(frappe.request.url, {
// 			cmd: 'frappe.core.doctype.file.file.download_file',
// 			file_url: '/private/files/Sample Upload Template (1).xlsx'
// 		});
// 	},
// });
