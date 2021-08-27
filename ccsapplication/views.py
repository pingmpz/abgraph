from django.shortcuts import render
import pyodbc
from .models import WorkCenterGroup, Machine, Transaction
from django.http import JsonResponse
import math
import random
import json
import threading
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import sys

def index(request):
    workcentergroup_list = WorkCenterGroup.objects.all()
    wcg = WorkCenterGroup.objects.get(name='BTA')
    machine_list = Machine.objects.filter(wcg=wcg)
    context = {
        'workcentergroup_list' : workcentergroup_list,
        'machine_list' : machine_list,
    }
    return render(request, 'index.html', context)

def index0(request):
    workcentergroup_list = WorkCenterGroup.objects.all()
    wcgs = WorkCenterGroup.objects.all().order_by('name')
    first_wcg_name = wcgs[0].name
    wcg = WorkCenterGroup.objects.get(name=first_wcg_name)
    machine_list = Machine.objects.filter(wcg=wcg)
    context = {
        'workcentergroup_list' : workcentergroup_list,
        'machine_list' : machine_list,
    }
    return render(request, 'index0.html', context)

def get_data(request):
    #-- REQUEST DATA FORM FRONT
    shift = request.GET.get('shift')
    x_count = int(request.GET.get('x_count'))
    type = request.GET.get('type')
    year = request.GET.get('year')
    month = request.GET.get('month')
    work_center_group_id = request.GET.get('work_center_group_id')
    machine_no = request.GET.get('machine_no')
    data_error = request.GET.get('data_error')
    print("------------------------------------------")
    print("INCLUDE ERROR DATA : ", data_error)
    print("SHIFT : ", shift)
    print("TYPE : ", type)
    print("YEAR : ", year)
    if type == 'M':
        print("MONTH : ", month, "(" + get_month_no(month) + ")")
    print("WCG ID : ", work_center_group_id)
    if work_center_group_id != "All Work Center Group":
        print("MACHINE NO : ", machine_no)
    print("------------------------------------------")
    #-- FETCH DATA FROM DATABASE
    result = []
    error_result = []
    t0 = time.time()
    for i in range(x_count):
        trans = Transaction.objects.filter(start_datetime__year=year).order_by('mc') #CHECK YEAR
        if type == 'Y':
            trans = trans.filter(start_datetime__month=(i+1)) #CHECK MONTH
        elif type == 'M':
            trans = trans.filter(start_datetime__month=get_month_no(month)) #CHECK MONTH
            trans = trans.filter(start_datetime__day=(i+1)) #CHECK DATE
        if shift == 'DAY':
            trans = trans.filter(start_datetime__hour__gte=7)
            trans = trans.filter(start_datetime__hour__lt=19)
        elif shift == 'NIGHT':
            trans = trans.filter(start_datetime__hour__gte=19) | trans.filter(start_datetime__hour__lt=7)
        if machine_no != 'All Machine':
            mc = Machine.objects.get(no=machine_no)
            trans = trans.filter(mc=mc)
        elif work_center_group_id != "All Work Center Group":
            wcg = WorkCenterGroup.objects.get(id=work_center_group_id)
            mcs = Machine.objects.filter(wcg=wcg)
            trans = trans.filter(mc__in=mcs)
        err = False
        temp_time = 0
        temp_time_same_mc = 0
        temp_mc_no = "-"
        for t in trans:
            # print(t.mc.no, t.start_datetime, t.stop_datetime, t.operate_time)
            if(temp_mc_no == t.mc.no):
                temp_time_same_mc += float(t.operate_time)
            else:
                if data_error == "FALSE" and temp_time_same_mc > (12 * 60):
                    temp_time_same_mc = (12 * 60)
                    err = True
                temp_time += temp_time_same_mc
                temp_mc_no = t.mc.no
                temp_time_same_mc = float(t.operate_time)
        if data_error == "FALSE" and temp_time_same_mc > (12 * 60):
            temp_time_same_mc = (12 * 60)
            err = True
        temp_time += temp_time_same_mc
        result.append(temp_time)
        error_result.append(err)
    t1 = time.time()
    print("EXCUTE COMPLETED !")
    print("EXCUTE TIME : ", (t1 - t0))
    print("------------------------------------------")
    # print(result)
    data = {
        'result' : result,
        'error_result' : error_result,
    }
    return JsonResponse(data)

