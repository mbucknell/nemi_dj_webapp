'''
Created on Mar 20, 2012

@author: mbucknel
'''
# Provides conversion to Excel format
from xlwt import Workbook

from django.http import HttpResponse

def dictfetchall(cursor):
    '''Returns all rows from the cursor query as a dictionary with the key value equal to column name in uppercase'''
    desc = cursor.description
    return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
            ]
    
def tsv_response(headings, vl_qs, filename):
    ''' Returns an http response which contains a tab-separate-values file 
    representing the values list query set, vl_qs, and using headings as the 
    column headers. filename will be the name of the file created with the suffix *.tsv
    '''
    response = HttpResponse(mimetype='text/tab-separated-values')
    response['Content-Disposition'] = ('attachment; filename=%s.tsv' % filename)

    response.write('\t'.join(headings))
    response.write('\n')

    for row in vl_qs:
        for col in row:
            response.write('%s\t' % str(col))
        response.write('\n')

    return response

def xls_response(headings, vl_qs, filename):
    '''Returns an http response which contains an Excel file
    representing the values list query set, vl_qs, and using headings
    as the column headers. filename will be the name of the file created with the suffix *.xls
    '''
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = ('attachment; filename=%s.xls' % filename)
    
    wb = Workbook()
    ws = wb.add_sheet('sheet 1')
    
    for col_i in range(len(headings)):
        ws.write(0, col_i, headings[col_i])
    
    for row_i in range(len(vl_qs)):
        for col_i in range(len(vl_qs[row_i])):
            ws.write(row_i + 1, col_i, vl_qs[row_i][col_i])
    
    wb.save(response)
    
    return response