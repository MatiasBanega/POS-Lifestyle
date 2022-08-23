from datetime import datetime
from datetime import date 
from dateutil.relativedelta import relativedelta
from odoo.osv import osv
from odoo import api, fields, models
from odoo import exceptions, _
from odoo.exceptions import UserError
import xlwt
import io
import base64
import re
import xlsxwriter
from itertools import count
from email.policy import default
import psycopg2
import json
import psycopg2.extras
import timeit

DATE_FORMAT_1 = "%Y-%d-%m"
DATE_FORMAT_2 = "%d/%m/%y"
DATE_FORMAT_3 = "%m/%d/%y"


class ss_purchase_details_report_wzd(models.Model):
    _name = "ss.purchase.detail.report"
       
    start_date = fields.Date('Date From') #, required=True
    end_date = fields.Date(string="Date To")#, required=True
    partner_id = fields.Many2one('vendor.master', string="Vendor",default='')
    company_id = fields.Many2one('res.company',string='Company',default=lambda self:self.env.company.id)
    organization_id = fields.Many2one('organization.master', string="Organization")
    company_id_domain= fields.Char(
    compute="_compute_company_id_domain",
    readonly=True,
    store=False,
)


    @api.depends('organization_id')
    def _compute_company_id_domain(self):
        if self.company_id:
            print('ffffffffff')
            self.company_id_domain = json.dumps(
                [('org_id', '=',self.organization_id.org_id)]
            )
        
        
    
    def print_ss_purchase_detail_report(self):
        print('aaa')
       
        print('eeee')
        res = {}
        dict={}
        lis=[]
        start_date = self.start_date
        end_date = self.end_date
        partner_id = self.partner_id.name
        company_id = self.company_id.name
        organization_id=self.organization_id.name
        print('rrrrrr')
        try:
            print('ssss')
            db_conn = self.env['db.connection'].search([('company_id','=',self.company_id.id)], limit=1)
            print('db_conn',db_conn.company_id,self.company_id.id)         
            db_connect=db_conn.database_connect()
            print('function',db_connect)
            cursor = db_connect.cursor()
