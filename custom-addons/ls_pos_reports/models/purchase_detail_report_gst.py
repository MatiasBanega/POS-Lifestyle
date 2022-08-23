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

DATE_FORMAT_1 = "%Y-%d-%m"
DATE_FORMAT_2 = "%d/%m/%y"
DATE_FORMAT_3 = "%m/%d/%y"


class purchase_details_report_wzd(models.Model):
    _name = "purchase.detail.report"
       
    start_date = fields.Date('Date From') #, required=True
    end_date = fields.Date(string="Date To")#, required=True
    partner_id = fields.Many2one('vendor.master', string="Vendor")
    company_id = fields.Many2one('res.company',string='Company',default=lambda self:self.env.company.id)
    
    company_id_domain= fields.Char(
    compute="_compute_company_id_domain",
    readonly=True,
    store=False,
)


    @api.depends('company_id')
    def _compute_company_id_domain(self):
        if self.company_id:
            self.company_id_domain = json.dumps(
                [('org_id', '=',self.company_id.organization_id.org_id)]
            )
        else:
            self.company_id_domain = json.dumps(
                []
            )

    
       
    def print_purchase_detail_report(self):

        def get_purchase_lines(self):
            res = {}
            dict={}
            lis=[]
            start_date = self.start_date
            end_date = self.end_date
            partner_id = self.partner_id.name
            company_id = self.company_id.name
            
            try:
                db_conn = self.env['db.connection'].search([('company_id','=',self.company_id.id)], limit=1)
                db_connect=db_conn.database_connect()
                cursor = db_connect.cursor()
                self.env['purchase.detail.report.screen.line'].search([]).unlink()
                if partner_id:
                    sql='''
                        SELECT 
          m.documentno AS GRP_grn_no, 
          m.um_billno AS STR_billno,
          m.um_billdate AS bill_date, 
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
          ) = m.m_inout_id THEN 0 ELSE round(m.um_tcsamt) END AS SUM_TCS_Amount,
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
           i.name as STR_Itemtype,
           pd.name as STR_ProductDesign,
           pcr.name as STR_ProductColor,
           s.name as STR_ProductSize,
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
        inner join um_productattribute pa on (ml.um_productattribute_id=pa.um_productattribute_id and ml.m_product_id=pa.m_product_id)
        left join um_brand b on (pa.um_brand_id=b.um_brand_id) 
        left join um_itemtype i on (pa.um_itemtype_id=i.um_itemtype_id) 
        left join um_productdesign pd on (pa.um_productdesign_id=pd.um_productdesign_id)
        left join um_productcolor pcr on (pa.um_productcolor_id = pcr.um_productcolor_id)
        left join um_productsize s on (pa.um_productsize_id=s.um_productsize_id)
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
        select r.GRP_grn_no as GRP_grn_no,null as STR_billno,null as bill_date,null as grn_date,null as STR_vendor,
        null as STR_Warehouse,
        sum(SUM_sub_total) as SUM_sub_total,sum(SUM_taxamount) as SUM_taxamount,sum(SUM_Cess) as SUM_Cess,
        sum(SUM_total_value) as SUM_total_value,
        sum(SUM_add_ded) as SUM_add_ded,sum(SUM_TCS_Amount) as SUM_TCS_Amount,
        sum(SUM_net_amount) as SUM_net_amount,
        sum(SUM_FrieghtCharges) as SUM_FrieghtCharges,
        null as STR_pcode,null as STR_productname,null as STR_Brand, null as STR_Itemtype, null as STR_ProductDesign,
        null as STR_ProductColor, null as STR_ProductSize,sum(NUM_QTY) as NUM_QTY,sum(SUM_mrp) as SUM_mrp,sum(SUM_GKM) as SUM_GKM,
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
          m.um_billdate AS bill_date, 
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
          ) = m.m_inout_id THEN 0 ELSE round(m.um_tcsamt) END AS SUM_TCS_Amount,
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
           i.name as STR_Itemtype,
           pd.name as STR_ProductDesign,
           pcr.name as STR_ProductColor,
           s.name as STR_ProductSize,
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
        inner join um_productattribute pa on (ml.um_productattribute_id=pa.um_productattribute_id and ml.m_product_id=pa.m_product_id)
        left join um_brand b on (pa.um_brand_id=b.um_brand_id) 
        left join um_itemtype i on (pa.um_itemtype_id=i.um_itemtype_id) 
        left join um_productdesign pd on (pa.um_productdesign_id=pd.um_productdesign_id)
        left join um_productcolor pcr on (pa.um_productcolor_id = pcr.um_productcolor_id)
        left join um_productsize s on (pa.um_productsize_id=s.um_productsize_id)
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
                    purchase_data = cursor.fetchall()
                    
#                 
                
                else:
                    sql='''
                        SELECT 
          m.documentno AS GRP_grn_no, 
          m.um_billno AS STR_billno,
          m.um_billdate AS bill_date, 
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
          ) = m.m_inout_id THEN 0 ELSE round(m.um_tcsamt) END AS SUM_TCS_Amount,
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
           i.name as STR_Itemtype,
           pd.name as STR_ProductDesign,
           pcr.name as STR_ProductColor,
           s.name as STR_ProductSize,
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
        inner join um_productattribute pa on (ml.um_productattribute_id=pa.um_productattribute_id and ml.m_product_id=pa.m_product_id)
        left join um_brand b on (pa.um_brand_id=b.um_brand_id) 
        left join um_itemtype i on (pa.um_itemtype_id=i.um_itemtype_id) 
        left join um_productdesign pd on (pa.um_productdesign_id=pd.um_productdesign_id)
        left join um_productcolor pcr on (pa.um_productcolor_id = pcr.um_productcolor_id)
        left join um_productsize s on (pa.um_productsize_id=s.um_productsize_id)
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
        select r.GRP_grn_no as GRP_grn_no,null as STR_billno,null as bill_date,null as grn_date,null as STR_vendor,
        null as STR_Warehouse,
        sum(SUM_sub_total) as SUM_sub_total,sum(SUM_taxamount) as SUM_taxamount,sum(SUM_Cess) as SUM_Cess,
        sum(SUM_total_value) as SUM_total_value,
        sum(SUM_add_ded) as SUM_add_ded,sum(SUM_TCS_Amount) as SUM_TCS_Amount,
        sum(SUM_net_amount) as SUM_net_amount,
        sum(SUM_FrieghtCharges) as SUM_FrieghtCharges,
        null as STR_pcode,null as STR_productname,null as STR_Brand, null as STR_Itemtype, null as STR_ProductDesign,
        null as STR_ProductColor, null as STR_ProductSize,sum(NUM_QTY) as NUM_QTY,sum(SUM_mrp) as SUM_mrp,sum(SUM_GKM) as SUM_GKM,
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
          m.um_billdate AS bill_date, 
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
          ) = m.m_inout_id THEN 0 ELSE round(m.um_tcsamt) END AS SUM_TCS_Amount,
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
           i.name as STR_Itemtype,
           pd.name as STR_ProductDesign,
           pcr.name as STR_ProductColor,
           s.name as STR_ProductSize,
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
        inner join um_productattribute pa on (ml.um_productattribute_id=pa.um_productattribute_id and ml.m_product_id=pa.m_product_id)
        left join um_brand b on (pa.um_brand_id=b.um_brand_id) 
        left join um_itemtype i on (pa.um_itemtype_id=i.um_itemtype_id) 
        left join um_productdesign pd on (pa.um_productdesign_id=pd.um_productdesign_id)
        left join um_productcolor pcr on (pa.um_productcolor_id = pcr.um_productcolor_id)
        left join um_productsize s on (pa.um_productsize_id=s.um_productsize_id)
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
                    
                    
                cursor.execute(sql)
                purchase_data = cursor.fetchall()
                for row in purchase_data:      
                    dict = {'GRP_grn_no':row[0],'STR_billno':row[1] , 'bill_date':row[2] ,'grn_date':row[3] ,
                        'STR_vendor':row[4],
                        'STR_Warehouse':row[5], 'SUM_sub_total':row[6],'SUM_taxamount':row[7],
                        'SUM_Cess':row[8],'SUM_total_value':row[9] , 'SUM_add_ded':row[10],'SUM_TCS_Amount':row[11],
                        'SUM_net_amount':row[12],'SUM_FrieghtCharges':row[13] , 'STR_pcode':row[14],'STR_productname':row[15],
                        'STR_Brand':row[16],'STR_Itemtype':row[17],'STR_ProductDesign':row[18],'STR_ProductColor':row[19],'STR_ProductSize':row[20],
                        'NUM_QTY':row[21],'SUM_mrp':row[22] , 'SUM_GKM':row[23],'SUM_sellingmarginmrp':row[24],
                        'SUM_markdown':row[25],'SUM_Diff_margin':row[26] , 'SUM_Diff_Amount':row[27],'SUM_lcost':row[28],
                        'SUM_linesubtotal':row[29], 'STR_Department':row[30],'STR_Category':row[31],
                        'STR_Manufacturer':row[32],'STR_tax':row[33] , 'NUM_igst':row[34],'NUM_cgst':row[35],
                        'NUM_sgst':row[36],
                        'NUM_linetaxtotal':row[37] ,
                         'NUM_Cesstotal':row[38],'STR_created':row[39],
                        'STR_ReversalNo':row[40],
                        'ReversedDate':row[41],
    #                 
                        }
                    lis.append(dict)
                
                return lis
            except (Exception, psycopg2.Error) as error:
                
                raise UserError(_("Error while fetching data from PostgreSQL "))
    
            finally:
    # closing database connection.
                if db_conn:
                    cursor.close()
                    db_connect.close()
            
        tsub = 0  
        ttax = 0
        tcess = 0
        ttvalue = 0
        ta_d = 0
        ttcs = 0
        tnet = 0
        tfrght = 0
        tqty = 0
        tmrp = 0
        tgkm = 0
        tsellmrp = 0
        tmdown = 0
        tdiffmrgn = 0
        tdiffamt = 0
        tlcst = 0
        tlstot = 0
        tigst = 0
        tcgst = 0
        tsgst = 0
        tltaxtot = 0
        tcesstot = 0
        twarhse=0
        purchase_detail_line = []
        seq = 0
        
        for line in get_purchase_lines(self):         
                
            if line['STR_Warehouse']:
                tsub+=line['SUM_sub_total']  
            if line['STR_Warehouse']:
                ttax+=line['SUM_taxamount']
            if line['STR_Warehouse']:
                tcess+=line['SUM_Cess']
            if line['STR_Warehouse']:
                ttvalue+=line['SUM_total_value']
            if line['STR_Warehouse']:
                ta_d+=line['SUM_add_ded']
            if line['STR_Warehouse']:
                ttcs+=line['SUM_TCS_Amount']
            if line['STR_Warehouse']:
                tnet+=line['SUM_net_amount']  
            if line['STR_Warehouse']:
                tfrght+=line['SUM_FrieghtCharges'] 
            if line['STR_Warehouse']:
                tqty+=line['NUM_QTY']
            if line['STR_Warehouse']:
                tmrp+=line['SUM_mrp']
            if line['STR_Warehouse']:
                tgkm+=line['SUM_GKM']
            if line['STR_Warehouse']:
                tsellmrp+=line['SUM_sellingmarginmrp']
            if line['STR_Warehouse']:
                tmdown+=line['SUM_markdown']
            if line['STR_Warehouse']:
                tdiffmrgn+=line['SUM_Diff_margin']
            if line['STR_Warehouse']:
                tdiffamt+=line['SUM_Diff_Amount']
            if line['STR_Warehouse']:
                tlcst+=line['SUM_lcost']  
            if line['STR_Warehouse']:
                tlstot+=line['SUM_linesubtotal'] 
            if line['STR_Warehouse']:
                tigst+=line['NUM_igst']
            if line['STR_Warehouse']:
                tcgst+=line['NUM_cgst']
            if line['STR_Warehouse']:
                tsgst+=line['NUM_sgst']
            if line['STR_Warehouse']:
                tltaxtot+=line['NUM_linetaxtotal']
            if line['STR_Warehouse']:
                tcesstot+=line['NUM_Cesstotal']  
            
                

            purchase_detail_line.append((0,0,{
                                'grn_no' : line['GRP_grn_no'],
                                'bill_no' : line['STR_billno'],
                                'bill_date' : line['bill_date'],
                                'grn_date' : line['grn_date'],
                                'partner_id' : line['STR_vendor'],
                                'ware_house' : line['STR_Warehouse'],
                                'sub_total' : line['SUM_sub_total'],
                                'tax_amt' : line['SUM_taxamount'],
                                'cess' : line['SUM_Cess'],
                                'total_val' : line['SUM_total_value'],
                                'add_ded' : line['SUM_add_ded'],
                                'tcs_amt' : line['SUM_TCS_Amount'],
                                'net_amt' : line['SUM_net_amount'],
                                'freight_charges' : line['SUM_FrieghtCharges'],
                                'pcode' : line['STR_pcode'],
                                'product_id' : line['STR_productname'],
                                'brand' : line['STR_Brand'],
                                'item_type' : line['STR_Itemtype'],
                                'prod_design' : line['STR_ProductDesign'],
                                'prod_color' : line['STR_ProductColor'],
                                'prod_size' : line['STR_ProductSize'],
                                'qty' : line['NUM_QTY'],
                                'mrp' : line['SUM_mrp'],
                                'gkm' : line['SUM_GKM'],
                                'sp_margin_mrp' : line['SUM_sellingmarginmrp'],
                                'm_down' : line['SUM_markdown'],
                                'diff_margin' : line['SUM_Diff_margin'],
                                'diff_amt' : line['SUM_Diff_Amount'],
                                'lcost' : line['SUM_lcost'],
                                'line_subtot' : line['SUM_linesubtotal'],
                                'brand' : line['STR_Brand'],
                                'dept' : line['STR_Department'],
                                'categ' : line['STR_Category'],
                                'manuftr' : line['STR_Manufacturer'],
                                'tax' : line['STR_tax'],
                                'igst' : line['NUM_igst'],
                                'cgst' : line['NUM_cgst'],
                                'sgst' : line['NUM_sgst'],
                                'line_taxtot' : line['NUM_linetaxtotal'],
                                'cess_tot' : line['NUM_Cesstotal'],
                                'created' : line['STR_created'],
                                'reversal_no' : line['STR_ReversalNo'],
                                'reversed_date' : line['ReversedDate'],
                                
                              
                                     }))
        if purchase_detail_line:
            purchase_detail_line.append((0,0,{
                                'grn_no' : 'Total',
                                'sub_total' : tsub,
                                'tax_amt' : ttax,
                                'cess' : tcess,
                                'total_val' : ttvalue,
                                'add_ded' : ta_d,
                                'tcs_amt' : ttcs,
                                'net_amt' : tnet,
                                'freight_charges' : tfrght,
                                'qty' : tqty,
                                'mrp' : tmrp,
                                'gkm' : tgkm,
                                'sp_margin_mrp' : tsellmrp,
                                'm_down' : tmdown,
                                'diff_margin' : tdiffmrgn,
                                'diff_amt' : tdiffamt,
                                'lcost' : tlcst,
                                'line_subtot' : tlstot,
                                'igst' : tigst,
                                'cgst' : tcgst,
                                'sgst' : tsgst,
                                'line_taxtot' : tltaxtot,
                                'cess_tot' : tcesstot,
                                

                                 }))    
                
            
         
        vals = {
                'start_date':self.start_date,             
                'end_date': self.end_date,
                'partner_id': self.partner_id.name,
                'company_id': self.company_id.name,
                'purchase_detail_line': purchase_detail_line,
                }
        purchase_wise_reports_id = self.env['purchase.detail.report.screen.wzd'].create(vals)

        res = self.env['ir.model.data'].check_object_reference(
                                            'ls_pos_reports', 'view_purchase_detail_wzd_report')
        return {
                    'name': 'Cashier Sales Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'purchase.detail.report.screen.wzd',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': purchase_wise_reports_id.id,
            }
       
       
