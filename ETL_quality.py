import traceback
import types
import pandas as pd
import numpy as np
import xlsxwriter
import time
import  os
from numpy import int64
from google.cloud import bigquery
from deep_translator import GoogleTranslator, PapagoTranslator, BaiduTranslator
import openai



###EXTRACT###

#***Loading and Reading data from multiple files***

class Data_Load:
    def __init__(self, responsedata_path, reportdata_path ):   # initiating path for reading and loading to a consolidated file
        try:

            self.responsedata_df = []
            self.reportdata_df = []
            for i in os.listdir(responsedata_path):  # read files based on csv or xlsx extension
                if str(i).endswith('.csv'):
                    self.responsefile_path = os.path.join(str(responsedata_path), i)
                    self.response_file = pd.read_csv(self.responsefile_path)
                    self.responsedata_df.append(self.response_file)
                    print(f'filename- {i}: file_shape - {self.response_file.shape}')

                elif str(i).endswith('.xlsx'):
                    self.responsefile_path = os.path.join(str(responsedata_path), i)
                    self.response_file = pd.read_excel(self.responsefile_path)
                    self.responsedata_df.append(self.response_file)
                    print(f'filename- {i}: file_shape - {self.response_file.shape}')

                #else:
                    #print('No "xlsx" or "csv" files found for response data')

            for i_next in os.listdir(reportdata_path):
                if str(i_next).endswith('xlsx'):
                    self.report_path = os.path.join(str(reportdata_path),i_next)
                    self.report_file = pd.read_excel(self.report_path, low_memory = False, index_col= False)
                    print(f'filename- {i_next}: file_shape - {self.report_file.shape}')
                    self.reportdata_df.append(self.report_file)
                elif str(i_next).endswith('csv'):
                    self.report_path = os.path.join(str(reportdata_path), i_next)
                    self.report_file = pd.read_csv(self.report_path, low_memory= False, skiprows= 14, index_col= False)
                    self.reportdata_df.append(self.report_file)
                    print(f'filename- {i_next}: file_shape - {self.report_file.shape}')

                else:
                    print('No "xlsx" or "csv" files found for report data(edge)')

            self.load_file()






        except FileNotFoundError as fe:
            print('Error with data file: ',fe)
            traceback.print_exc()
        except BaseException as be :
            print('An error occurred :', be)
            traceback.print_exc()

    def load_query(self):
        client = bigquery.client.Client(project='my-pipeline-prokject')
        print('Bigquery loaded\n')
        print()

    def load_file(self):
        try:
            response_output_path = r"C:\Users\prabi\OneDrive\Desktop\my__pipeline project\Files for output only\test_rrsponse_output.xlsx"
            report_output_path = r"C:\Users\prabi\OneDrive\Desktop\my__pipeline project\Files for output only\test_report_output.xlsx"
            main_file_path = r"C:\Users\prabi\OneDrive\Desktop\my__pipeline project\Files for output only\test_main_output.xlsx"

            self.response_main_file = pd.concat(self.responsedata_df)  # concatenate all respondent data files in one
            self.report_main_file = pd.concat(self.reportdata_df)  # concatenate all project report data in one
            print('\nBELOW ARE DIMENSIONS OF DATA FILES')

            print('response_main_file shape', self.response_main_file.shape)
            print('report_main_file shape', self.report_main_file.shape)

            self.main_file = pd.merge(self.response_main_file, self.report_main_file[['Token','Verified Token']],
                                       on = 'Token', how= 'right')

            print('main_file shape:', self.main_file.shape)

            #for column in self.main_file.columns:
               # print(f"column - {column} : type - {self.main_file[column].dtype}\n")


            response_output_check = pd.DataFrame(self.response_main_file)
            report_output_check = pd.DataFrame(self.report_main_file)
            '''with pd.ExcelWriter(response_output_path, engine='xlsxwriter') as w:
                response_output_check.to_excel(w)
            print('\nUser can take a look in response data consolidated excel\n')

            with pd.ExcelWriter(report_output_path, engine='xlsxwriter') as w:
                report_output_check.to_excel(w)
            print('\nUser can take a look in report data consolidated excel\n')

            with pd.ExcelWriter(main_file_path, engine='xlsxwriter') as w:
                self.main_file.to_excel(w)
            print('\nUser can take a look in report data consolidated excel\n')'''

            print('Shape of response consolidated file :', self.response_main_file.shape)
            print('Shape of project report consolidated file :', self.report_main_file.shape)


        except FileNotFoundError as fe:
            print('Error in load data : ', fe)
            traceback.print_exc()
        except BaseException as be:
            print('An error in load data, ', be)
            traceback.print_exc()







                                                                      ###TRANSFORM###