#             self.env['ss.purchase.detail.report.screen.line'].search([]).unlink()
            if partner_id:
                sql='''
                   SELECT 
m.documentno AS GRP_grn_no, 
m.um_billno AS STR_billno,

m.movementdate AS grn_date, 
p.name AS STR_vendor, 
w.name as STR_Warehouse, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.Um_grosscosttotal) END AS SUM_sub_total, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_vattotal) END AS SUM_taxamount, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_cesstotal) END AS SUM_Cess, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_netcosttotal) END AS SUM_total_value, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_additiondeductionamt) END AS SUM_add_ded,
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE coalesce(round(m.um_tcsamt,2),0) END AS SUM_TCS_Amount,
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_grandtotal) END AS SUM_net_amount,
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_additionalcharges) END AS SUM_FrieghtCharges,
pr.value as STR_pcode, 
pr.um_name as STR_productname, 
b.name as STR_Brand,

ml.movementqty as NUM_QTY, 
round(ml.um_mrp, 2) as SUM_mrp, 
round(ml.um_gkm, 2) as SUM_GKM, 
round(ml.um_sellingmarginmrp,2) as SUM_sellingmarginmrp,
round(ml.um_markdown, 2) as SUM_markdown, 
round(ml.um_markdown-ml.um_gkm,2) AS SUM_Diff_margin, 
case when ml.movementqty>0 then round((ml.um_mrp*(ml.um_markdown-ml.um_gkm)/ml.movementqty),2) 
else round((ml.um_mrp*(ml.um_markdown-ml.um_gkm)/1),2) End AS SUM_Diff_Amount, 
round(ml.um_netcost, 2) as SUM_lcost, 
round(ml.um_grosscosttotal, 2) as SUM_linesubtotal, 
dp.name as STR_Department,
pc.name as STR_Category,
mf.name as STR_Manufacturer,
ct.name as STR_tax, 
case when t.sopotype = 'B' and t.um_cgst_rate is null then coalesce(round(ml.um_vattotal, 2),0) else 0 end as NUM_igst, 
case when t.sopotype = 'B' 
and t.rate > 0 then coalesce (round(
ml.um_vattotal * t.um_cgst_rate / t.rate, 
2
) ,0) else 0 end as NUM_cgst, 
case when t.sopotype = 'B'
and t.rate > 0 then coalesce (round(
ml.um_vattotal * t.um_cgst_rate / t.rate, 
2
) ,0) else 0 end as NUM_sgst, 
round(ml.um_vattotal, 2) as NUM_linetaxtotal, 
round(ml.um_cesstotal, 2) as NUM_Cesstotal, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN NULL ELSE a.name END AS STR_created, 
case when m.reversal_id is not null then (
select 
docstatus || ' - ' || documentno :: text 
from 
m_inout 
where 
m_inout_id = m.reversal_id
) else null end as STR_ReversalNo, 
case when m.reversal_id is not null then (
select 
movementdate :: Date 
from 
m_inout 
where 
m_inout_id = m.reversal_id
) else null end as ReversedDate 
FROM 
M_InOutLine ml 
inner join c_tax t on t.c_taxcategory_id = ml.um_purchasetaxcategory_id 
and t.isactive = 'Y' 
join m_inout m on (ml.m_inout_id = m.m_inout_id) 
join c_bpartner p on (
m.c_bpartner_id = p.c_bpartner_id
) 
join ad_user a on (ml.createdby = a.ad_user_id) 
join m_product pr on (
ml.m_product_id = pr.m_product_id
) 
JOIN M_Product_Category pc ON pc.M_Product_Category_ID = pr.M_Product_Category_ID
join M_Warehouse w on (w.M_Warehouse_ID=m.M_Warehouse_ID) 
left JOIN um_manufacturer mf ON mf.UM_Manufacturer_ID = pr.UM_Manufacturer_ID
LEFT JOIN UM_Brand b ON b.UM_Brand_ID = pr.um_brand_id 
LEFT JOIN um_product_department dp ON dp.um_product_department_id = pr.um_product_department_id
join c_taxcategory ct on (
ml.um_purchasetaxcategory_id = ct.c_taxcategory_id) 
WHERE 
m.MovementType IN ('V+') 
AND (
(
m.Docstatus in ('CO', 'CL')
) 
or (
m.docstatus in ('VO', 'RE') 
and m.reversal_id is not null
))
AND m.AD_Client_ID = 1000001 
AND  cast(m.movementdate as Date) >= '%s' and  cast(m.movementdate as Date) <='%s'
and (
     p.name=null or  p.name='%s'
     )

union all
select r.GRP_grn_no as GRP_grn_no,null as STR_billno,null as grn_date,null as STR_vendor,
null as STR_Warehouse,
sum(SUM_sub_total) as SUM_sub_total,sum(SUM_taxamount) as SUM_taxamount,sum(SUM_Cess) as SUM_Cess,
sum(SUM_total_value) as SUM_total_value,
sum(SUM_add_ded) as SUM_add_ded,sum(SUM_TCS_Amount) as SUM_TCS_Amount,
sum(SUM_net_amount) as SUM_net_amount,
sum(SUM_FrieghtCharges) as SUM_FrieghtCharges,
null as STR_pcode,null as STR_productname,null as STR_Brand, sum(NUM_QTY) as NUM_QTY,sum(SUM_mrp) as SUM_mrp,sum(SUM_GKM) as SUM_GKM,
sum(SUM_sellingmarginmrp) as SUM_sellingmarginmrp,sum(SUM_markdown) as SUM_markdown,
sum(SUM_Diff_margin) as SUM_Diff_margin,sum(SUM_Diff_Amount )as SUM_Diff_Amount,
sum(SUM_lcost) as SUM_lcost, sum(SUM_linesubtotal) as SUM_linesubtotal, null as  STR_Department,
null as STR_Category,
null as STR_Manufacturer,null as STR_tax,sum(NUM_igst) as NUM_igst,sum(NUM_cgst) as NUM_cgst,
sum(NUM_sgst) as NUM_sgst,sum(NUM_linetaxtotal) as NUM_linetaxtotal,sum(NUM_Cesstotal) as NUM_Cesstotal, 
null as STR_created,
null as STR_ReversalNo, null as ReversedDate from
(
SELECT 
m.documentno AS GRP_grn_no, 
m.um_billno AS STR_billno,

m.movementdate AS grn_date, 
p.name AS STR_vendor, 
w.name as STR_Warehouse, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.Um_grosscosttotal) END AS SUM_sub_total, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_vattotal) END AS SUM_taxamount, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_cesstotal) END AS SUM_Cess, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_netcosttotal) END AS SUM_total_value, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_additiondeductionamt) END AS SUM_add_ded,
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE coalesce(round(m.um_tcsamt,2),0) END AS SUM_TCS_Amount,
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_grandtotal) END AS SUM_net_amount,
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_additionalcharges) END AS SUM_FrieghtCharges,
pr.value as STR_pcode, 
pr.um_name as STR_productname, 
b.name as STR_Brand,

ml.movementqty as NUM_QTY, 
round(ml.um_mrp, 2) as SUM_mrp, 
round(ml.um_gkm, 2) as SUM_GKM, 
round(ml.um_sellingmarginmrp,2) as SUM_sellingmarginmrp,
round(ml.um_markdown, 2) as SUM_markdown, 
round(ml.um_markdown-ml.um_gkm,2) AS SUM_Diff_margin, 
case when ml.movementqty>0 then round((ml.um_mrp*(ml.um_markdown-ml.um_gkm)/ml.movementqty),2) 
else round((ml.um_mrp*(ml.um_markdown-ml.um_gkm)/1),2) End AS SUM_Diff_Amount, 
round(ml.um_netcost, 2) as SUM_lcost, 
round(ml.um_grosscosttotal, 2) as SUM_linesubtotal, 
dp.name as STR_Department,
pc.name as STR_Category,
mf.name as STR_Manufacturer,
ct.name as STR_tax, 
case when t.sopotype = 'B' and t.um_cgst_rate is null then round(ml.um_vattotal, 2) else 0 end as NUM_igst, 
case when t.sopotype = 'B' 
and t.rate > 0 then round(
ml.um_vattotal * t.um_cgst_rate / t.rate, 
2
) else 0 end as NUM_cgst, 
case when t.sopotype = 'B'
and t.rate > 0 then round(
ml.um_vattotal * t.um_sgst_rate / t.rate, 
2
) else 0 end as NUM_sgst, 
round(ml.um_vattotal, 2) as NUM_linetaxtotal, 
round(ml.um_cesstotal, 2) as NUM_Cesstotal, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN NULL ELSE a.name END AS STR_created, 
case when m.reversal_id is not null then (
select 
docstatus || ' - ' || documentno :: text 
from 
m_inout 
where 
m_inout_id = m.reversal_id
) else null end as STR_ReversalNo, 
case when m.reversal_id is not null then (
select 
movementdate :: Date 
from 
m_inout 
where 
m_inout_id = m.reversal_id
) else null end as ReversedDate 
FROM 
M_InOutLine ml 
inner join c_tax t on t.c_taxcategory_id = ml.um_purchasetaxcategory_id 
and t.isactive = 'Y' 
join m_inout m on (ml.m_inout_id = m.m_inout_id) 
join c_bpartner p on (
m.c_bpartner_id = p.c_bpartner_id
) 
join ad_user a on (ml.createdby = a.ad_user_id) 
join m_product pr on (
ml.m_product_id = pr.m_product_id
) 
JOIN M_Product_Category pc ON pc.M_Product_Category_ID = pr.M_Product_Category_ID
join M_Warehouse w on (w.M_Warehouse_ID=m.M_Warehouse_ID) 
left JOIN um_manufacturer mf ON mf.UM_Manufacturer_ID = pr.UM_Manufacturer_ID

LEFT JOIN UM_Brand b ON b.UM_Brand_ID = pr.um_brand_id 
LEFT JOIN um_product_department dp ON dp.um_product_department_id = pr.um_product_department_id
join c_taxcategory ct on (
ml.um_purchasetaxcategory_id = ct.c_taxcategory_id) 
WHERE 
m.MovementType IN ('V+') 
AND (
(
m.Docstatus in ('CO', 'CL')
) 
or (
m.docstatus in ('VO', 'RE') 
and m.reversal_id is not null
))
AND m.AD_Client_ID = 1000001 
AND  cast(m.movementdate as Date) >= '%s' and  cast(m.movementdate as Date) <='%s'
and (
     p.name=null or  p.name='%s'
     )
)r group by  r.GRP_grn_no


order by GRP_grn_no, grn_date

             ''' %(start_date, end_date,partner_id,start_date, end_date,partner_id)
                


                cursor.execute(sql)
                #print(sql)
                purchase_data = cursor.fetchall()
              
    
            
            else:
                print('else')
                sql='''
                    SELECT 
m.documentno AS GRP_grn_no, 
m.um_billno AS STR_billno,

m.movementdate AS grn_date, 
p.name AS STR_vendor, 
w.name as STR_Warehouse, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.Um_grosscosttotal) END AS SUM_sub_total, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_vattotal) END AS SUM_taxamount, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_cesstotal) END AS SUM_Cess, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_netcosttotal) END AS SUM_total_value, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_additiondeductionamt) END AS SUM_add_ded,
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE coalesce(round(m.um_tcsamt,2),0) END AS SUM_TCS_Amount,
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_grandtotal) END AS SUM_net_amount,
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_additionalcharges) END AS SUM_FrieghtCharges,
pr.value as STR_pcode, 
pr.um_name as STR_productname, 
b.name as STR_Brand,

ml.movementqty as NUM_QTY, 
round(ml.um_mrp, 2) as SUM_mrp, 
round(ml.um_gkm, 2) as SUM_GKM, 
round(ml.um_sellingmarginmrp,2) as SUM_sellingmarginmrp,
round(ml.um_markdown, 2) as SUM_markdown, 
round(ml.um_markdown-ml.um_gkm,2) AS SUM_Diff_margin, 
case when ml.movementqty>0 then round((ml.um_mrp*(ml.um_markdown-ml.um_gkm)/ml.movementqty),2) 
else round((ml.um_mrp*(ml.um_markdown-ml.um_gkm)/1),2) End AS SUM_Diff_Amount, 
round(ml.um_netcost, 2) as SUM_lcost, 
round(ml.um_grosscosttotal, 2) as SUM_linesubtotal, 
dp.name as STR_Department,
pc.name as STR_Category,
mf.name as STR_Manufacturer,
ct.name as STR_tax, 
case when t.sopotype = 'B' and t.um_cgst_rate is null then coalesce(round(ml.um_vattotal, 2),0) else 0 end as NUM_igst, 
case when t.sopotype = 'B' 
and t.rate > 0 then coalesce (round(
ml.um_vattotal * t.um_cgst_rate / t.rate, 
2
) ,0) else 0 end as NUM_cgst, 
case when t.sopotype = 'B'
and t.rate > 0 then coalesce (round(
ml.um_vattotal * t.um_cgst_rate / t.rate, 
2
) ,0) else 0 end as NUM_sgst, 
round(ml.um_vattotal, 2) as NUM_linetaxtotal, 
round(ml.um_cesstotal, 2) as NUM_Cesstotal, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN NULL ELSE a.name END AS STR_created, 
case when m.reversal_id is not null then (
select 
docstatus || ' - ' || documentno :: text 
from 
m_inout 
where 
m_inout_id = m.reversal_id
) else null end as STR_ReversalNo, 
case when m.reversal_id is not null then (
select 
movementdate :: Date 
from 
m_inout 
where 
m_inout_id = m.reversal_id
) else null end as ReversedDate 
FROM 
M_InOutLine ml 
inner join c_tax t on t.c_taxcategory_id = ml.um_purchasetaxcategory_id 
and t.isactive = 'Y' 
join m_inout m on (ml.m_inout_id = m.m_inout_id) 
join c_bpartner p on (
m.c_bpartner_id = p.c_bpartner_id
) 
join ad_user a on (ml.createdby = a.ad_user_id) 
join m_product pr on (
ml.m_product_id = pr.m_product_id
) 
JOIN M_Product_Category pc ON pc.M_Product_Category_ID = pr.M_Product_Category_ID
join M_Warehouse w on (w.M_Warehouse_ID=m.M_Warehouse_ID) 
left JOIN um_manufacturer mf ON mf.UM_Manufacturer_ID = pr.UM_Manufacturer_ID
LEFT JOIN UM_Brand b ON b.UM_Brand_ID = pr.um_brand_id 
LEFT JOIN um_product_department dp ON dp.um_product_department_id = pr.um_product_department_id
join c_taxcategory ct on (
ml.um_purchasetaxcategory_id = ct.c_taxcategory_id) 
WHERE 
m.MovementType IN ('V+') 
AND (
(
m.Docstatus in ('CO', 'CL')
) 
or (
m.docstatus in ('VO', 'RE') 
and m.reversal_id is not null
))
AND m.AD_Client_ID = 1000001 
AND  cast(m.movementdate as Date) >= '%s' and  cast(m.movementdate as Date) <='%s'


union all
select r.GRP_grn_no as GRP_grn_no,null as STR_billno,null as grn_date,null as STR_vendor,
null as STR_Warehouse,
sum(SUM_sub_total) as SUM_sub_total,sum(SUM_taxamount) as SUM_taxamount,sum(SUM_Cess) as SUM_Cess,
sum(SUM_total_value) as SUM_total_value,
sum(SUM_add_ded) as SUM_add_ded,sum(SUM_TCS_Amount) as SUM_TCS_Amount,
sum(SUM_net_amount) as SUM_net_amount,
sum(SUM_FrieghtCharges) as SUM_FrieghtCharges,
null as STR_pcode,null as STR_productname,null as STR_Brand, sum(NUM_QTY) as NUM_QTY,sum(SUM_mrp) as SUM_mrp,sum(SUM_GKM) as SUM_GKM,
sum(SUM_sellingmarginmrp) as SUM_sellingmarginmrp,sum(SUM_markdown) as SUM_markdown,
sum(SUM_Diff_margin) as SUM_Diff_margin,sum(SUM_Diff_Amount )as SUM_Diff_Amount,
sum(SUM_lcost) as SUM_lcost, sum(SUM_linesubtotal) as SUM_linesubtotal, null as  STR_Department,
null as STR_Category,
null as STR_Manufacturer,null as STR_tax,sum(NUM_igst) as NUM_igst,sum(NUM_cgst) as NUM_cgst,
sum(NUM_sgst) as NUM_sgst,sum(NUM_linetaxtotal) as NUM_linetaxtotal,sum(NUM_Cesstotal) as NUM_Cesstotal, 
null as STR_created,
null as STR_ReversalNo, null as ReversedDate from
(
SELECT 
m.documentno AS GRP_grn_no, 
m.um_billno AS STR_billno,

m.movementdate AS grn_date, 
p.name AS STR_vendor, 
w.name as STR_Warehouse, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.Um_grosscosttotal) END AS SUM_sub_total, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_vattotal) END AS SUM_taxamount, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_cesstotal) END AS SUM_Cess, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_netcosttotal) END AS SUM_total_value, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_additiondeductionamt) END AS SUM_add_ded,
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE coalesce(round(m.um_tcsamt,2),0) END AS SUM_TCS_Amount,
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_grandtotal) END AS SUM_net_amount,
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN 0 ELSE round(m.um_additionalcharges) END AS SUM_FrieghtCharges,
pr.value as STR_pcode, 
pr.um_name as STR_productname, 
b.name as STR_Brand,

ml.movementqty as NUM_QTY, 
round(ml.um_mrp, 2) as SUM_mrp, 
round(ml.um_gkm, 2) as SUM_GKM, 
round(ml.um_sellingmarginmrp,2) as SUM_sellingmarginmrp,
round(ml.um_markdown, 2) as SUM_markdown, 
round(ml.um_markdown-ml.um_gkm,2) AS SUM_Diff_margin, 
case when ml.movementqty>0 then round((ml.um_mrp*(ml.um_markdown-ml.um_gkm)/ml.movementqty),2) 
else round((ml.um_mrp*(ml.um_markdown-ml.um_gkm)/1),2) End AS SUM_Diff_Amount, 
round(ml.um_netcost, 2) as SUM_lcost, 
round(ml.um_grosscosttotal, 2) as SUM_linesubtotal, 
dp.name as STR_Department,
pc.name as STR_Category,
mf.name as STR_Manufacturer,
ct.name as STR_tax, 
case when t.sopotype = 'B' and t.um_cgst_rate is null then round(ml.um_vattotal, 2) else 0 end as NUM_igst, 
case when t.sopotype = 'B' 
and t.rate > 0 then round(
ml.um_vattotal * t.um_cgst_rate / t.rate, 
2
) else 0 end as NUM_cgst, 
case when t.sopotype = 'B'
and t.rate > 0 then round(
ml.um_vattotal * t.um_sgst_rate / t.rate, 
2
) else 0 end as NUM_sgst, 
round(ml.um_vattotal, 2) as NUM_linetaxtotal, 
round(ml.um_cesstotal, 2) as NUM_Cesstotal, 
CASE WHEN LAG(m.m_inout_id) OVER (
ORDER BY 
m.m_inout_id, 
ml.line
) = m.m_inout_id THEN NULL ELSE a.name END AS STR_created, 
case when m.reversal_id is not null then (
select 
docstatus || ' - ' || documentno :: text 
from 
m_inout 
where 
m_inout_id = m.reversal_id
) else null end as STR_ReversalNo, 
case when m.reversal_id is not null then (
select 
movementdate :: Date 
from 
m_inout 
where 
m_inout_id = m.reversal_id
) else null end as ReversedDate 
FROM 
M_InOutLine ml 
inner join c_tax t on t.c_taxcategory_id = ml.um_purchasetaxcategory_id 
and t.isactive = 'Y' 
join m_inout m on (ml.m_inout_id = m.m_inout_id) 
join c_bpartner p on (
m.c_bpartner_id = p.c_bpartner_id
) 
join ad_user a on (ml.createdby = a.ad_user_id) 
join m_product pr on (
ml.m_product_id = pr.m_product_id
) 
JOIN M_Product_Category pc ON pc.M_Product_Category_ID = pr.M_Product_Category_ID
join M_Warehouse w on (w.M_Warehouse_ID=m.M_Warehouse_ID) 
left JOIN um_manufacturer mf ON mf.UM_Manufacturer_ID = pr.UM_Manufacturer_ID

LEFT JOIN UM_Brand b ON b.UM_Brand_ID = pr.um_brand_id 
LEFT JOIN um_product_department dp ON dp.um_product_department_id = pr.um_product_department_id
join c_taxcategory ct on (
ml.um_purchasetaxcategory_id = ct.c_taxcategory_id) 
WHERE 
m.MovementType IN ('V+') 
AND (
(
m.Docstatus in ('CO', 'CL')
) 
or (
m.docstatus in ('VO', 'RE') 
and m.reversal_id is not null
))
AND m.AD_Client_ID = 1000001 
AND  cast(m.movementdate as Date) >= '%s' and  cast(m.movementdate as Date) <='%s'

)r group by  r.GRP_grn_no


order by GRP_grn_no, grn_date


                ''' %(start_date, end_date,start_date, end_date)
             
            if sql:    
                cursor.execute(sql)
                print('sql',sql)
                purchase_data = cursor.fetchall()
                print('purchase',purchase_data)
            self.createform3a(purchase_data)
            print('create')
            return 
        
