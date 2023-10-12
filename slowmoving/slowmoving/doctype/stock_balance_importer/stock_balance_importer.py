# Copyright (c) 2022, frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
import os
import openpyxl
import datetime
from datetime import datetime

class StockBalanceImporter(Document):
	pass

@frappe.whitelist()
def make_entries(file_name,warehouse_name,doc):
	frappe.log_error('sdjsjdsajdjjsdjsadjsajbj')
	print('\n\n\n\njajsjjsaj\n\n\n\n\n\n')
	ware_doc = frappe.get_doc("Warehouse",warehouse_name)
	media_file_path = frappe.get_doc("File", {"file_url": file_name}).get_full_path()
	split_tup = os.path.splitext(media_file_path)
	if split_tup[1] != '.xlsx':
		frappe.throw('Please upload .xlsx format')
	
	ise_sheet = openpyxl.load_workbook(media_file_path)
	ise_file = ise_sheet.active
	rows_count = (ise_file.max_row)+1
	
	
	

	item_list = frappe.db.get_list('Item',pluck='name')
	uom_list = frappe.db.get_list('UOM',pluck='name')
	ic = []
	l = []
	for r in range(2,rows_count):
		uom_list = frappe.db.get_list('UOM',pluck='name')
		uom_list_lower = [ele.lower() for ele in uom_list]
		uom = (ise_file.cell(row=r,column=4)).value
		item_code = (ise_file.cell(row=r,column=2)).value
		ic.append(item_code)
		if uom is not None:
			uom_lower = uom.lower()
			if uom and uom_lower not in uom_list_lower:
				uom_doc = frappe.new_doc("UOM")
				if uom_doc:
					uom_doc.uom_name = uom
					uom_doc.save()
				else:
					frappe.throw("uom document not created")


			item = (ise_file.cell(row=r, column=2)).value
			qty = (ise_file.cell(row=r,column=5)).value
			item = str(item)

			
			

			if item not in item_list and not frappe.db.exists("Item",item):
				item_doc = frappe.new_doc("Item")
				if item_doc :
					item_doc.item_code = item
					name = (ise_file.cell(row=r,column=3)).value
					# packing_date = (ise_file.cell(row=r,column=1)).value
					# packing_date = str(packing_date)
					# pack_date = datetime.strptime(str(packing_date),'%Y-%m-%d %H:%M:%S').date()
					item_doc.item_name = name
					item_doc.machine_type = (ise_file.cell(row=r,column=6)).value
					item_doc.item_group = "Products"
					item_doc.has_batch_no = 0
					
					uom = (ise_file.cell(row=r,column=4)).value
					item_doc.stock_uom = uom
					item_doc.save()
				else:
					frappe.throw("item document is not created")

		
			
		sb1 = frappe.db.get_all('Stock Balance Form',{'warehouse':warehouse_name},'item_code', pluck='item_code')
		for x in sb1:
			l.append(x)
		sbf = frappe.db.get_list('Stock Balance Form',['item_code','warehouse'])

		k = []
		for i in sbf:
			k.append(tuple(i.values()))

		it_c = (ise_file.cell(row=r,column=2)).value
		



		if (it_c,warehouse_name) not in k:
			print('\n\n\n\nDJDJDJJDKJKDJDJK))(((\n\n\n\n')
			stc_bal = frappe.new_doc("Stock Balance Form")
			if stc_bal and (ise_file.cell(row=r,column=2)).value:
				stc_bal.item_code = (ise_file.cell(row=r,column=2)).value
				stc_bal.item_name = (ise_file.cell(row=r,column=3)).value
				stc_bal.machine_type = (ise_file.cell(row=r,column=6)).value
				stc_bal.stock_uom = (ise_file.cell(row=r,column=4)).value
				stc_bal.warehouse = warehouse_name
				stc_bal.balance_qty = (ise_file.cell(row=r,column=5)).value
				stc_bal.save()

		else:
			
			for y in l:
				if y in ic:
					if y == (ise_file.cell(row=r,column=2)).value:
						frappe.log_error(f'yyyyy{y}')
						sb = frappe.get_doc("Stock Balance Form",{'item_code':y,'warehouse':warehouse_name})
						sb.balance_qty = (ise_file.cell(row=r,column=5)).value
						frappe.log_error(f'balance_qty{sb.balance_qty}')
						sb.save()
				else:
					if y:
						sb = frappe.get_doc("Stock Balance Form",{'item_code':y,'warehouse':warehouse_name})
						sb.balance_qty = 0
						sb.save()
						# frappe.delete_doc('Stock Balance Form', sb.name)


	frappe.msgprint("Stock Balance Form is Successfully Created")

