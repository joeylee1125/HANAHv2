# -*- coding: UTF-8 -*-
import datetime
import time
import Spider
import DBOperation
import StaticUtils
import VerdictAnalyser

CASE_TABLE = StaticUtils.case_table


def get_total_number(search_criteria):
    wenshu = Spider.WenShu()
    wenshu.set_search_criteria(search_criteria)
    return wenshu.get_total_item_number()


def download_all_caselist(search_criteria, max_page):
    cases = dict()
    wenshu = Spider.WenShu()
    wenshu.set_search_criteria(search_criteria)
    for index in range(1, max_page + 1):
        tmp_case_list = wenshu.get_case_list(index)
        if not cases:
            cases = tmp_case_list
        else:
            for key, value in tmp_case_list.items():
                cases[key] += value
    print(f"{cases}")
    return cases


def download_case(case_id):
    w = Spider.WenShu()
    return w.get_case(case_id)


def download_case_list_by_upload_date(year, upload_date):
        search_criteria = "案件类型:刑事案件,审判程序:一审,法院地域:四川省,裁判年份:" + year + ",文书类型:判决书,上传日期:" + upload_date + " TO " + upload_date
        total_number = get_total_number(search_criteria)
        if int(total_number) == 0:
            return None
        max_page = int(total_number) // 20 if int(total_number) % 20 == 0 else (int(total_number) // 20) + 1
        cases = download_all_caselist(search_criteria, max_page)
        db_sc_cases = DBOperation.MyDatabase('127.0.0.1', 'root', '082666')
        length = len(cases['name'])
        for i in range(length):
            data = dict()
            for key in cases:
                if key == 'procedure':
                    data['trial'] = cases[key][i]
                else:
                    data[key] = cases[key][i]
                data['download'] = 'no'
                data['upload_date'] = upload_date
            doc_id = db_sc_cases.get(StaticUtils.case_table, 'doc_id', 'doc_id=\'{}\''.format(data['doc_id']))
            if not doc_id:
                fields_list = ["name", "doc_id", "date", "case_id", "trial", "court", "download", "upload_date"]
                values = ''
                for key in fields_list:
                    #transfer to str if it's a int
                    if isinstance(data[key], int):
                        values = values + str(data[key])
                    else:
                        if values:
                            values = values +",\'" + data[key] + "\'"
                        else:
                            values = "(\'" + data[key] + "\'"
                values = values + ")"
                fields = ','.join(fields_list)
                db_sc_cases.insert(CASE_TABLE, fields, values)
        db_sc_cases.commit()
        db_sc_cases.close()


def download_case_list_by_upload_period(year, start_date, end_date):
    search_criteria = "案件类型:刑事案件,审判程序:一审,法院地域:四川省,裁判年份:{},文书类型:判决书,上传日期:{} TO {}".format(year, start_date, end_date)
    total_number = get_total_number(search_criteria)
    if int(total_number) == 0:
        return None
    max_page = int(total_number) // 20 if int(total_number) % 20 == 0 else (int(total_number) // 20) + 1
    cases = download_all_caselist(search_criteria, max_page)
    db_sc_cases = DBOperation.MyDatabase('127.0.0.1', 'root', '082666')
    length = len(cases['name'])
    for i in range(length):
        data = dict()
        for key in cases:
            if key == 'procedure':
                data['trial'] = cases[key][i]
            else:
                data[key] = cases[key][i]
            data['download'] = 'no'
            data['upload_date'] = start_date
        doc_id = db_sc_cases.get(StaticUtils.case_table, 'doc_id', 'doc_id=\'{}\''.format(data['doc_id']))
        if not doc_id:
            fields_list = ["name", "doc_id", "date", "case_id", "trial", "court", "download", "upload_date"]
            values = ''
            for key in fields_list:
                # transfer to str if it's a int
                if isinstance(data[key], int):
                    values = values + str(data[key])
                else:
                    if values:
                        values = values + ",\'" + data[key] + "\'"
                    else:
                        values = "(\'" + data[key] + "\'"
            values = values + ")"
            fields = ','.join(fields_list)
            db_sc_cases.insert(CASE_TABLE, fields, values)
            # db_sc_cases.insert(StaticUtils.case_table, data)
    db_sc_cases.commit()
    db_sc_cases.close()


def download_new_testcases():
    db_sc_cases = DBOperation.MyDatabase('127.0.0.1', 'root', '082666')
    case_list = db_sc_cases.get(StaticUtils.case_table, 'name, doc_id, court, YEAR(DATE)', 'download=\'no\'')
    total = len(case_list)
    i = 0
    for case in case_list:
        case_name, case_doc_id, case_court, case_year = case
        print(case_name, case_doc_id, case_court, case_year)
        try:
            case_text = download_case(case_doc_id)
        except Exception as e:
            print(e)
            db_sc_cases.commit()
        print("Sleep 2s ...")
        time.sleep(2)
        if case_text:
            verdict = VerdictAnalyser.VerdictAnalyser(case_text)
            print(f"{i}/{total} case {case_name} is downloaded.")
            db_sc_cases.update(StaticUtils.case_table,
                               'download', '\'yes\'',
                               f'doc_id=\'{case_doc_id}\'')
            db_sc_cases.update(StaticUtils.case_table,
                               'content', f'\'{verdict.content}\'',
                               f'doc_id=\'{case_doc_id}\'')
            db_sc_cases.commit()
        else:
            db_sc_cases.update(StaticUtils.case_table, 'download', '\'empty\'', f'doc_id=\'{case_doc_id}\'')
            print(f"{i}/{total} case {case_name} is empty.")
        i += 1
    db_sc_cases.commit()
    db_sc_cases.close()


def main():
    #download_new_testcases()
    #return None

    years = ['2016', '2017', '2018']

    start = '2018-07-03'
    end = '2018-07-16'
    date_start = datetime.datetime.strptime(start, '%Y-%m-%d')
    date_end = datetime.datetime.strptime(end, '%Y-%m-%d')
    while date_start < date_end:
        print(f"Download case uploaded by "
              f"=================={date_start.year}-{date_start.month}-{date_start.day}=====================")
        for year in years:
            upload_date = f'{date_start.year}' + '-' + f'{date_start.month:02d}' + '-' + f'{date_start.day:02d}'
            download_case_list_by_upload_date(year, upload_date)
        #download_new_testcases()
        date_start += datetime.timedelta(days=1)


if __name__ == "__main__":
    main()
