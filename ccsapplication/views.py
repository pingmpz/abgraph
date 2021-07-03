from django.shortcuts import render
import pyodbc
from .models import WorkCenterGroup, Machine, Transaction, Record
from django.http import JsonResponse
import math
import random
import json
import threading

def get_connection():
    conn = pyodbc.connect('Driver={SQL Server};''Server=SVSP-SQL;''Database=CCS_Production;')
                        # 'UID=CCSGROUPS\sqladmin;'
                        # 'PWD=$ql@2019;'
                        # 'Trusted_Connection=yes;'
    return conn

def index(request):
    cursor = get_connection().cursor()
    UpdateWorkCenterGroup().start()
    UpdateMachine().start()
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
    # print(shift, x_count, type, year, month, work_center_group_id, work_center_group_id_count, machine_no, machine_count)
    #-- FETCH DATA FROM DATABASE
    cursor = get_connection().cursor()
    result = []
    result = get_random_data(x_count, type, work_center_group_id, work_center_group_id_count, machine_no, machine_count)
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
        cursor = get_connection().cursor()
        cursor.execute("SELECT REPLACE(WorkCenterGroup, ' Machine', '') as WorkCenterGroup FROM M_Machine WHERE WorkCenterGroup NOT LIKE '%Man%' GROUP BY WorkCenterGroup")
        workcentergroup_list = cursor.fetchall()
        for wcg in workcentergroup_list:
            isExist = WorkCenterGroup.objects.filter(name=wcg[0]).exists()
            if isExist == False:
                wcg_new = WorkCenterGroup(name=wcg.WorkCenterGroup)
                wcg_new.save()

class UpdateMachine(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        cursor = get_connection().cursor()
        cursor.execute("SELECT MachineNumber, MachineName, REPLACE(WorkCenterGroup, ' Machine', '') as WorkCenterGroup FROM M_Machine")
        machine_list = cursor.fetchall()
        for mc in machine_list:
            isMachineExist = Machine.objects.filter(no=mc[0]).exists()
            if isMachineExist == False:
                isWCGExist = WorkCenterGroup.objects.filter(name=mc[2]).exists()
                if isWCGExist == True:
                    wcg = WorkCenterGroup.objects.get(name=mc[2])
                    mc_new = Machine(no=mc[0],name=mc[1],wcg=wcg)
                    mc_new.save()

class UpdateTransaction(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        cursor = get_connection().cursor()
        queryStr = "SELECT MachineOperatorID, MachineOperatorStart, MachineOperatorStop, MachineOperatorTime FROM L_ProductionOrderRoutingMachineOperator WHERE OperateBy = 'Machine' AND MachineOperatorTime <> 0"
        cursor.execute(queryStr)
        transaction_list = cursor.fetchall()