# 		stc_ent_doc = frappe.new_doc("Stock Entry")
# 		availabe_qty = frappe.db.get_value('Bin',{'item_code':item, 'warehouse':warehouse_name} ,'actual_qty')
# 		# se = frappe.db.get_list('Bin',fields=['item_code'],pluck='item_code')
# 		se = frappe.db.get_values('Bin',{'warehouse':warehouse_name},'item_code')
# 		item_code = (ise_file.cell(row=r,column=2)).value
# 		for i in se:
# 			for j in i:
# 				l.append(j)
				
		
# 		if availabe_qty:
# 			if qty> availabe_qty:
# 				accepted_qty = qty - availabe_qty
# 				stc_ent_doc.stock_entry_type = 'Material Receipt'
# 				stc_ent_doc.posting_date = (ise_file.cell(row=r,column=1)).value
# 				stc_ent_doc.to_warehouse = warehouse_name
# 				item_code = (ise_file.cell(row=r,column=2)).value
# 				item_name = (ise_file.cell(row=r,column=3)).value
# 				# accepted_qty = (ise_file.cell(row=r,column=5)).value
# 				uom = (ise_file.cell(row=r,column=4)).value
# 				if item_code is not None and item_name is not None and uom is not None:
# 					stc_ent_doc.append("items",{
# 						"item_code": item_code,
# 						"item_name": item_name,
# 						"t_warehouse": warehouse_name,
# 						"qty" : accepted_qty,
# 						"transfer_qty" : accepted_qty,
# 						"uom" : uom,
# 						"stock_uom" : uom,
# 						"conversion_factor" : 1,
# 						"allow_zero_valuation_rate" : 1,
# 						})


# 					stc_ent_doc.save()
# 					stc_ent_doc.submit()

# 			if qty< availabe_qty:
# 				accepted_qty = availabe_qty - qty
# 				stc_ent_doc.stock_entry_type = 'Material Issue'
# 				stc_ent_doc.from_warehouse = warehouse_name
# 				item_code = (ise_file.cell(row=r,column=2)).value
# 				item_name = (ise_file.cell(row=r,column=3)).value
# 				stc_ent_doc.posting_date = (ise_file.cell(row=r,column=1)).value
# 				# accepted_qty = (ise_file.cell(row=r,column=5)).value
# 				uom = (ise_file.cell(row=r,column=4)).value
# 				if item_code is not None and item_name is not None and uom is not None:
# 					stc_ent_doc.append("items",{
# 						"item_code": item_code,
# 						"item_name": item_name,
# 						"s_warehouse": warehouse_name,
# 						"qty" : accepted_qty,
# 						"transfer_qty" : accepted_qty,
# 						"uom" : uom,
# 						"stock_uom" : uom,
# 						"conversion_factor" : 1,
# 						"allow_zero_valuation_rate" : 1,
# 						})


# 					stc_ent_doc.save()
# 					stc_ent_doc.submit()

# 			# if item_code not in l:
# 			# 	qt = frappe.db.get_values('Bin',{'warehouse':warehouse_name},'item_code')

				

# 		else:
# 			stc_ent_doc.stock_entry_type = 'Material Receipt'
# 			stc_ent_doc.to_warehouse = warehouse_name
# 			stc_ent_doc.posting_date = (ise_file.cell(row=r,column=1)).value
# 			item_code = (ise_file.cell(row=r,column=2)).value
# 			item_name = (ise_file.cell(row=r,column=3)).value
# 			accepted_qty = (ise_file.cell(row=r,column=5)).value
# 			uom = (ise_file.cell(row=r,column=4)).value
# 			if item_code is not None and item_name is not None and uom is not None:
# 				stc_ent_doc.append("items",{
# 					"item_code": item_code,
# 					"item_name": item_name,
# 					"t_warehouse": warehouse_name,
# 					"qty" : accepted_qty,
# 					"transfer_qty" : accepted_qty,
# 					"uom" : uom,
# 					"stock_uom" : uom,
# 					"conversion_factor" : 1,
# 					"allow_zero_valuation_rate" : 1,
# 					})


# 				stc_ent_doc.save()
# 				stc_ent_doc.submit()

	
# 	for i in l:
# 		if i not in ic:
# 			stc_ent_doc = frappe.new_doc("Stock Entry")
# 			qt = frappe.db.get_value('Bin',{'warehouse':warehouse_name,'item_code':i},'actual_qty')
# 			uom  = frappe.db.get_value('Bin',{'warehouse':warehouse_name,'item_code':i},'stock_uom')

# 			stc_ent_doc.stock_entry_type = 'Material Issue'
# 			stc_ent_doc.from_warehouse = warehouse_name
# 			if qt > 0.0:
# 				stc_ent_doc.append("items",{
# 					"item_code": i,
# 					# "item_name": item_name,
# 					"s_warehouse": warehouse_name,
# 					"qty" : float(qt),
# 					"transfer_qty" : float(qt),
# 					"uom" : uom,
# 					"stock_uom" : uom,
# 					"conversion_factor" : 1,
# 					"allow_zero_valuation_rate" : 1,
# 					})


# 				stc_ent_doc.save()
# 				stc_ent_doc.submit()

				
# 	frappe.msgprint("Stock Entry is Successfully Created")

@frappe.whitelist()
def make_st_ent(file_name,warehouse_name,doc):
	frappe.enqueue(make_entries, queue='long',timeout=4000,file_name=file_name,warehouse_name=warehouse_name,doc=doc)


