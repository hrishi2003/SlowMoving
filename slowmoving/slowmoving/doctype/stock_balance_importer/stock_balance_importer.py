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

def is_excel_file(file_name):
    _, ext = os.path.splitext(file_name)
    return ext == '.xlsx'

def create_or_update_item(item_code, item_name, uom, warehouse_name, balance_qty, machine_type):
    item_list = frappe.db.get_list('Item', pluck='name')
    uom_list_lower = [uom.lower() for uom in frappe.db.get_list('UOM', pluck='name')]

    if item_code not in item_list and not frappe.db.exists("Item", item_code):
        item_doc = frappe.new_doc("Item")
        item_doc.item_code = item_code
        item_doc.item_name = item_name
        item_doc.machine_type = machine_type
        item_doc.item_group = "Products"
        item_doc.has_batch_no = 0

        if uom.lower() not in uom_list_lower:
            uom_doc = frappe.new_doc("UOM")
            uom_doc.uom_name = uom
            uom_doc.save()
            item_doc.stock_uom = uom
        else:
            item_doc.stock_uom = uom

        item_doc.save()

    update_stock_balance(item_code, warehouse_name, balance_qty, machine_type)

def update_stock_balance(item_code, warehouse_name, balance_qty, machine_type):
    sbf = frappe.db.get_list('Stock Balance Form', {'item_code': item_code, 'warehouse': warehouse_name})
    if not sbf:
        # Create a new SBF TEST entry
        stc_bal = frappe.new_doc("Stock Balance Form")
        stc_bal.item_code = item_code
        stc_bal.warehouse = warehouse_name
        stc_bal.machine_type = machine_type
    else:
        # Update the existing SBF TEST entry
        stc_bal = frappe.get_doc("Stock Balance Form", sbf[0].name)

    stc_bal.balance_qty = balance_qty
    stc_bal.save()

@frappe.whitelist()
def make_entries(file_name, warehouse_name, doc):
    try:
        if not is_excel_file(file_name):
            frappe.throw('Please upload .xlsx format')

        media_file_path = frappe.get_doc("File", {"file_url": file_name}).get_full_path()
        ise_sheet = openpyxl.load_workbook(media_file_path)
        ise_file = ise_sheet.active

        # Create a list to track existing item codes from the Excel data
        existing_item_codes = []
        l=[]

        for row in range(2, ise_file.max_row + 1):
            item_code = ise_file.cell(row=row, column=2).value
            item_name = ise_file.cell(row=row, column=3).value
            uom = ise_file.cell(row=row, column=4).value
            balance_qty = ise_file.cell(row=row, column=5).value
            machine_type = ise_file.cell(row=row, column=6).value

            create_or_update_item(item_code, item_name, uom, warehouse_name, balance_qty, machine_type)

            existing_item_codes.append(item_code)

        # Set balance_qty to 0 for items not found in the uploaded Excel data
        frappe.log_error(f'items,{existing_item_codes}')
        sbf_entries = frappe.get_all('Stock Balance Form', {'warehouse': warehouse_name}, 'item_code', pluck='item_code')
        for item in sbf_entries:
            # item_code = entry.get('item_code')
            frappe.log_error(f'item2,{item}')
            if item not in existing_item_codes and item is not None:
                l.append(item)
        frappe.log_error(f"l,{l}")
        frappe.msgprint("Stock Balance Form is Successfully Created")
    except Exception as e:
        frappe.log_error(f"Error in make_entries: {str(e)}")
        frappe.throw("An error occurred while processing the file.")


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

# @frappe.whitelist()
# def make_st_ent(file_name,warehouse_name,doc):
# 	frappe.enqueue(make_entries, queue='long',timeout=8000,file_name=file_name,warehouse_name=warehouse_name,doc=doc)
# 	frappe.msgprint("Stock Balance Form is Successfully Created")