def get_data0(request):
    #-- REQUEST DATA
    year = request.GET.get('year')
    month = request.GET.get('month')
    mc_no = request.GET.get('mc_no')
    #-- Prepare Data
    result = []
    mc = Machine.objects.get(no=mc_no)
    trans = Transaction.objects.filter(mc=mc,start_datetime__year=year,start_datetime__month=get_month_no(month))
    day_count = get_month_day_count(year, month)
    for i in range(day_count):
        day = str(i + 1)
        name = ""
        color = "opacity: 0"
        start_hrs = 0
        start_min = 0
        end_hrs = 0
        end_min = 0
        result.append([day,name,color,start_hrs,start_min,end_hrs,end_min])
    for tran in trans:
        if float(tran.operate_time) > 720:
            print("Error :", tran.id, tran.start_datetime, tran.stop_datetime, tran.operate_time)
            day = str(tran.start_datetime.day)
            name = "✖"
            color = "red"
            start_hrs = tran.start_datetime.hour
            start_min = tran.start_datetime.minute
            end_hrs = tran.start_datetime.hour
            end_min = tran.start_datetime.minute + 20
            result.append([day,name,color,start_hrs,start_min,end_hrs,end_min])
        elif tran.start_datetime.day != tran.stop_datetime.day:
            day = str(tran.start_datetime.day)
            name = "►"
            color = "rgb(130,177,254)"
            start_hrs = tran.start_datetime.hour
            start_min = tran.start_datetime.minute
            end_hrs = 24
            end_min = 0
            result.append([day,name,color,start_hrs,start_min,end_hrs,end_min])
            day = str(tran.stop_datetime.day)
            name = "◄"
            color = "rgb(130,177,254)"
            start_hrs = 0
            start_min = 0
            end_hrs = tran.stop_datetime.hour
            end_min = tran.stop_datetime.minute
            result.append([day,name,color,start_hrs,start_min,end_hrs,end_min])
        else:
            day = str(tran.start_datetime.day)
            name = "►"
            if tran.start_datetime.hour == tran.stop_datetime.hour:
                name = ""
            color = "rgb(130,177,254)"
            start_hrs = tran.start_datetime.hour
            start_min = tran.start_datetime.minute
            end_hrs = tran.stop_datetime.hour
            end_min = tran.stop_datetime.minute
            result.append([day,name,color,start_hrs,start_min,end_hrs,end_min])
    data = {
        'result' : result,
    }
    return JsonResponse(data)

def get_machine_list(request):
    #-- REQUEST DATA FORM FRONT
    wcg_id = request.GET.get('wcg_id')
    #-- FETCH DATA FROM DATABASE
    machine_list = []
    mc_list = []
    if wcg_id == '-1':
        mc_list = Machine.objects.all()
    else:
        mc_list = Machine.objects.filter(wcg=wcg_id)
    for mc in mc_list:
        machine_list.append([mc.no,mc.name])
    data = {
        'machine_list' : machine_list,
    }
    return JsonResponse(data)

def get_exp_hrs(request):
    #-- REQUEST DATA FORM FRONT
    machine_no = request.GET.get('machine_no')
    #-- FETCH DATA FROM DATABASE
    machine = Machine.objects.get(no=machine_no)
    data = {
        'exp_hrs' : machine.exp_hrs,
    }
    return JsonResponse(data)

#--------------------------------------------------------------------------------------------------------------------- Update Data
def get_connection():
    conn = pyodbc.connect('Driver={SQL Server};''Server=SVSP-SQL;''Database=CCS_Production;''UID=CCSGROUPS\sqladmin;''PWD=$ql@2019;''Trusted_Connection=yes;')
                        # 'UID=CCSGROUPS\sqladmin;'
                        # 'PWD=$ql@2019;'
                        # 'Trusted_Connection=yes;'
    return conn

def update_data(request):
    UpdateWorkCenterGroup().start()
    UpdateMachine().start()
    UpdateTransaction().start()
    data = {
    }
    return JsonResponse(data)

