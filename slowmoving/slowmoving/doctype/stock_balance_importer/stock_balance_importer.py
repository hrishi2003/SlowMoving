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
		uom_list = frappe.db.get_list('UOM',pluck='name')
		uom_list_lower = [ele.lower() for ele in uom_list]
		uom = (ise_file.cell(row=r,column=4)).value
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
		
		

		if item not in item_list:
			item_doc = frappe.new_doc("Item")
			if item_doc:
				item_doc.item_code = item
				name = (ise_file.cell(row=r,column=3)).value
				packing_date = (ise_file.cell(row=r,column=1)).value
				pack_date = datetime.strptime(str(packing_date),'%Y-%m-%d %H:%M:%S').date()
				item_doc.item_name = name
				item_doc.machine_type = (ise_file.cell(row=r,column=6)).value
				item_doc.item_group = "Products"
				item_doc.has_batch_no = 0
				
				uom = (ise_file.cell(row=r,column=4)).value
				item_doc.stock_uom = uom
				item_doc.save()
			else:
				frappe.throw("item document is not created")

		stc_ent_doc = frappe.new_doc("Stock Entry")
		availabe_qty = frappe.db.get_value('Bin',{'item_code':item, 'warehouse':warehouse_name} ,'actual_qty')
		
		if availabe_qty:
			print('-------------------STOCK LEdger ENTRY-------------------------')
			print('availabe_qty',availabe_qty)
			# for i in stock_ledg_ent:
			print('------------------MATERIAL Receipt---------------')
			if qty> availabe_qty:
				accepted_qty = qty - availabe_qty
				stc_ent_doc.stock_entry_type = 'Material Receipt'
				stc_ent_doc.posting_date = (ise_file.cell(row=r,column=1)).value
				stc_ent_doc.to_warehouse = warehouse_name
				item_code = (ise_file.cell(row=r,column=2)).value
				item_name = (ise_file.cell(row=r,column=3)).value
				# accepted_qty = (ise_file.cell(row=r,column=5)).value
				uom = (ise_file.cell(row=r,column=4)).value
				stc_ent_doc.append("items",{
					"item_code": item_code,
					"item_name": item_name,
					"t_warehouse": warehouse_name,
					"qty" : accepted_qty,
					"transfer_qty" : accepted_qty,
					"uom" : uom,
					"stock_uom" : uom,
					"conversion_factor" : 1,
					"allow_zero_valuation_rate" : 1,
					})


				stc_ent_doc.save()
				stc_ent_doc.submit()

			else:
				print('------------------MATERIAL ISSUE---------------')
				accepted_qty = availabe_qty - qty
				stc_ent_doc.stock_entry_type = 'Material Issue'
				stc_ent_doc.from_warehouse = warehouse_name
				item_code = (ise_file.cell(row=r,column=2)).value
				item_name = (ise_file.cell(row=r,column=3)).value
				stc_ent_doc.posting_date = (ise_file.cell(row=r,column=1)).value
				# accepted_qty = (ise_file.cell(row=r,column=5)).value
				uom = (ise_file.cell(row=r,column=4)).value
				stc_ent_doc.append("items",{
					"item_code": item_code,
					"item_name": item_name,
					"s_warehouse": warehouse_name,
					"qty" : accepted_qty,
					"transfer_qty" : accepted_qty,
					"uom" : uom,
					"stock_uom" : uom,
					"conversion_factor" : 1,
					"allow_zero_valuation_rate" : 1,
					})


				stc_ent_doc.save()
				stc_ent_doc.submit()

				

		else:
			print('------------------MATERIAL Receipt---------------')
			stc_ent_doc.stock_entry_type = 'Material Receipt'
			stc_ent_doc.to_warehouse = warehouse_name
			stc_ent_doc.posting_date = (ise_file.cell(row=r,column=1)).value
			item_code = (ise_file.cell(row=r,column=2)).value
			item_name = (ise_file.cell(row=r,column=3)).value
			accepted_qty = (ise_file.cell(row=r,column=5)).value
			uom = (ise_file.cell(row=r,column=4)).value
			stc_ent_doc.append("items",{
				"item_code": item_code,
				"item_name": item_name,
				"t_warehouse": warehouse_name,
				"qty" : accepted_qty,
				"transfer_qty" : accepted_qty,
				"uom" : uom,
				"stock_uom" : uom,
				"conversion_factor" : 1,
				"allow_zero_valuation_rate" : 1,
				})


			stc_ent_doc.save()
			stc_ent_doc.submit()
				
	frappe.msgprint("Stock Entry is Successfully Created")