#         except (Exception, psycopg2.Error) as error:
#             raise UserError(_("Error while fetching data from PostgreSQL "))
#             print("Error while fetching data from PostgreSQL", error)

        finally:
            if db_conn:
                cursor.close()
#                     print('db_connect',db_connect)
#                     print('close',db_connect.close)
                db_connect.close()
#                     print('db_connect1',db_connect)
#                     print('close1',db_connect.close)
        
#         stop = timeit.default_timer()
#         print("return Run Time = ", stop - start)
    
    def createform3a(self,purchase_data):
        
#         self.env['ss.purchase.detail.report.gst.view'].search([]).unlink()
        form_header = self.env['ss.purchase.detail.report.gst.view'].search([])
        print('line',form_header)
        print('unlink')
        if form_header:
            print('form_header',form_header)
            for line in purchase_data: 
            
                print('line',line)  
                self.create     
                ({
                     'grn_no' : line[0],
                                'bill_no' : line[1],
#                                 'bill_date' : line['bill_date'],
                                'grn_date' : line[2],
                                'partner_id' : line[3],
                                'ware_house' : line[4],
                                'sub_total' : line[5],
                                'tax_amt' : line[6],
                                'cess' : line[7],
                                'total_val' : line[8],
                                'add_ded' : line[9],
                                'tcs_amt' : line[10],
                                'net_amt' : line[11],
                                'freight_charges' : line[12],
                                'pcode' : line[13],
                                'product_id' : line[14],
                                'brand' : line[15],
#                                 'item_type' : line['STR_Itemtype'],
#                                 'prod_design' : line['STR_ProductDesign'],
#                                 'prod_color' : line['STR_ProductColor'],
#                                 'prod_size' : line['STR_ProductSize'],
                                'qty' : line[16],
                                'mrp' : line[17],
                                'gkm' : line[18],
                                'sp_margin_mrp' : line[19],
                                'm_down' : line[20],
                                'diff_margin' : line[21],
                                'diff_amt' : line[22],
                                'lcost' : line[23],
                                'line_subtot' : line[24],
                                 
                                'dept' : line[25],
                                'categ' : line[26],
                                'manuftr' : line[27],
                                'tax' : line[28],
                                'igst' : line[29],
                                'cgst' : line[30],
                                'sgst' : line[31],
                                'line_taxtot' : line[32],
                                'cess_tot' : line[33],
                                'created' : line[34],
                                'reversal_no' : line[35],
                                'reversed_date' : line[36],
                                                                                
        })
        print('vvvvvvv')
# v=ss_purchase_details_report_wzd().createform3a()         
       
      