#***Clean***

#Look for empty columns

class Data_Check(Data_Load):



    def loaddata_to_query(self):
        try:
            client = bigquery.Client(project='my-pipeline-prokject')
            table_id = 'my-pipeline-prokject.etl_dataset.converted_file'
            job = client.load_table_from_dataframe(self.main_file_converted, table_id,
                                                   job_config=bigquery.LoadJobConfig(
                                                       write_disposition='WRITE_TRUNCATE'))

            job.result()

            print(f'Job loaded in biq query with {len(self.main_file_converted)} rows')

        except BaseException as be:
            print('An error occurred while loading to bigQuery', be)


    def gender_translate(self):

        translate = GoogleTranslator()

        gender_dict = {}
        unique_gender = self.main_file_converted['GENDER'].dropna().unique()
        for gender in unique_gender:
            original = str(gender)
            lower_gender = str(gender).lower()
            translator = GoogleTranslator(source= 'auto', target = 'en')
            translated_gender = translator.translate(lower_gender)


            if any(word in translated_gender for word in ['woman', 'feminine', 'donna'] ):
                translated_gender = 'female'
            elif any(word in translated_gender for word in ['man', 'masculine']):
                translated_gender = 'male'
            elif any(word in translated_gender for word in ['prefer', 'not', 'answer']):
                translated_gender = 'prefer not to answer'
    

            gender_dict[original]= translated_gender.capitalize()





        self.main_file_converted['GENDER'] =   self.main_file_converted['GENDER'].map(gender_dict )







    '''self.main_file['GENDER'] = self.main_file['GENDER'].apply(lambda x : translator.translate(str(x)) if pd.notna(x) else x )

       with pd.ExcelWriter(main_file_path, engine='xlsxwriter') as w:
           self.main_file_converted.to_excel(w)
       print('\nUser can take a look in report data consolidated excel\n')
       print('Gender translations converted')'''





    def empty_column(self):
        try:
            self.empty_columns = []
            self.ignore_columns = []
            for i in self.main_file.columns:

                if self.main_file[i].isna().all():  # if any empty column
                    self.empty_columns.append([i])
                elif self.main_file[i].isna().any():  # if any empty cell in a column
                    self.ignore_columns.append([i])

            if self.empty_columns:
                self.main_file.drop(self.main_file[self.empty_columns], inplace= True)  # remove empty columns, if any
                print('\nEmpty columns are below and removed :\n', self.empty_columns)
            elif self.ignore_columns:
                print('\nBelow columns are with empty cells(some blank cells in a column)\n')
                print(self.ignore_columns, '\n')
            else:
                print('\nNo empty columns found\n')

        except IndexError as ie:
            print('An error occurred : ',ie)
            traceback.print_exc()

        except BaseException as be:
            print('An error occurred : ',be)
            traceback.print_exc()





    def column_check(self): # function to convert any numeric entered as text in excel and rest is untouched

        try:
            mixed_cols = []
            main_cols = []
            for column in self.main_file_converted.columns:
                if self.main_file_converted[column].dtype == object:
                    converted = pd.to_numeric(self.main_file_converted[column], errors='coerce')
                    numeric_count = converted.notna().sum()
                    if numeric_count > 0:
                        print(
                            f'Mixed type column "{column}" found with {numeric_count} numeric rows including blank cells')
                        mixed_cols.append(column)

            print(f'Mixed columns are {mixed_cols}\n')
            return mixed_cols
        except BaseException as be:
            print('An error occurred : ', be)
            traceback.print_exc()




    def cells_check(self,cols,mix_cols):  #2 arguements to pass in for cols which has similar type(integer) and mix col for those which...
                                           #...converted for columns with integers saved as text


        try:
            # checking first for blank cells and then if any numeric entered as text in numeric type columns and convert as necessary
            self.col_dtype = self.main_file_converted[cols].dtype
            print(f"Columns : {cols} - type is {self.col_dtype}")
            if pd.api.types.is_numeric_dtype(self.main_file_converted[cols]):  # checking for blank cells and nan values
                self.main_file[cols] = pd.to_numeric(self.main_file[cols], errors='coerce')
                # print(f'{cols} is a numeric columns')


            elif cols in mix_cols:
                self.main_file_converted[cols] = self.main_file_converted[cols].apply(lambda x: pd.to_numeric(x, errors='ignore'))
                print(f'{cols} is a mixed column converted(for integers might have entered as text)')

        except BaseException as be:
            print('An error occurred : ', be)
            traceback.print_exc()


    def missing_handle(self):   # to keep blanl cells as 'unknown' so missing cells are handled.
        try:
            for cols in self.main_file_converted.columns:
                nan_count = self.main_file_converted[cols].isna().sum()
                print(f'{nan_count} blank cells in {cols}')

                if nan_count > 0:
                    if pd.api.types.is_numeric_dtype(self.main_file_converted[cols]):
                        print(f'{cols} — {nan_count} NaN kept as NaN (numeric column)')
                    else:
                        self.main_file_converted[cols].fillna('Unknown', inplace= True)  # this is where we are finding if any plank cells and can replace with unkmnowbn
                        print(f'Blank cells in "{cols}" column filled to "Unknown"')



        except BaseException as be:
            print('An error occurred : ', be)
            traceback.print_exc()

    def bad_cells(self):

        try:

            self.main_file_converted = self.main_file.copy()
            self.empty_column()
            self.missing_handle()
            self.gender_translate()
            mix_cols = self.column_check()




            for cols in self.main_file_converted.columns:
                self.cells_check(cols, mix_cols)

            for cols in self.main_file_converted.columns:
                col_dtype = self.main_file_converted[cols].dtype
                ntype_count = {}
                self.column_len = self.main_file_converted[cols].notna().sum()

                print(f'"{cols}" column type is {col_dtype}')
                print(f'Length of {cols} is {self.column_len} without blank cells')
                # cells_typecount = sum(isinstance(cells, (np.float64, np.int64)) for cells in self.main_file[cols])

                ntype_cells = {}
                for cells in self.main_file_converted[cols]:
                    if not pd.isna(cells):
                        cells_type = type(cells)

                        if cells_type not in ntype_cells:
                            ntype_cells[cells_type] = 0
                        ntype_cells[cells_type] += 1

                for key, value in ntype_cells.items():
                    print(f'{key}:{value}')

                max_key = max(ntype_cells, key=ntype_cells.get)
                print(f'Dominant type in column {cols} is : {max_key.__name__}')


                if max_key in (int, int64, np.int64, np.float64, float):
                    self.main_file_converted[cols] = pd.to_numeric(self.main_file_converted[cols], errors='coerce')
                    print(f'"{cols}" column type updated to {self.main_file_converted[cols].dtype}\n')
                else:
                    self.main_file_converted[cols] = self.main_file_converted[cols].astype(str)
                    print(f'"{cols}" column type remains {self.main_file_converted[cols].dtype}\n')

            self.load_query()
            print()
            self.loaddata_to_query()




        except BaseException as be:
            print('An error occurred : ', be)
            traceback.print_exc()















response_path = r'C:\Users\prabi\OneDrive\Desktop\my__pipeline project'
report_path = r"C:\Users\prabi\OneDrive\Desktop\my__pipeline project\edge_status file"

test = Data_Check(response_path,report_path)
test.bad_cells()