class purchase_detail_screen_wzd(models.Model):
    _name = "purchase.detail.report.screen.wzd"
    _description = "Purchase Detail Reports"
    
    name = fields.Char(string="Name", default='Purchase Detail Report with GST')
    start_date = fields.Date(string="Date From")
    end_date = fields.Date(string="Date To")
    partner_id = fields.Char(string="Vendor")
    company_id = fields.Char(string="Company")
    purchase_detail_line = fields.One2many('purchase.detail.report.screen.line','purchase_order_id',string='Open Order Line')
    
    def print_purchase_excel_report(self):
        filename= 'Purchase Detail Report.xls'
        workbook= xlwt.Workbook(encoding="UTF-8")
        style_header = xlwt.easyxf('font: bold on; font:height 230; align: wrap No; borders: left thin, right thin, top thin, bottom thin;')
        style = xlwt.easyxf('font:height 230; align: wrap No;borders: left thin, right thin, top thin, bottom thin;')
        header=xlwt.easyxf('pattern: pattern solid, fore_colour light_orange;''font:height 400; align: horiz center;font:bold True;' "borders: top thin,bottom thin , left thin, right thin")
        style = xlwt.easyxf('font:height 230; align: wrap No;')
        base_style = xlwt.easyxf('align: wrap yes')
        date_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY')
        datetime_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY HH:mm:SS')
        sheet= workbook.add_sheet('Purchase Detail Report with GST')
        format6 = xlwt.easyxf('font:height 210,bold True;align: horiz left')
        
        format6 = xlwt.easyxf('font: bold off, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color yellow;')
        txt_v = xlwt.easyxf('font: bold off, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color white;')
        start_date = self.start_date or ''
        end_date = self.end_date  or ''
        partner_id = self.partner_id or ''
        company_id = self.company_id or ''
        

        sheet.col(0).width = 850*5
        sheet.col(1).width = 850*5
        sheet.col(2).width = 850*5
        sheet.col(3).width = 850*5
        sheet.col(4).width = 850*5
        sheet.col(5).width = 850*5
        sheet.col(6).width = 850*5
        sheet.col(7).width = 850*5
        sheet.col(8).width = 850*5
        sheet.col(9).width = 850*5
        sheet.col(10).width = 850*5    
        sheet.col(11).width = 850*5
        sheet.write(2, 0, 'GRN No', format6)
        sheet.write(2, 1, 'Bill No', format6)
        sheet.write(2, 2, 'Bill Date', format6)
        sheet.write(2, 3, 'GRN Date', format6)
        sheet.write(2, 4, 'Vendor', format6)
        sheet.write(2, 5, 'Warehouse', format6)
        sheet.write(2, 6, 'SubTotal', format6)
        sheet.write(2, 7, 'Tax Amount', format6)
        sheet.write(2, 8, 'CESS', format6)
        sheet.write(2, 9, 'Total Value', format6)
        sheet.write(2, 10, 'Add Ded', format6)
        sheet.write(2, 11, 'Tcs Amount', format6)
        sheet.write(2, 12, 'Net Amount', format6)
        sheet.write(2, 13, 'Freight Charges', format6)
        sheet.write(2, 14, 'Pcode', format6)
        sheet.write(2, 15, 'Product Name', format6)
        sheet.write(2, 16, 'Brand', format6)
        sheet.write(2, 17, 'Item Type', format6)
        sheet.write(2, 18, 'Product Design', format6)
        sheet.write(2, 19, 'Product Color', format6)
        sheet.write(2, 20, 'Product Size', format6)
        sheet.write(2, 21, 'Quantity', format6)
        sheet.write(2, 22, 'MRP', format6)
        sheet.write(2, 23, 'GKM', format6)
        sheet.write(2, 24, 'Selling Margin MRP', format6)
        sheet.write(2, 25, 'Mark Down', format6)
        sheet.write(2, 26, 'Different Margin', format6)
        sheet.write(2, 27, 'Different Amount', format6)
        sheet.write(2, 28, 'Landed Cost', format6)
        sheet.write(2, 29, 'Line SubTotal', format6)
        sheet.write(2, 30, 'Department', format6)
        sheet.write(2, 31, 'Category', format6)
        sheet.write(2, 32, 'Manufacturer', format6)
        sheet.write(2, 33, 'Tax', format6)
        sheet.write(2, 34, 'IGST', format6)
        sheet.write(2, 35, 'CGST', format6)
        sheet.write(2, 36, 'SGST', format6)
        sheet.write(2, 37, 'Line Taxtotal', format6)
        sheet.write(2, 38, 'CESS Total', format6)
        sheet.write(2, 39, 'Created', format6)
        sheet.write(2, 40, 'Reversal No', format6)
        sheet.write(2, 41, 'Reversed Date', format6)
        
        
        
                 
        sheet.write_merge(0, 1, 0, 10, 'Purchase Detail Report with GST',header)
           
               
        sql = '''  select grn_no,bill_no, to_char(bill_date,'dd/mm/yyyy'),to_char(grn_date,'dd/mm/yyyy'), partner_id, ware_house, sub_total,
        tax_amt,cess, total_val, add_ded, tcs_amt,net_amt,freight_charges, pcode, product_id,brand,item_type,
        prod_design,prod_color,prod_size,qty,mrp,gkm,sp_margin_mrp,
        m_down,diff_margin,diff_amt,lcost,line_subtot,dept,categ,manuftr,tax,igst,cgst,sgst,line_taxtot,
        cess_tot,created,reversal_no,reversed_date from purchase_detail_report_screen_line
                where purchase_order_id=(select max(purchase_order_id) from purchase_detail_report_screen_line)    
                
                
                     '''
           

           
        self.env.cr.execute(sql)
        rows2 = self.env.cr.fetchall()
        for row_index, row in enumerate(rows2):
            for cell_index, cell_value in enumerate(row):
                cell_style = txt_v 
                if isinstance(cell_value, str):
                    cell_value = re.sub("\r", " ", cell_value)
                elif isinstance(cell_value,float) :
                    cell_style =  txt_v    
                sheet.row(row_index+1).height = 70*5
                sheet.write(row_index + 3, cell_index, cell_value,txt_v)
                     
        fp =io.BytesIO()
        workbook.save(fp)
        export_id = self.env['excel.extended.purchase.detail.rep'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        
        fp.seek(0)
        data = fp.read()
        fp.close()

        return{
              'view_mode': 'form',
              'res_id': export_id.id,
              'res_model': 'excel.extended.purchase.detail.rep',
              'type': 'ir.actions.act_window',
              'context': False,
          
            }
        
purchase_detail_screen_wzd()
 
class purchase_detail_screen_line(models.Model):
    _name = "purchase.detail.report.screen.line"
    _description = "Open Orders summary Line"
    
    purchase_order_id = fields.Many2one('purchase.detail.report.screen.wzd',string='purchase_order_id',ondelete='cascade')
    grn_no = fields.Char(string="GRN No")
    bill_no = fields.Char(string="Bill No")
    bill_date = fields.Date(string="Bill Date")
    grn_date = fields.Date(string="GRN Date")
    partner_id = fields.Char(string="Vendor")
    ware_house = fields.Char(string="Warehouse")
    sub_total = fields.Float(string="SubTotal")
    tax_amt = fields.Float(string="Tax Amount")
    cess = fields.Float(string="CESS")
    total_val = fields.Float(string="Total Value")
    add_ded = fields.Float(string="Add Ded")
    tcs_amt = fields.Float(string="Tcs Amount")
    net_amt = fields.Float(string="Net Amount")
    freight_charges = fields.Float(string="Freight Charges")
    pcode = fields.Char(string="Pcode")
    product_id = fields.Char(string="Product Name")
    brand = fields.Char(string="Brand")
    item_type = fields.Char(string="Item Type")
    prod_design = fields.Char(string="Product Design")
    prod_color = fields.Char(string="Product Color")
    prod_size = fields.Char(string="Product Size")
    qty = fields.Float(string="Quantity")
    mrp = fields.Float(string="MRP")
    gkm = fields.Float(string="GKM")
    sp_margin_mrp = fields.Float(string="Selling Margin MRP")
    m_down = fields.Float(string="Mark Down")
    diff_margin = fields.Float(string="Different Margin")
    diff_amt = fields.Float(string="Different Amount")
    lcost = fields.Float(string="Landed Cost")
    line_subtot = fields.Float(string="Line SubTotal")
    dept = fields.Char(string="Department")
    categ = fields.Char(string="Category")
    manuftr = fields.Char(string="Manufacturer")
    tax = fields.Char(string="Tax")
    igst = fields.Float(string="IGST")
    cgst = fields.Float(string="CGST")
    sgst = fields.Float(string="SGST")
    line_taxtot = fields.Float(string="Line Taxtotal")
    cess_tot = fields.Float(string="CESS Total")
    created = fields.Char(string="Created")
    reversal_no = fields.Char(string="Reversal No")
    reversed_date = fields.Date(string="Reversed Date")
    
           
purchase_detail_screen_line()

     
class excel_extended_purchase_detail_rep(models.Model):
    _name= "excel.extended.purchase.detail.rep"

    name = fields.Char(string="Name", default='Download Excel Report')    
    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64) 
    
