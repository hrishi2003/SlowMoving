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
	print('HIIEEHASAJKDKJI',file_name,warehouse_name)
	ware_doc = frappe.get_doc("Warehouse",warehouse_name)
	media_file_path = frappe.get_doc("File", {"file_url": file_name}).get_full_path()
	split_tup = os.path.splitext(media_file_path)
	if split_tup[1] != '.xlsx':
		frappe.throw('Please upload .xlsx format')
	
	ise_sheet = openpyxl.load_workbook(media_file_path)
	ise_file = ise_sheet.active
	rows_count = ise_file.max_row+1
	
	

	item_list = frappe.db.get_list('Item',pluck='name')
	print('\nITEM LIST\n',item_list,'\n')
	uom_list = frappe.db.get_list('UOM',pluck='name')
	

	for r in range(2,rows_count):
		frappe.msgprint('IMPORT FILE iterate')
		uom_list = frappe.db.get_list('UOM',pluck='name')
		print('IMPORT FILE UOMLIST',uom_list)
		uom_list_lower = [ele.lower() for ele in uom_list]
		uom = (ise_file.cell(row=r,column=4)).value
		uom_lower = uom.lower()
		if uom and uom_lower not in uom_list_lower:
			frappe.msgprint('IMPORT FILE UOMMMMMMMMM')
			uom_doc = frappe.new_doc("UOM")
			if uom_doc:
				print('IMPORT FILE UOMMDOCCCC',uom_doc)
				uom_doc.uom_name = uom
				frappe.msgprint('IMPORT FILE UOMMSAAVVVVVVE')
				uom_doc.save()
			else:
				frappe.throw("uom document not created")


		item = (ise_file.cell(row=r, column=2)).value
		qty = (ise_file.cell(row=r,column=5)).value
		print('I(*&^%$£%^&*()TEEEEEEEEMMMMMM',item)
		print('qty(*&^%$£%^&*()TEEEEEEEEMMMMMM',qty)
		

		if item not in item_list:
			item_doc = frappe.new_doc("Item")
			if item_doc:
				item_doc.item_code = item
				name = (ise_file.cell(row=r,column=3)).value
				packing_date = (ise_file.cell(row=r,column=1)).value
				pack_date = datetime.strptime(str(packing_date),'%Y-%m-%d %H:%M:%S').date()
				item_doc.item_name = name
				item_doc.item_group = "Products"
				item_doc.has_batch_no = 1
				
				uom = (ise_file.cell(row=r,column=4)).value
				item_doc.stock_uom = uom
				item_doc.save()
			else:
				frappe.throw("item document is not created")

		stc_ent_doc = frappe.new_doc("Stock Entry")
		stock_ledg_ent = frappe.db.get_list('Stock Ledger Entry', filters = {'item_code':item, 'warehouse':warehouse_name} ,fields=['item_code','qty_after_transaction'])
		
		if len(stock_ledg_ent)>= 1:
			for i in stock_ledg_ent:
				if qty> i['qty_after_transaction']:
					accepted_qty = qty - i['qty_after_transaction']
					stc_ent_doc.stock_entry_type = 'Material Receipt'
					stc_ent_doc.to_warehouse = warehouse_name
					item_code = (ise_file.cell(row=r,column=2)).value
					item_name = (ise_file.cell(row=r,column=3)).value
					accepted_qty = (ise_file.cell(row=r,column=5)).value
					uom = (ise_file.cell(row=r,column=4)).value
					stc_ent_doc.append("items",{
						"item_code": item_code,
						"item_name": item_name,
						"t_warehouse": warehouse_name,
						"qty" : accepted_qty,
						"uom" : uom,
						"allow_zero_valuation_rate" : 1,
						})


					stc_ent_doc.save()

				else:
					accepted_qty = i['qty_after_transaction'] - qty
					stc_ent_doc.stock_entry_type = 'Material Issue'
					stc_ent_doc.from_warehouse = warehouse_name
					item_code = (ise_file.cell(row=r,column=2)).value
					item_name = (ise_file.cell(row=r,column=3)).value
					accepted_qty = (ise_file.cell(row=r,column=5)).value
					uom = (ise_file.cell(row=r,column=4)).value
					stc_ent_doc.append("items",{
						"item_code": item_code,
						"item_name": item_name,
						"s_warehouse": warehouse_name,
						"qty" : accepted_qty,
						"uom" : uom,
						"allow_zero_valuation_rate" : 1,
						})


					stc_ent_doc.save()
				

		else:
			stc_ent_doc.stock_entry_type = 'Material Receipt'
			stc_ent_doc.to_warehouse = warehouse_name
			item_code = (ise_file.cell(row=r,column=2)).value
			item_name = (ise_file.cell(row=r,column=3)).value
			accepted_qty = (ise_file.cell(row=r,column=5)).value
			uom = (ise_file.cell(row=r,column=4)).value
			stc_ent_doc.append("items",{
				"item_code": item_code,
				"item_name": item_name,
				"t_warehouse": warehouse_name,
				"qty" : accepted_qty,
				"uom" : uom,
				"allow_zero_valuation_rate" : 1,
				})


			stc_ent_doc.save()
				
	frappe.msgprint("Stock Entry is Successfully Created")

