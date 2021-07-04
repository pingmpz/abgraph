from django.shortcuts import render
import pyodbc
from .models import WorkCenterGroup, Machine, Transaction
from django.http import JsonResponse
import math
import random
import json
import threading
from datetime import datetime
import time

def get_connection():
    conn = pyodbc.connect('Driver={SQL Server};''Server=SVSP-SQL;''Database=CCS_Production;')
                        # 'UID=CCSGROUPS\sqladmin;'
                        # 'PWD=$ql@2019;'
                        # 'Trusted_Connection=yes;'
    return conn

def index(request):
    # UpdateWorkCenterGroup().start()
    # UpdateMachine().start()
    # UpdateTransaction().start()
    workcentergroup_list = WorkCenterGroup.objects.all()
    machine_list = Machine.objects.all()
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
    work_center_group_id = request.GET.get('work_center_group_id')
    work_center_group_id_count = request.GET.get('work_center_group_id_count')
    machine_no = request.GET.get('machine_no')
    machine_count = request.GET.get('machine_count')
    print("------------------------------------------")
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
    t0 = time.time()
    for i in range(x_count):
        trans = Transaction.objects.filter(start_datetime__year=year) #CHECK YEAR
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
        temp_time = 0
        temp_machine_no = "-1"
        for t in trans:
            # print(t.mc.no, t.start_datetime, t.stop_datetime, t.operate_time)
            temp_time += round(float(t.operate_time) / 60)
        result.append(temp_time)
    t1 = time.time()
    print("EXCUTE COMPLETED !")
    print("EXCUTE TIME : ", (t1 - t0))
    print("------------------------------------------")
    # result = get_random_data(x_count, type, work_center_group_id, work_center_group_id_count, machine_no, machine_count)
    # print(result)
    data = {
        'result' : result,
    }
    return JsonResponse(data)

def get_machine_list(request):
    #-- REQUEST DATA FORM FRONT
    work_center_group_id = request.GET.get('work_center_group_id')
    #-- FETCH DATA FROM DATABASE
    machine_list = []
    mc_list = []
    if work_center_group_id == 'All Work Center Group':
        mc_list = Machine.objects.all()
    else:
        mc_list = Machine.objects.filter(wcg=work_center_group_id)
    for mc in mc_list:
        machine_list.append([mc.no,mc.name])
    data = {
        'machine_list' : machine_list,
    }
    return JsonResponse(data)

#--------------------------------------------------------------------------------------------------------------------- ETC Function
def get_month_no(month):
    month_set = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
    return str(month_set.index(month) + 1)

def get_random_data(x_count, type, work_center_group_id, work_center_group_id_count, machine_no, machine_count):
    result = []
    for i in range(x_count):
        coef = 1; # coefficient
        if(type == "Y"):
            coef = coef * 30;
        if(work_center_group_id == "All Work Center Group"):
            coef = coef * int(machine_count) * int(work_center_group_id_count)
        if(work_center_group_id != "All Work Center Group" and machine_no == "All Machine"):
            coef = coef * int(machine_count)
        result.append(math.floor(random.randint(0, 12) * coef))
    return result

#--------------------------------------------------------------------------------------------------------------------- Threading
class UpdateWorkCenterGroup(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
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
        print("------------------------------------------")
        print("--- UPDATE WORK CENTER GROUP COMPLETED")
        print("--- ALL ITEM : " + str(all_item))
        print("--- NEW ITEM : " + str(new_item))
        print("------------------------------------------")

class UpdateMachine(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
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
        print("--------------------------------")
        print("--- UPDATE MACHINE COMPLETED")
        print("--- ALL ITEM : " + str(all_item))
        print("--- NEW ITEM : " + str(new_item))
        print("--------------------------------")

class UpdateTransaction(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        all_item = 0
        new_item = 0
        cursor = get_connection().cursor()
        queryStr = "SELECT MachineOperatorID, MachineOperatorStart, MachineOperatorStop, MachineOperatorTime FROM L_ProductionOrderRoutingMachineOperator WHERE OperateBy = 'Machine' AND MachineOperatorTime <> 0"
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
        print("------------------------------------")
        print("--- UPDATE TRANSACTION COMPLETED")
        print("--- ALL ITEM : " + str(all_item))
        print("--- NEW ITEM : " + str(new_item))
        print("------------------------------------")
