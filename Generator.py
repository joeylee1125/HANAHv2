# -*- coding: UTF-8 -*-
# version 2 use database instead of csv.
import DBOperation

import StaticUtils
import VerdictAnalyserv3


def update_case_table(db_conn, case):
    fields_list = ['court_level', 'region', 'prosecutor', 'court_procedure', 'verdict']
    data_list = list()
    for f in fields_list:
        data_list.append(case[f])
    #print(fields_list, data_list)
    #fields_list.append('analysed')
    #data_list.append(5)
    db_conn.multi_update(StaticUtils.case_table,
                         fields_list,
                         data_list,
                         'doc_id=\'{}\' and name=\'{}\''.format(case['doc_id'],
                                                                 case['name']))

def update_defendant_table(db_conn, case):
    for index, defendant in enumerate(case['defendant']):
        fields_list = list()
        data_list = list()
        for k, v in defendant.items():
        # if value is none, do nothing, ignore this field.
            if v is not None:
                fields_list.append(k)
                data_list.append(v)
        #print(fields_list, data_list)
        defendant_id = case['doc_id'] + '{:0>2}'.format(index)
        #print(defendant_id, defendant['name'])
        defendant_doc_id = db_conn.get(StaticUtils.defendant_table, 'doc_id', 'doc_id=\'{}\''.format(case['doc_id']))
        if not defendant_doc_id:
            add_defendant(db_conn, case['doc_id'], defendant['name'], defendant_id)
        db_conn.multi_update(StaticUtils.defendant_table,
                             fields_list,
                             data_list,
                             'doc_id=\'{}\' and name=\'{}\''.format(case['doc_id'], defendant['name']))


def update_to_db(db_conn, case_list):
    for case in case_list:
        update_case_table(db_conn, case)
        update_defendant_table(db_conn, case)

def add_defendant(db_conn, case_doc_id, case_defendant_name, defendant_id):
    #INSERT INTO `sichuan_cases`.`defendent_list` (`doc_id`, `name`) VALUES ('0002099c-c066-4f99-a119-a850009ef04b', 'test');
    db_conn.insert(StaticUtils.defendant_table, ('`doc_id`, `name`,`defendant_id`'), (case_doc_id, case_defendant_name, defendant_id))


def analyse_case(db_conn):
    case_list_out = list()
    case_list = db_conn.get(StaticUtils.case_table, 'name, doc_id, court, YEAR(DATE), content', 'YEAR(DATE)=2015 and analysed is null', rows=2000)
    #print(case_list)
    #case_list = db_conn.get(StaticUtils.case_table, 'name, doc_id, court, YEAR(DATE), content',
    #                        'doc_id=\'83801051-e508-462b-9602-a8ff00a65e95\'')
    #for case_name, case_doc_id, case_court, case_year, case_content in case_list:
    for case_info in case_list:
        case = dict()
        case['name'], case['doc_id'], case['court'], case['year'], case['content'] = case_info
        #if not case['content'] or len(case['content']) < 100 or "附带民事" in case['content']:
        if not case['content'] or len(case['content']) < 100 :
            db_conn.update(StaticUtils.case_table, 'analysed', -1, 'doc_id=\'{}\''.format(case['doc_id']))
#            print(case['doc_id'])
            continue
        verdict = VerdictAnalyserv3.VerdictAnalyser(case['content'], case['year'])
        # collect data for case table
        case['court_level'] = verdict.get_court_level(case['court'])
        case['region'] = verdict.get_region(case['court'])
        case['prosecutor'] = verdict.get_prosecutor()
        case['court_procedure'] = verdict.get_procedure()
        case['verdict'] = verdict.get_verdict_name()

        # collect data for defendant table
        try:
            defendant_info_list, defendant_name_list = verdict.get_defendant_name_list(
                verdict.get_defendant_info_list())
        except Exception as e:
            print(e)
        if not defendant_name_list:
            db_conn.update(StaticUtils.case_table, 'analysed', 0, 'doc_id=\'{}\''.format(case['doc_id']))
            continue
        else:
            db_conn.update(StaticUtils.case_table, 'analysed', len(defendant_name_list), 'doc_id=\'{}\''.format(case['doc_id']))
        case['defendant'] = []
        convict_info = verdict.get_defendant_convict_info(defendant_name_list)
        for i in range(len(defendant_name_list)):
            lawyer_list = verdict.get_defendant_lawyer(defendant_info_list[i])
            s_lawyer_list = verdict.get_defendant_s_lawyer(defendant_info_list[i])
            case['defendant'].append(dict())
            case['defendant'][i]['name'] = defendant_name_list[i]
            case['defendant'][i]['nation'] = verdict.get_defendant_nation(defendant_info_list[i])
            case['defendant'][i]['age'] = verdict.get_defendant_age(defendant_info_list[i])
            case['defendant'][i]['education'] = verdict.get_defendant_education(defendant_info_list[i])
            case['defendant'][i]['job'] = verdict.get_defendant_job(defendant_info_list[i])
            case['defendant'][i]['charge'] = verdict.get_defendant_charge(defendant_name_list[i], convict_info)
            case['defendant'][i]['charge_c'] = verdict.get_charge_class(case['defendant'][i]['charge'])
            case['defendant'][i]['prison'] = verdict.get_defendant_prison(defendant_name_list[i], convict_info)
            case['defendant'][i]['prison_l'] = verdict.get_prison_len(case['defendant'][i]['prison'])
            case['defendant'][i]['probation'] = verdict.get_defendant_probation(defendant_name_list[i], convict_info)
            case['defendant'][i]['probation_l'] = verdict.get_prison_len(case['defendant'][i]['probation'])
            case['defendant'][i]['fine'] = verdict.get_defendant_fine(defendant_name_list[i], convict_info)
            case['defendant'][i]['lawyer_n'] = len(lawyer_list) if lawyer_list else None
            case['defendant'][i]['s_lawyer_n'] = len(s_lawyer_list) if s_lawyer_list else None
            case['defendant'][i]['has_lawyer'] = 'yes' if case['defendant'][i]['lawyer_n'] or case['defendant'][i]['s_lawyer_n'] else 'no'
        case_list_out.append(case)
    return case_list_out

def main():
    db_sc_cases = DBOperation.MyDatabase('127.0.0.1', 'root', '082666')
    cases = analyse_case(db_sc_cases)
    update_to_db(db_sc_cases, cases)
    db_sc_cases.commit()
    db_sc_cases.close()

if __name__ == "__main__":
    main()
