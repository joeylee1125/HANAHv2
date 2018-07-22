# -*- coding: UTF-8 -*-
import MySQLdb
import StaticUtils
import FileOperations

DATABASE = "sichuan_cases"

class MyDatabase:
    def __init__(self, host_address, username, password):
        self.conn = MySQLdb.connect(host=host_address, user=username, password=password, charset="utf8")

    def create_table(self, table, fields):
        sql_cmd = "CREATE TABLE IF NOT EXISTS {}.{} ({})".format(DATABASE, table, fields)
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_cmd)
            cursor.close()
        except Exception as e:
            print(e)

    def add_column(self, table, column, pre_column):
        # insert column after pre_column
        sql_cmd = "ALTER TABLE {}.{} ADD COLUMN {} TEXT NULL AFTER {};".format(DATABASE, table, column, pre_column)
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_cmd)
            cursor.close()
        except Exception as e:
            print(e)

    def get_max_record(self, table, column):
        sql_cmd = f'SELECT max({column}) from {DATABASE}.{table}'
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_cmd)
        except Exception as e:
            print(e)
        results = cursor.fetchone()
        return results

    def generate_new_table(self):
        sql_cmd = f'SELECT doc_id from {DATABASE}.all_in_one'
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_cmd)
        except Exception as e:
            print(e)
        results = cursor.fetchall()
        i = 1
        for doc_id in results:
            sql_cmd = f'SELECT year(DATE) FROM {DATABASE}.case_list where doc_id=\'{doc_id[0]}\''
            cursor.execute(sql_cmd)
            d = cursor.fetchone()
            sql_cmd = f'UPDATE {DATABASE}.all_in_one SET year = \'{d[0]}\' where doc_id=\'{doc_id[0]}\''
            cursor.execute(sql_cmd)
            i += 1
            print(i)
        cursor.close()
        return None
        sql_cmd = f'UPDATE {DATABASE}.all_in_one SET \'year\' = {r}'
        print(sql_cmd)
        cursor.execute(sql_cmd)
        sql_cmd = f'UPDATE {DATABASE}.all_in_one SET {fields[index]} = {item}'
        cursor.execute(sql_cmd)
        cursor.close()
        return None

        cursor.close()
        return field_list
        fields = ",".join(f for f in self.get_fields(table1))
        print(fields)
        return None
        #sql_cmd = f'SELECT {fields} from {DATABASE}.{table}'
        if criteria:
            sql_cmd = f'{sql_cmd} WHERE {criteria}'
        if rows:
            sql_cmd = f'{sql_cmd} LIMIT {rows}'
        # print(sql_cmd)
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_cmd)
        except Exception as e:
            print(e)
        results = cursor.fetchall()

    def _get_field_list(self, table):
        if table ==  'caselist':
            return ["name", "doc_id", "date", "case_id", "trial", "court","download","upload_date"]
        elif table == 'test_table':
            return ['id', 'name', 'begin_date', 'end_date']


    def update(self, table, fields, data, criteria):
        #print(fields,data,criteria)
        sql_cmd = 'UPDATE {}.{} SET {} = {} WHERE {}'.format(DATABASE,table,fields, data, criteria)
        #print(sql_cmd)
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_cmd)
            cursor.close()
        except Exception as e:
            print(e)

    def multi_update(self, table, fields_list, data_list, criteria=None):
        if len(fields_list) != len(data_list):
            print("fields number and data number is not match.")
            return None
        content = ''
        for index, fields in enumerate(fields_list):
            # if not the first column, add a ',' as a separator.
            if content:
                content = content + ','
            content = content + '{}=\'{}\''.format(fields_list[index], data_list[index])
        if criteria:
            sql_cmd = 'UPDATE {}.{} SET {} WHERE {}'.format(DATABASE, table, content, criteria)
        else:
            sql_cmd = 'UPDATE {}.{} SET {}'.format(DATABASE, table, content)
        #print(sql_cmd)
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_cmd)
            cursor.close()
        except Exception as e:
            print(e)

    def get_all(self, table):
        sql_cmd = f'SELECT * from {DATABASE}.{table}'
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_cmd)
        except Exception as e:
            print(e)
        results = cursor.fetchall()
        cursor.close()
        return results

    def get(self, table, fields, criteria=None, rows=None):
        sql_cmd = f'SELECT {fields} from {DATABASE}.{table}'
        if criteria:
            sql_cmd = f'{sql_cmd} WHERE {criteria}'
        if rows:
            sql_cmd = f'{sql_cmd} LIMIT {rows}'
        #print(sql_cmd)
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_cmd)
        except Exception as e:
            print(e)
        results = cursor.fetchall()
        cursor.close()
        return results

    def delete_row(self, table, criteria):
        sql_cmd = 'DELETE FROM {}.{} WHERE {};'.format(DATABASE, table, criteria)
        print(sql_cmd)
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_cmd)
        except Exception as e:
            print(e)

    def insert(self, table, fields, values):
        sql_cmd = "INSERT INTO `{}`.`{}` ({}) VALUES {};".format(DATABASE, table, fields, values)
        #print(sql_cmd)

        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_cmd)
            cursor.close()
        except Exception as e:
            print(e)

