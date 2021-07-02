from django.shortcuts import render
import pyodbc
from django.http import JsonResponse
import math
import random
import json

def get_connection():
    conn=pyodbc.connect('Driver={SQL Server};''Server=SVSP-SQL;''Database=CCS_Production;')
                        # 'UID=CCSGROUPS\sqladmin;'
                        # 'PWD=$ql@2019;'
                        # 'Trusted_Connection=yes;'
    return conn

def index(request):
    cursor = get_connection().cursor()
    cursor.execute("SELECT REPLACE(WorkCenterGroup, 'Machine', '') as WorkCenterGroup FROM M_Machine WHERE WorkCenterGroup NOT LIKE '%Man%' GROUP BY WorkCenterGroup")
    workcentergroup_list = cursor.fetchall()
    cursor.execute("SELECT * FROM M_Machine")
    machine_list = cursor.fetchall()
    context = {
        'workcentergroup_list' : workcentergroup_list,
        'machine_list' : machine_list,
    }
    return render(request, 'index.html', context)

def get_data(request):
    #-- REQUEST DATA FORM FRONT
    shift = request.GET.get('shift')
    x_count = int(request.GET.get('x_count'))
    type = request.GET.get('type')
    year = request.GET.get('year')
    month = request.GET.get('month')
    work_center_group = request.GET.get('work_center_group')
    work_center_group_count = request.GET.get('work_center_group_count')
    machine_no = request.GET.get('machine_no')
    machine_count = request.GET.get('machine_count')
    print(shift, x_count, type, year, month, work_center_group, work_center_group_count, machine_no, machine_count)
    #-- FETCH DATA FROM DATABASE
    cursor = get_connection().cursor()
    # cursor.execute("SELECT * FROM M_Machine")
    result = get_random_data(x_count, type, work_center_group, work_center_group_count, machine_no, machine_count)
    data = {
        'result' : result,
    }
    return JsonResponse(data)

def get_machine_list(request):
    #-- REQUEST DATA FORM FRONT
    work_center_group = request.GET.get('work_center_group')
    #-- FETCH DATA FROM DATABASE
    machine_list = []
    rows = []
    cursor = get_connection().cursor()
    if work_center_group == 'All Work Center Group':
        cursor.execute("SELECT MachineNumber, MachineName FROM M_Machine")
        rows = cursor.fetchall()
    else:
        cursor.execute("SELECT MachineNumber, MachineName FROM M_Machine WHERE WorkCenterGroup LIKE '%" + work_center_group + "%'")
        rows = cursor.fetchall()
    for row in rows:
        machine_list.append([x for x in row])
    data = {
        'machine_list' : machine_list,
    }
    return JsonResponse(data)

def get_random_data(x_count, type, work_center_group, work_center_group_count, machine_no, machine_count):
    result = []
    for i in range(x_count):
        coef = 1; # coefficient
        if(type == "Y"):
            coef = coef * 30;
        if(work_center_group == "All Work Center Group"):
            coef = coef * int(machine_count) * int(work_center_group_count)
        if(work_center_group != "All Work Center Group" and machine_no == "All Machine"):
            coef = coef * int(machine_count)
        result.append(math.floor(random.randint(0, 12) * coef))
    return result
