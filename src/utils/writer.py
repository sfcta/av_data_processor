'''
author: Drew Cooper
date: January 7, 2020
description: some stuff you can do with pandas DataFrames
'''
def as_percent(df, cols=None, axis=None):
    if not cols:
        cols = df.columns.tolist()
    d = df.loc[:,cols].copy()
    if axis==None:
        s = d.sum().sum()
        return d/s
    else:
        s = d.loc[:,cols].sum(axis)
        if axis==1:
            for c in cols:
                d[c] = d[c] / s
        elif axis==0:
            for c in cols:
                d[c] = d[c] / s[c]
    return d

def write_to_excel(template_path, output_path, table_data):
    """
    Populate tables in an Excel template based on table titles in the Excel sheet.

    Parameters:
        template_path (str): Path to the Excel template.
        output_path (str): Path to save the updated Excel file.
        table_data (dict): Dictionary where keys are table titles in the Excel template
                           and values are Pandas DataFrames to populate the tables.
    """
    # Load the Excel template
    wb = load_workbook(template_path)
    ws = wb.active  # Assuming all tables are in the active sheet

    for table_title, df in table_data.items():
        # Locate the table title in the Excel template
        title_row, title_col = None, None
        for row in ws.iter_rows():
            for cell in row:
                if cell.value == table_title:  # Match the table title
                    title_row, title_col = cell.row, cell.column
                    break
            if title_row:
                break

        if not title_row or not title_col:
            print(f"Table title '{table_title}' not found in template!")
            continue

        # Write the DataFrame to the table below the title
        start_row = title_row + 2 
        start_col = title_col

        merged_cell_offset = 1
        while isinstance(ws.cell(row=start_row, column=start_col+merged_cell_offset), MergedCell):
            merged_cell_offset += 1

        # Write DataFrame row index
        for i, idx in enumerate(df.index):
            ws.cell(row=start_row + i, column=start_col, value=idx)

        # Write DataFrame columns and values
        for i, (idx, row) in enumerate(df.iterrows()):
            for j, value in enumerate(row):
                ws.cell(row=start_row + i, column=start_col + j + merged_cell_offset, value=value)

    # Save the updated Excel file
    wb.save(output_path)
    print(f"Data written successfully to {output_path}")


def df_to_excel(writer, sheet_name, df, table_name, 
                startrow, startcol, 
                row_buffer=2, col_buffer=2,
                home_row=0, home_col=0,
                offset_rows=False, offset_cols=False,
                reset_rows=False, reset_cols=False,
                index=True
                ):
    
    workbook = writer.book
    title_fmt = workbook.add_format({'bold':True,'italic':True})
    firstrow_fmt = workbook.add_format({'bottom':2,'top':1,'bold':True})
    oddrows_fmt = workbook.add_format({'bottom':0,'top':0})
    evenrows_fmt = workbook.add_format({'bottom':0,'top':0}) 
    lastrow_fmt = workbook.add_format({'bottom':2})
    firstcol_fmt = workbook.add_format({'right':1})
    
    # write the df first, at startrow +1, in case the sheet doesn't exist yet
    df.to_excel(writer, sheet_name=sheet_name, startrow=startrow+1, startcol=startcol, index=index)

    # then go back and write the title
    worksheet = writer.sheets[sheet_name]
    #worksheet.conditional_format(startrow+1,startcol,startrow+1,startcol+len(df.columns)-1,
    #                             {'type': 'cell', 'criteria':'>=', 'value':0, 'format': firstrow_fmt})
    #worksheet.conditional_format(startrow+2,startcol,startrow+len(df),startcol+len(df.columns)-1,
    #                             {'type': 'cell', 'criteria':'>=', 'value':0, 'format': oddrows_fmt})
    #worksheet.conditional_format(startrow+len(df)+1,startcol,startrow+1,startcol+len(df.columns)-1,
    #                             {'type': 'cell', 'criteria':'>=', 'value':0, 'format': lastrow_fmt})
    worksheet.write(startrow, startcol, table_name, title_fmt)
    
    if reset_rows:
        startrow = home_row
    elif offset_rows:
        startrow = startrow + len(df) + 2 + row_buffer
    if reset_cols:
        startcol = home_col
    elif offset_cols:
        startcol = startcol + len(df.columns) + 2 + col_buffer
    

    return startrow, startcol
    
#def set_range_styles