class UpdateWorkCenterGroup(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("--- UPDATING WORK CENTER GROUP ---")
        all_item = 0
        new_item = 0
        cursor = get_connection().cursor()
        cursor.execute("SELECT REPLACE(WorkCenterGroup, ' Machine', '') as WorkCenterGroup FROM M_Machine WHERE WorkCenterGroup NOT LIKE '%Man%' GROUP BY WorkCenterGroup")
        workcentergroup_list = cursor.fetchall()
        for wcg in workcentergroup_list:
            all_item += 1
            isExist = WorkCenterGroup.objects.filter(name=wcg[0]).exists()
            if isExist == False:
                wcg_new = WorkCenterGroup(name=wcg.WorkCenterGroup)
                wcg_new.save()
                new_item += 1
        print("--- UPDATE WORK CENTER GROUP COMPLETED")
        print("--- ALL RECORD : " + str(all_item))
        print("--- NEW RECORD  : " + str(new_item))
        print("--- --- ---")

class UpdateMachine(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("--- UPDATING MACHINE ---")
        all_item = 0
        new_item = 0
        cursor = get_connection().cursor()
        cursor.execute("SELECT MachineNumber, MachineName, REPLACE(WorkCenterGroup, ' Machine', '') as WorkCenterGroup FROM M_Machine")
        machine_list = cursor.fetchall()
        for mc in machine_list:
            all_item += 1
            isMachineExist = Machine.objects.filter(no=mc[0]).exists()
            if isMachineExist == False:
                isWCGExist = WorkCenterGroup.objects.filter(name=mc[2]).exists()
                if isWCGExist == True:
                    wcg = WorkCenterGroup.objects.get(name=mc[2])
                    mc_new = Machine(no=mc[0],name=mc[1],wcg=wcg)
                    mc_new.save()
                    new_item += 1
        print("--- UPDATE MACHINE COMPLETED")
        print("--- ALL RECORD : " + str(all_item))
        print("--- NEW RECORD  : " + str(new_item))
        print("--- --- ---")

class UpdateTransaction(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # Transaction.objects.all().delete()
        print("--- UPDATING TRANSACTION COMPLETED ---")
        all_item = 0
        new_item = 0
        lastest_tran = last_transaction()
        start_query_date = lastest_tran.start_datetime + relativedelta(months=-1)
        cursor = get_connection().cursor()
        queryStr = "SELECT MachineOperatorID, MachineOperatorStart, MachineOperatorStop, MachineOperatorTime"
        queryStr += " FROM L_ProductionOrderRoutingMachineOperator"
        queryStr += " WHERE OperateBy = 'Machine' AND MachineOperatorTime <> 0"
        queryStr += " AND CAST(MachineOperatorStart AS Date) >= '" + start_query_date.strftime("%Y-%m-%d") + "'"
        queryStr += " ORDER BY MachineOperatorStart"
        cursor.execute(queryStr)
        transaction_list = cursor.fetchall()
        for tran in transaction_list:
            all_item += 1
            isMachineExist = Machine.objects.filter(no=tran[0]).exists()
            if isMachineExist == True:
                mc = Machine.objects.get(no=tran[0])
                isTranExist = Transaction.objects.filter(mc=mc,start_datetime=tran[1],stop_datetime=tran[2],operate_time=tran[3]).exists()
                if isTranExist == False:
                    tran_new = Transaction(mc=mc,start_datetime=tran[1],stop_datetime=tran[2],operate_time=tran[3])
                    tran_new.save()
                    new_item += 1
        print("--- UPDATE TRANSACTION COMPLETED")
        # print("--- QUERY STATEMENT : " + queryStr)
        print("--- START QUERY DATE : " + start_query_date.strftime("%Y-%m-%d"))
        print("--- ALL RECORD : " + str(all_item))
        print("--- NEW RECORD  : " + str(new_item))
        print("--- --- ---")

def last_transaction():
    tran = Transaction.objects.last()
    return tran

#--------------------------------------------------------------------------------------------------------------------- ETC Function
def get_month_no(month):
    month_set = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
    return str(month_set.index(month) + 1)

def get_month_day_count(year, month):
    if month == "FEB" and int(year)%4 == 0:
        return 29
    elif month == "FEB" :
        return 28
    elif month == "JAN" or month == "MAR" or month == "MAY" or month == "JUL" or month == "AUG" or month == "OCT" or month == "DEC":
        return 31
    return 30