#   def insert(self, table, data):
#       print(data)
#       fields_list = self._get_field_list(table)
#       values = ''
#       for key in fields_list:
#           if isinstance(data[key], int):
#               values = values + str(data[key])
#           else:
#               if values:
#                   values = values +",\'" + data[key] + "\'"
#               else:
#                   values = "\'" + data[key] + "\'"
#       fields = ','.join(fields_list)
#       sql_cmd = "INSERT INTO {}.{} ({}) VALUES ({})".format(DATABASE, table, fields, values)
#       print(sql_cmd)
#       try:
#           cursor = self.conn.cursor()
#           cursor.execute(sql_cmd)
#           cursor.close()
#       except Exception as e:
#           print(e)

    def add_column(self):
        pass

    def get_fields(self, table):
        sql_cmd = f'SELECT * from {DATABASE}.{table} LIMIT 10'
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_cmd)
        except Exception as e:
            print(e)
        field_list = [ i[0] for i in cursor.description ]
        cursor.close()
        return field_list

    def count(self, table):
        sql_cmd = f'SELECT doc_id from {DATABASE}.{table} WHERE analysed=0'
        #print(sql_cmd)
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_cmd)
        except Exception as e:
            print(e)
        cursor.fetchall()
        results = int(cursor.rowcount)
        cursor.close()
        return results

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

def main():
    db = MyDatabase('127.0.0.1', 'root', '082666')
    dl = list()
    fields = db.get_fields('defendant_list_2015')
    result = db.get_all('defendant_list_2015')
    db.close()
    for record in result:
        defendant = dict()
        for index, item in enumerate(record):
            defendant[fields[index]] = item
           # print(defendant)
        dl.append(defendant)
    print(dl)
    FileOperations.MyCsvFile('C:\\Users\\lij37\\Cases\\DBExport\\2015.csv').write_dict(fields, dl)
    return None
    database_name = 'sichuan_cases'
    table_name = 'case_list'
    print(d.count(table_name))
    defendant_list = db_conn.get
    case_list = db_conn.get(StaticUtils.case_table, 'name, doc_id, court, YEAR(DATE), content',
                            'YEAR(DATE)=2015 and analysed is null', rows=2000)

    #data = ['基层','资阳','四川省安岳县人民检察院','简易程序','四川省安岳县人民法院刑事判决书']
    #fields = ['court_level', 'region', 'prosecutor', 'court_procedure', 'verdict']
    #d.multi_update(table_name, fields, data, 'doc_id=\'{}\''.format('00026964-5c2c-4958-ba28-8b68413c0937'))
    #d.commit()
    d.close()

    # Get fields from


if __name__ == "__main__":
    main()