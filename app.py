from flask import Flask, render_template, request, session, redirect, url_for, send_file, jsonify
from werkzeug.utils import secure_filename
from os.path import join, dirname, abspath
from database import collectioncon
from werkzeug.security import check_password_hash
from os import listdir, urandom, remove
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(24)

bsdic = {}


def get_current_user():
    user_result = None
    if 'user' in session:
        user = session['user']
        cl = collectioncon('user')
        user_result = cl.find_one({'id': user}, {'_id': 0})
    return user_result


@app.route('/')
def index():
    title = '상황판'
    user = get_current_user()
    ds_cl = collectioncon('dashindex')
    bu_cl = collectioncon('business')
    svr_cl = collectioncon('svr')
    ch_cl = collectioncon('chart')
    dash_checked = list(ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                         {'$match': {'children.children.name': '완료'}}]))
    dash_checking = list(ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                          {'$match': {'children.children.name': '점검중'}}]))
    dash_uncheck = list(ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                         {'$match': {'children.children.name': '미점검'}}]))
    svr_total = list(svr_cl.find({}, {'_id': 0}))
    svr_started = list(svr_cl.find({'started': 1}, {'_id': 0}))
    drstime = ds_cl.find_one({'step': '재해 선언'}, {'_id': 0, 'Stime': 1})
    drstime1 = drstime['Stime']
    drstime = ds_cl.find_one({'step': '시스템 복구(업무 기동 포함)'}, {'_id': 0, 'Stime': 1})
    drstime2 = drstime['Stime']
    drstime = ds_cl.find_one({'step': '업무 점검'}, {'_id': 0, 'Stime': 1})
    drstime3 = drstime['Stime']
    drstime = ds_cl.find_one({'step': '재해 복구 완료'}, {'_id': 0, 'Stime': 1})
    drstime4 = drstime['Stime']
    drfinish = ds_cl.find_one({'step': '재해 복구 완료'}, {'_id': 0, 'Qtime': 1})
    drfinish1 = drfinish['Qtime']
    alldata = ds_cl.find({}, {'_id': 0})
    total_svr_done = svr_cl.aggregate([{'$match': {'started': {'$exists': 1}}}])
    svr_done = svr_cl.aggregate([{'$match': {'started': 1}}])
    svr_timeck = ds_cl.find_one({'step': '시스템 복구(업무 기동 포함)'}, {'_id': 0, 'timeck': 1})
    svr_timeck = svr_timeck['timeck']

    total_num = len(list(ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}}])))
    restore_num = len(list(ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'children.children.name': '복구중'}}])))
    bs_uncheck_num = len(list(ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'children.children.name': '미점검'}}])))
    bs_checking_num = len(list(ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'children.children.name': '점검중'}}])))
    bs_checked_num = len(list(ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'children.children.name': '완료'}}])))

    if len(list(total_svr_done)) == len(list(svr_done)) and svr_timeck == 0:
        svr_done_time = datetime.now().strftime('%Y/%m/%d %H:%M')
        ds_cl.update_one({'step': '시스템 복구(업무 기동 포함)'}, {'$set': {'Qtime': svr_done_time}})
        ds_cl.update_one({'step': '시스템 복구(업무 기동 포함)'}, {'$set': {'timeck': 1}})
        ds_cl.update_one({'step': '업무 점검'}, {'$set': {'Stime': svr_done_time}})
    else:
        pass
    total_bsdone = bu_cl.aggregate([{'$unwind': '$BS'}, {'$match': {'BS.BSdone': {'$exists': 1}}}])
    bsdone = bu_cl.aggregate([{'$unwind': '$BS'}, {'$match': {'BS.BSdone': 1}}])
    bs_timeck = ds_cl.find_one({'step': '업무 점검'}, {'_id': 0, 'timeck': 1})
    bs_timeck = bs_timeck['timeck']
    if len(list(total_bsdone)) == len(list(bsdone)) and bs_timeck == 0:
        bsdone_time = datetime.now().strftime('%Y/%m/%d %H:%M')
        ds_cl.update_one({'step': '업무 점검'}, {'$set': {'Qtime': bsdone_time}})
        ds_cl.update_one({'step': '재해 복구 완료'}, {'$set': {'Stime': bsdone_time}})
        ds_cl.update_one({'step': '업무 점검'}, {'$set': {'timeck': 1}})
    else:
        pass
    if len(drstime1) == 0:
        pass
    else:
        drstime = ds_cl.find_one({'step': '재해 선언'}, {'_id': 0, 'Stime': 1})
        drstime1 = drstime['Stime']
    return render_template('index.html', title=title, user=user, drfinish=drfinish1, drstime4=drstime4,
                           drstime3=drstime3,
                           drstime2=drstime2, drstime1=drstime1,
                           alldata=alldata,
                           total_num=total_num, restore_num=restore_num, bs_uncheck_num=bs_uncheck_num,
                           bs_checking_num=bs_checking_num, bs_checked_num=bs_checked_num,
                           svr_total=svr_total, svr_started=svr_started, dash_checked=dash_checked,
                           dash_checking=dash_checking, dash_uncheck=dash_uncheck)


@app.route('/index2')
def index2():
    title = '상황판'
    user = get_current_user()
    ds_cl = collectioncon('dashindex')
    bu_cl = collectioncon('business')
    svr_cl = collectioncon('svr')
    ch_cl = collectioncon('chart')
    dash_checked = list(ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                         {'$match': {'children.children.name': '완료'}}]))
    dash_checking = list(ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                          {'$match': {'children.children.name': '점검중'}}]))
    dash_uncheck = list(ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                         {'$match': {'children.children.name': '미점검'}}]))
    svr_total = list(svr_cl.find({}, {'_id': 0}))
    svr_started = list(svr_cl.find({'started': 1}, {'_id': 0}))
    drstime = ds_cl.find_one({'step': '재해 선언'}, {'_id': 0, 'Stime': 1})
    drstime1 = drstime['Stime']
    drstime = ds_cl.find_one({'step': '시스템 복구(업무 기동 포함)'}, {'_id': 0, 'Stime': 1})
    drstime2 = drstime['Stime']
    drstime = ds_cl.find_one({'step': '업무 점검'}, {'_id': 0, 'Stime': 1})
    drstime3 = drstime['Stime']
    drstime = ds_cl.find_one({'step': '재해 복구 완료'}, {'_id': 0, 'Stime': 1})
    drstime4 = drstime['Stime']
    drfinish = ds_cl.find_one({'step': '재해 복구 완료'}, {'_id': 0, 'Qtime': 1})
    drfinish1 = drfinish['Qtime']
    alldata = ds_cl.find({}, {'_id': 0})
    total_svr_done = svr_cl.aggregate([{'$match': {'started': {'$exists': 1}}}])
    svr_done = svr_cl.aggregate([{'$match': {'started': 1}}])
    svr_timeck = ds_cl.find_one({'step': '시스템 복구(업무 기동 포함)'}, {'_id': 0, 'timeck': 1})
    svr_timeck = svr_timeck['timeck']

    total_num = len(list(ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}}])))
    restore_num = len(list(ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'children.children.name': '복구중'}}])))
    bs_uncheck_num = len(list(ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'children.children.name': '미점검'}}])))
    bs_checking_num = len(list(ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'children.children.name': '점검중'}}])))
    bs_checked_num = len(list(ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'children.children.name': '완료'}}])))

    if len(list(total_svr_done)) == len(list(svr_done)) and svr_timeck == 0:
        svr_done_time = datetime.now().strftime('%Y/%m/%d %H:%M')
        ds_cl.update_one({'step': '시스템 복구(업무 기동 포함)'}, {'$set': {'Qtime': svr_done_time}})
        ds_cl.update_one({'step': '시스템 복구(업무 기동 포함)'}, {'$set': {'timeck': 1}})
        ds_cl.update_one({'step': '업무 점검'}, {'$set': {'Stime': svr_done_time}})
    else:
        pass
    total_bsdone = bu_cl.aggregate([{'$unwind': '$BS'}, {'$match': {'BS.BSdone': {'$exists': 1}}}])
    bsdone = bu_cl.aggregate([{'$unwind': '$BS'}, {'$match': {'BS.BSdone': 1}}])
    bs_timeck = ds_cl.find_one({'step': '업무 점검'}, {'_id': 0, 'timeck': 1})
    bs_timeck = bs_timeck['timeck']
    if len(list(total_bsdone)) == len(list(bsdone)) and bs_timeck == 0:
        bsdone_time = datetime.now().strftime('%Y/%m/%d %H:%M')
        ds_cl.update_one({'step': '업무 점검'}, {'$set': {'Qtime': bsdone_time}})
        ds_cl.update_one({'step': '재해 복구 완료'}, {'$set': {'Stime': bsdone_time}})
        ds_cl.update_one({'step': '업무 점검'}, {'$set': {'timeck': 1}})
    else:
        pass
    if len(drstime1) == 0:
        pass
    else:
        drstime = ds_cl.find_one({'step': '재해 선언'}, {'_id': 0, 'Stime': 1})
        drstime1 = drstime['Stime']

    ch_cl = collectioncon('chart')
    OC = ch_cl.find({'name': '쇼핑몰'}, {'_id': 0})
    OC_total = ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'name': '쇼핑몰'}}])
    OC_total = len(list(OC_total))
    OC_uncheck_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                      {'$match': {'name': '쇼핑몰', 'children.children.name': '미점검'}}])
    OC_uncheck_num = len(list(OC_uncheck_num))
    OC_checking_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': '쇼핑몰', 'children.children.name': '점검중'}}])
    OC_checking_num = len(list(OC_checking_num))
    OC_checked_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                      {'$match': {'name': '쇼핑몰', 'children.children.name': '완료'}}])
    OC_checked_num = len(list(OC_checked_num))
    pos = ch_cl.find({'name': 'POS'}, {'_id': 0})
    pos_total = ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'name': 'POS'}}])
    pos_total = len(list(pos_total))
    pos_uncheck_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': 'POS', 'children.children.name': '미점검'}}])
    pos_uncheck_num = len(list(pos_uncheck_num))
    pos_checking_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                        {'$match': {'name': 'POS', 'children.children.name': '점검중'}}])
    pos_checking_num = len(list(pos_checking_num))
    pos_checked_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': 'POS', 'children.children.name': '완료'}}])
    pos_checked_num = len(list(pos_checked_num))
    prm = ch_cl.find({'name': 'PRM NEXT'}, {'_id': 0})
    prm_total = ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'name': 'PRM NEXT'}}])
    prm_total = len(list(prm_total))
    prm_uncheck_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': 'PRM NEXT', 'children.children.name': '미점검'}}])
    prm_uncheck_num = len(list(prm_uncheck_num))
    prm_checking_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                        {'$match': {'name': 'PRM NEXT', 'children.children.name': '점검중'}}])
    prm_checking_num = len(list(prm_checking_num))

    prm_checked_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': 'PRM NEXT', 'children.children.name': '완료'}}])
    prm_checked_num = len(list(prm_checked_num))
    scm = ch_cl.find({'name': 'SCM'}, {'_id': 0})
    scm_total = ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'name': 'SCM'}}])
    scm_total = len(list(scm_total))
    scm_uncheck_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': 'SCM', 'children.children.name': '미점검'}}])
    scm_uncheck_num = len(list(scm_uncheck_num))
    scm_checking_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                        {'$match': {'name': 'SCM', 'children.children.name': '점검중'}}])
    scm_checking_num = len(list(scm_checking_num))
    scm_checked_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': 'SCM', 'children.children.name': '완료'}}])
    scm_checked_num = len(list(scm_checked_num))
    fcm = ch_cl.find({'name': 'FCM'}, {'_id': 0})
    fcm_total = ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'name': 'FCM'}}])
    fcm_total = len(list(fcm_total))
    fcm_uncheck_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': 'FCM', 'children.children.name': '미점검'}}])
    fcm_uncheck_num = len(list(fcm_uncheck_num))
    fcm_checking_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                        {'$match': {'name': 'FCM', 'children.children.name': '점검중'}}])
    fcm_checking_num = len(list(fcm_checking_num))
    fcm_checked_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': 'FCM', 'children.children.name': '완료'}}])
    fcm_checked_num = len(list(fcm_checked_num))
    hrm = ch_cl.find({'name': 'HRM'}, {'_id': 0})
    hrm_total = ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'name': 'HRM'}}])
    hrm_total = len(list(hrm_total))
    hrm_uncheck_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': 'HRM', 'children.children.name': '미점검'}}])
    hrm_uncheck_num = len(list(hrm_uncheck_num))
    hrm_checking_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                        {'$match': {'name': 'HRM', 'children.children.name': '점검중'}}])
    hrm_checking_num = len(list(hrm_checking_num))
    hrm_checked_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': 'HRM', 'children.children.name': '완료'}}])
    hrm_checked_num = len(list(hrm_checked_num))
    common = ch_cl.find({'name': '공통'}, {'_id': 0})
    common_total = ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'name': '공통'}}])
    common_total = len(list(common_total))
    common_uncheck_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                          {'$match': {'name': '공통', 'children.children.name': '미점검'}}])
    common_uncheck_num = len(list(common_uncheck_num))
    common_checking_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                           {'$match': {'name': '공통', 'children.children.name': '점검중'}}])
    common_checking_num = len(list(common_checking_num))
    common_checked_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                          {'$match': {'name': '공통', 'children.children.name': '완료'}}])
    common_checked_num = len(list(common_checked_num))
    etc = ch_cl.find({'name': '기타'}, {'_id': 0})
    etc_total = ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'name': '기타'}}])
    etc_total = len(list(etc_total))
    etc_uncheck_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': '기타', 'children.children.name': '미점검'}}])
    etc_uncheck_num = len(list(etc_uncheck_num))
    etc_checking_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                        {'$match': {'name': '기타', 'children.children.name': '점검중'}}])
    etc_checking_num = len(list(etc_checking_num))
    etc_checked_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': '기타', 'children.children.name': '완료'}}])
    etc_checked_num = len(list(etc_checked_num))

    OC = list(OC)
    pos = list(pos)
    prm = list(prm)
    scm = list(scm)
    fcm = list(fcm)
    hrm = list(hrm)
    common = list(common)
    etc = list(etc)

    # bs_cl=collectioncon('chart')
    OC_uncheck_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                      {'$match': {'name': '쇼핑몰', 'children.children.name': '미점검'}}])
    OC_uncheck_num = len(list(OC_uncheck_num))
    # cl = collectioncon('business')
    # data = list(cl.find({}, {'_id': False}))
    return render_template('index2.html', title=title, user=user, drfinish=drfinish1, drstime4=drstime4,
                           drstime3=drstime3,
                           drstime2=drstime2, drstime1=drstime1,
                           alldata=alldata,
                           total_num=total_num, restore_num=restore_num, bs_uncheck_num=bs_uncheck_num,
                           bs_checking_num=bs_checking_num, bs_checked_num=bs_checked_num,
                           svr_total=svr_total, svr_started=svr_started, dash_checked=dash_checked,
                           dash_checking=dash_checking, dash_uncheck=dash_uncheck, OC=OC,
                           pos=pos, prm=prm, scm=scm, fcm=fcm, hrm=hrm, common=common, etc=etc,
                           OC_total=OC_total, pos_total=pos_total, scm_total=scm_total, fcm_total=fcm_total,
                           hrm_total=hrm_total,
                           common_total=common_total, etc_total=etc_total, prm_total=prm_total,
                           OC_uncheck_num=OC_uncheck_num, OC_checking_num=OC_checking_num,
                           OC_checked_num=OC_checked_num,
                           pos_uncheck_num=pos_uncheck_num, pos_checked_num=pos_checked_num,
                           pos_checking_num=pos_checking_num,
                           prm_uncheck_num=prm_uncheck_num, prm_checking_num=prm_checking_num,
                           prm_checked_num=prm_checked_num,
                           scm_uncheck_num=scm_uncheck_num, scm_checking_num=scm_checking_num,
                           scm_checked_num=scm_checked_num,
                           fcm_uncheck_num=fcm_uncheck_num, fcm_checking_num=fcm_checking_num,
                           fcm_checked_num=fcm_checked_num,
                           hrm_uncheck_num=hrm_uncheck_num, hrm_checking_num=hrm_checking_num,
                           hrm_checked_num=hrm_checked_num,
                           common_uncheck_num=common_uncheck_num, common_checking_num=common_checking_num,
                           common_checked_num=common_checked_num,
                           etc_uncheck_num=etc_uncheck_num, etc_checking_num=etc_checking_num,
                           etc_checked_num=etc_checked_num)


@app.route('/timesave', methods=['POST'])
def timesave():
    if request.method == 'POST':
        drstime = request.form['time']
        cl = collectioncon('dashindex')
        cl.update_one({'step': '재해 선언'}, {'$set': {'Stime': drstime, 'Qtime': drstime}})
        return redirect(url_for('index'))


@app.route('/timereset', methods=['POST'])
def timereset():
    if request.method == 'POST':
        # drstime = request.form['time']
        ds_cl = collectioncon('dashindex')
        svr_cl = collectioncon('svr')
        bu_cl = collectioncon('business')
        ch_cl = collectioncon('chart')
        ch_cl.update_many({},
                          {'$set': {'children.$[].children.$[].name': '미점검',
                                    'children.$[].children.$[].normal.fill': '#FF7A85'}})
        ds_cl.update_one({'step': '재해 선언'}, {'$set': {'Stime': '', 'Qtime': '', 'timeck': 0}})
        ds_cl.update_one({'step': '시스템 복구(업무 기동 포함)'}, {'$set': {'Stime': '', 'Qtime': '', 'timeck': 0}})
        ds_cl.update_one({'step': '업무 점검'}, {'$set': {'Stime': '', 'Qtime': '', 'timeck': 0}})
        ds_cl.update_one({'step': '재해 복구 완료'}, {'$set': {'Stime': '', 'Qtime': '', 'timeck': 0}})
        svr_cl.update_many({'started': 1}, {'$set': {'started': 0}})
        while (True):
            valcheck = (bu_cl.update({'BS.checked': 1},
                                     {'$set': {'BS.$.BSdone': 0, 'BS.$.BSing': 0,
                                               'BS.$.ckname': '', 'BS.$.ckdate': '',
                                               'BS.$.checked': 0}}))
            if (valcheck['nModified'] == 0):
                break
        return redirect(url_for('index'))


@app.route('/systimesave', methods=['POST'])
def systimesave():
    if request.method == 'POST':
        drstime = request.form['time']
        cl = collectioncon('dashindex')
        cl.update_one({'step': '시스템 복구(업무 기동 포함)'}, {'$set': {'Stime': drstime}})
        return redirect(url_for('index'))


@app.route('/drillfinish', methods=['POST'])
def drillfinish():
    if request.method == 'POST':
        drstime = request.form['time']
        cl = collectioncon('dashindex')
        cl.update_one({'step': '재해 복구 완료'}, {'$set': {'Qtime': drstime}})
        return redirect(url_for('index'))


def systimedone():
    cl = collectioncon('svr')
    total = cl.find({}, {'_id': 0, 'started': 1}).count()
    current = cl.find({'started': 1}, {'_id': 0, 'started': 1}).count()
    if total == current:
        cl1 = collectioncon('dashindex')
        cl1.update_one({'step': '시스템 복구(업무 기동 포함)'}, {'$set': {'Qtime': ''}})


def servtimedone():
    cl = collectioncon('business')
    total = cl.find({}, {'_id': 0, 'started': 1}).count()
    current = cl.find({'started': 1}, {'_id': 0, 'started': 1}).count()
    if total == current:
        cl1 = collectioncon('dashindex')
        cl1.update_one({'step': '업무 점검'}, {'$set': {'Qtime': ''}})


@app.route('/dashsvrrate', methods=['POST', 'GET'])
def dashsvrrate():
    cl = collectioncon('svr')
    data = list(cl.find({}, {'_id': 0, 'started': 1}))
    return jsonify(data)


@app.route('/dashbsrate', methods=['POST', 'GET'])
def dashbsrate():
    cl = collectioncon('business')
    data = list(cl.find({}, {'_id': 0, 'BS.BSdone': 1}))
    data2 = []
    for i in data:
        for x in i['BS']:
            data2.append(x)
    return jsonify(data2)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = get_current_user()
        cl = collectioncon('user')
        user = request.form['username']
        passwd = request.form['password']
        getuser = cl.find_one({'id': user}, {'_id': False})
        if getuser is None:
            return 'no user'
        else:
            if check_password_hash(getuser['pw'], passwd):
                session['user'] = getuser['id']
                return redirect(url_for('index'))
            else:
                return 'password is not correct'
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route('/hostrate')
def hostrate():
    title = '서버 기동률'
    user = get_current_user()
    if 'user' in session and 'bcrs' in user['id']:
        cl = collectioncon('svr')
        data = list(cl.find({}, {'_id': 0}))
        return render_template('hostrate.html', title=title, user=user, data=data)
    return redirect(url_for('login'))


@app.route('/hostmg')
def hostmg():
    title = '서버 관리'
    user = get_current_user()
    if 'user' in session:
        if 'bcrs' in user['id']:
            cl = collectioncon('svr')
            data = cl.find()
            return render_template('hostmg.html', title=title, user=user, data=data)
    return redirect(url_for('login'))


@app.route('/hostadd', methods=['POST'])
def hostadd():
    user = get_current_user()
    if 'user' in session:
        if 'bcrs' in user['id']:
            hostname = request.form['hostname']
            ip = request.form['ip']
            port = request.form['port']
            port = int(port)
            cl = collectioncon('svr')
            cl.insert_one({'hostname': hostname, 'ip': ip, 'port': port})
            return redirect(url_for('hostmg'))
    return redirect(url_for('login'))


@app.route('/hostdel/<hostname>', methods=['POST', 'GET'])
def hostdel(hostname):
    user = get_current_user()
    if 'user' in session:
        if 'bcrs' in user['id']:
            cl = collectioncon('svr')
            cl.remove({'hostname': hostname})
            return redirect(url_for('hostmg'))
    return redirect(url_for('index'))


@app.route('/hostedit', methods=['POST'])
def hostedit():
    user = get_current_user()
    if 'user' in session:
        if 'bcrs' in user['id']:
            hostname = request.form['hostname']
            org_hostname = request.form['org_hostname']
            ip = request.form['ip']
            port = request.form['port']
            port = int(port)
            cl = collectioncon('svr')
            cl.update({'hostname': org_hostname}, {'$set': {'hostname': hostname, 'ip': ip, 'port': port}})
            return redirect(url_for('hostmg'))
    return redirect(url_for('login'))


@app.route('/bs', methods=['POST', 'GET'])
def bs():
    title = '업무명 관리'
    user = get_current_user()
    if 'user' in session:
        cl = collectioncon('business')
        data = cl.find({}, {'_id': False})
        data = list(data)
        if request.method == 'POST':
            bdname = request.form['bdname']
            if bdname:
                data1 = cl.find_one({'BD': bdname}, {'_id': False})
                return data1
        return render_template('bs.html', title=title, user=user, data=data)
    return redirect(url_for('login'))


@app.route('/files')
def files():
    title = '업무복구문서 다운로드'
    user = get_current_user()
    if 'user' in session:
        basedir = abspath(dirname(__file__))
        uploaddir = basedir + '/uploads'
        data = listdir(uploaddir)
        return render_template('files.html', user=user, title=title, data=data)
    return redirect(url_for('login'))


@app.route('/fileupload', methods=['POST', 'GET'])
def upload():
    basedir = abspath(dirname(__file__))
    user = get_current_user()
    if 'user' in session and 'bcrs' in user['id']:
        if request.method == 'POST':
            f = request.files.getlist('file[]')
            for i in f:
                i.save(join(basedir, 'uploads', secure_filename(i.filename)))
        return redirect(url_for('files'))
    return redirect(url_for('login'))


@app.route('/filedelete', methods=['POST', 'GET'])
def filedelete():
    user = get_current_user()
    if 'user' in session and 'bcrs' in user['id']:
        if request.method == 'GET':
            basedir = abspath(dirname(__file__))
            uploaddir = basedir + '/uploads'
            data = listdir(uploaddir)
            for i in data:
                remove(uploaddir + '/' + i)
        return redirect(url_for('files'))
    return redirect(url_for('login'))


@app.route('/download/<filename>')
def download(filename):
    file = f'uploads/' + filename
    return send_file(file)


@app.route('/bdedit', methods=['POST'])
def bdedit():
    user = get_current_user()
    if 'user' in session and 'bcrs' in user['id']:
        org_bdname = request.form['org_bdname']
        bdname = request.form['bdname']
        cl = collectioncon('business')
        if org_bdname:
            cl.update({'BD': org_bdname}, {'$set': {'BD': bdname}})
        else:
            cl.insert_one({'BD': bdname, 'BS': [{'BSname': '', 'BSing': 0, 'BSdone': 0,
                                                 'ckdate': '', 'ckname': '', 'checked': 0}]})
        return redirect(url_for('bsmanage'))
    return redirect(url_for('login'))


@app.route('/bddel/<path:bd>')
def bddel(bd):
    user = get_current_user()
    if 'user' in session and 'bcrs' in user['id']:
        cl = collectioncon('business')
        cl.remove({'BD': bd})
        return redirect(url_for('bsmanage'))
    return redirect(url_for('login'))


@app.route('/bsdel/<path:bdname>/<path:bsname>')
def bsdel(bdname, bsname):
    user = get_current_user()
    if 'user' in session and 'bcrs' in user['id']:
        cl = collectioncon('business')
        cl.update_one({'BD': bdname}, {'$pull': {'BS': {'BSname': bsname}}})
        return redirect(url_for('bsmanage'))
    return redirect(url_for('login'))


@app.route('/bsadd', methods=['POST'])
def bsadd():
    user = get_current_user()
    if 'user' in session and 'bcrs' in user['id']:
        org_bdname = request.form['org_bdname2']
        bsname = request.form['bsname']
        cl = collectioncon('business')
        cl.update_one({'BD': org_bdname},
                      {'$push': {'BS': {'BSname': bsname,
                                        'BSing': 0, 'BSdone': 0,
                                        'ckdate': '',
                                        'ckname': '',
                                        'checked': 0}}})
        return redirect(url_for('bsmanage'))
    return redirect(url_for('login'))


@app.route('/bsingcheck', methods=['POST'])
def bsingcheck():
    user = get_current_user()
    if 'user' in session:
        cl = collectioncon('business')
        ch_cl = collectioncon('chart')
        if request.method == 'POST':
            bsname = request.form['bsname']
            cl.update_one({'BS.BSname': bsname}, {'$set': {'BS.$.BSing': 1, 'BS.$.checked': 1}})
            ch_cl.update_one({'children.name': bsdic[bsname]}, {'$set': {'children.$.children.$[].name'
                                                                         : '점검중',
                                                                         'children.$.children.$[].normal.fill': '#6495ED'}})
        return redirect(url_for('bs'))
    return redirect(url_for('login'))


@app.route('/bsingcheckreset', methods=['POST'])
def bsingcheckreset():
    user = get_current_user()
    if 'user' in session:
        cl = collectioncon('business')
        ch_cl = collectioncon('chart')
        if request.method == 'POST':
            bsname = request.form['bsname']
            cl.update_one({'BS.BSname': bsname}, {'$set': {'BS.$.BSing': 0, 'BS.$.checked': 0}})
            ch_cl.update_one({'children.name': bsdic[bsname]}, {'$set': {'children.$.children.$[].name'
                                                                         : '미점검',
                                                                         'children.$.children.$[].normal.fill': '#FF7A85'}})
        return redirect(url_for('bs'))
    return redirect(url_for('login'))


@app.route('/bsdonecheck', methods=['POST'])
def bsdonecheck():
    user = get_current_user()
    if 'user' in session:
        cl = collectioncon('business')
        ch_cl = collectioncon('chart')
        if request.method == 'POST':
            bsname = request.form['bsname']
            # ckname = request.form['ckname']
            # ckdate = request.form['ckdate']
            ch_cl.update_one({'children.name': bsdic[bsname]}, {'$set': {'children.$.children.$[].name'
                                                                         : '완료',
                                                                         'children.$.children.$[].normal.fill': '#32BEBE'}})
            # cl.update_one({'BS.BSname': bsname},
            #               {'$set': {'BS.$.BSdone': 1, 'BS.$.ckname': ckname,
            #                         'BS.$.ckdate': datetime.now().strftime(
            #                             '%d일 %H시 %M분'.encode('unicode-escape').decode()).encode().decode(
            #                             'unicode-escape'),
            #                         'BS.$.checked': 1}})
            cl.update_one({'BS.BSname': bsname},
                          {'$set': {'BS.$.BSdone': 1,
                                    'BS.$.ckdate': datetime.now().strftime(
                                        '%d일 %H시 %M분'.encode('unicode-escape').decode()).encode().decode(
                                        'unicode-escape'),
                                    'BS.$.checked': 1}})
        return redirect(url_for('bs'))
    return redirect(url_for('login'))


@app.route('/bsdonecheckreset', methods=['POST'])
def bsdonecheckreset():
    user = get_current_user()
    if 'user' in session:
        cl = collectioncon('business')
        ch_cl = collectioncon('chart')
        if request.method == 'POST':
            bsname = request.form['bsname']
            ch_cl.update_one({'children.name': bsdic[bsname]}, {'$set': {'children.$.children.$[].name'
                                                                         : '점검중',
                                                                         'children.$.children.$[].normal.fill': '#6495ED'}})
            cl.update_one({'BS.BSname': bsname},
                          {'$set': {'BS.$.BSdone': 0,
                                    'BS.$.ckdate': '',
                                    'BS.$.checked': 0}})
        return redirect(url_for('bs'))
    return redirect(url_for('login'))


@app.route('/bsmanage', methods=['POST', 'GET'])
def bsmanage():
    title = '업무명 관리'
    user = get_current_user()
    if 'user' in session:
        cl = collectioncon('business')
        data = cl.find({}, {'_id': False})
        data = list(data)
        if request.method == 'POST':
            bdname = request.form['bdname']
            if bdname:
                data1 = cl.find_one({'BD': bdname}, {'_id': False})
                return data1
        return render_template('bsmanage.html', title=title, user=user, data=data)
    return redirect(url_for('login'))


@app.route('/test', methods=['POST', 'GET'])
def test():
    cl = collectioncon('test')
    data = cl.find({}, {'_id': False})
    if request.method == 'POST':
        bsname = request.form['bsname']
        # print(cl.update({'BS.BSname': bsname}, {'$set': {'BS.BSing': 1}}))
        print(cl.update({'BS.BSname': bsname}, {'$set': {'BS.$.BSing': 1}}))
        # cl.update({'BS.BSname': bsname}, {'_id': 0, 'BS': {'$elemMatch': {'BSname': bsname}}})
        aa = cl.find({'BS.BSname': bsname}, {'_id': 0, 'BS': {'$elemMatch': {'BSname': bsname}}})
        aa = list(aa)
        print(aa)
    return render_template('test.html', data=data)


@app.route('/bsrate')
def bsrate():
    title = '업무 서비스 기동'
    user = get_current_user()

    if 'user' in session:
        cl = collectioncon('business')
        data = list(cl.find({}, {'_id': False}))
        if request.method == 'POST':
            bdname = request.form['bdname']
            if bdname:
                data1 = cl.find_one({'BD': bdname}, {'_id': False})
                return data1
        return render_template('bsrate.html', title=title, user=user, data=data)
    return redirect(url_for('login'))


@app.route('/svrstarted', methods=['POST'])
def svrstarted():
    user = get_current_user()
    if 'user' in session and 'bcrs' in user['id']:
        hostname = request.form['hostname']
        cl = collectioncon('svr')
        cl.update({'hostname': hostname}, {'$set': {'started': 1}})
        return redirect(url_for('hostrate'))
    return redirect(url_for('login'))


@app.route('/bsratereset', methods=['GET'])
def bsratereset():
    user = get_current_user()
    if 'user' in session and 'bcrs' in user['id']:
        cl = collectioncon('business')
        ch_cl = collectioncon('chart')
        ch_cl.update_many({},
                          {'$set': {'children.$[].children.$[].name': '미점검',
                                    'children.$[].children.$[].normal.fill': '#FF7A85'}})
        while (True):
            valcheck = (cl.update({'BS.checked': 1},
                                  {'$set': {'BS.$.BSdone': 0, 'BS.$.BSing': 0,
                                            'BS.$.ckname': '', 'BS.$.ckdate': '',
                                            'BS.$.checked': 0}}))
            if (valcheck['nModified'] == 0):
                break
        return redirect(url_for('bsrate'))
    return redirect(url_for('login'))


@app.route('/hostratereset', methods=['GET'])
def hostratereset():
    user = get_current_user()
    if 'user' in session and 'bcrs' in user['id']:
        cl = collectioncon('svr')
        cl.update_many({}, {'$set': {'started': 0}})
        return redirect(url_for('hostrate'))
    return redirect(url_for('login'))


@app.route('/bsrate_chart')
def bsrate_chart():
    user = get_current_user()
    title = '업무 서비스 기동 진행'
    ch_cl = collectioncon('chart')
    OC = ch_cl.find({'name': '쇼핑몰'}, {'_id': 0})
    OC_total = ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'name': '쇼핑몰'}}])
    OC_total = len(list(OC_total))
    OC_uncheck_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                      {'$match': {'name': '쇼핑몰', 'children.children.name': '미점검'}}])
    OC_uncheck_num = len(list(OC_uncheck_num))
    OC_checking_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': '쇼핑몰', 'children.children.name': '점검중'}}])
    OC_checking_num = len(list(OC_checking_num))
    OC_checked_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                      {'$match': {'name': '쇼핑몰', 'children.children.name': '완료'}}])
    OC_checked_num = len(list(OC_checked_num))
    pos = ch_cl.find({'name': 'POS'}, {'_id': 0})
    pos_total = ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'name': 'POS'}}])
    pos_total = len(list(pos_total))
    pos_uncheck_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': 'POS', 'children.children.name': '미점검'}}])
    pos_uncheck_num = len(list(pos_uncheck_num))
    pos_checking_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                        {'$match': {'name': 'POS', 'children.children.name': '점검중'}}])
    pos_checking_num = len(list(pos_checking_num))
    pos_checked_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': 'POS', 'children.children.name': '완료'}}])
    pos_checked_num = len(list(pos_checked_num))
    prm = ch_cl.find({'name': 'PRM NEXT'}, {'_id': 0})
    prm_total = ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'name': 'PRM NEXT'}}])
    prm_total = len(list(prm_total))
    prm_uncheck_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': 'PRM NEXT', 'children.children.name': '미점검'}}])
    prm_uncheck_num = len(list(prm_uncheck_num))
    prm_checking_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                        {'$match': {'name': 'PRM NEXT', 'children.children.name': '점검중'}}])
    prm_checking_num = len(list(prm_checking_num))
    prm_checked_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': 'PRM NEXT', 'children.children.name': '완료'}}])
    prm_checked_num = len(list(prm_checked_num))
    scm = ch_cl.find({'name': 'SCM'}, {'_id': 0})
    scm_total = ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'name': 'SCM'}}])
    scm_total = len(list(scm_total))
    scm_uncheck_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': 'SCM', 'children.children.name': '미점검'}}])
    scm_uncheck_num = len(list(scm_uncheck_num))
    scm_checking_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                        {'$match': {'name': 'SCM', 'children.children.name': '점검중'}}])
    scm_checking_num = len(list(scm_checking_num))
    scm_checked_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': 'SCM', 'children.children.name': '완료'}}])
    scm_checked_num = len(list(scm_checked_num))
    fcm = ch_cl.find({'name': 'FCM'}, {'_id': 0})
    fcm_total = ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'name': 'FCM'}}])
    fcm_total = len(list(fcm_total))
    fcm_uncheck_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': 'FCM', 'children.children.name': '미점검'}}])
    fcm_uncheck_num = len(list(fcm_uncheck_num))
    fcm_checking_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                        {'$match': {'name': 'FCM', 'children.children.name': '점검중'}}])
    fcm_checking_num = len(list(fcm_checking_num))
    fcm_checked_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': 'FCM', 'children.children.name': '완료'}}])
    fcm_checked_num = len(list(fcm_checked_num))
    hrm = ch_cl.find({'name': 'HRM'}, {'_id': 0})
    hrm_total = ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'name': 'HRM'}}])
    hrm_total = len(list(hrm_total))
    hrm_uncheck_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': 'HRM', 'children.children.name': '미점검'}}])
    hrm_uncheck_num = len(list(hrm_uncheck_num))
    hrm_checking_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                        {'$match': {'name': 'HRM', 'children.children.name': '점검중'}}])
    hrm_checking_num = len(list(hrm_checking_num))
    hrm_checked_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': 'HRM', 'children.children.name': '완료'}}])
    hrm_checked_num = len(list(hrm_checked_num))
    common = ch_cl.find({'name': '공통'}, {'_id': 0})
    common_total = ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'name': '공통'}}])
    common_total = len(list(common_total))
    common_uncheck_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                          {'$match': {'name': '공통', 'children.children.name': '미점검'}}])
    common_uncheck_num = len(list(common_uncheck_num))
    common_checking_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                           {'$match': {'name': '공통', 'children.children.name': '점검중'}}])
    common_checking_num = len(list(common_checking_num))
    common_checked_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                          {'$match': {'name': '공통', 'children.children.name': '완료'}}])
    common_checked_num = len(list(common_checked_num))
    etc = ch_cl.find({'name': '기타'}, {'_id': 0})
    etc_total = ch_cl.aggregate(
        [{'$unwind': '$children'}, {'$project': {'_id': 0}}, {'$match': {'name': '기타'}}])
    etc_total = len(list(etc_total))
    etc_uncheck_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': '기타', 'children.children.name': '미점검'}}])
    etc_uncheck_num = len(list(etc_uncheck_num))
    etc_checking_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                        {'$match': {'name': '기타', 'children.children.name': '점검중'}}])
    etc_checking_num = len(list(etc_checking_num))
    etc_checked_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                       {'$match': {'name': '기타', 'children.children.name': '완료'}}])
    etc_checked_num = len(list(etc_checked_num))
    OC = list(OC)
    pos = list(pos)
    prm = list(prm)
    scm = list(scm)
    fcm = list(fcm)
    hrm = list(hrm)
    common = list(common)
    etc = list(etc)

    # bs_cl=collectioncon('chart')
    OC_uncheck_num = ch_cl.aggregate([{'$unwind': '$children'}, {'$project': {'_id': 0}},
                                      {'$match': {'name': '쇼핑몰', 'children.children.name': '미점검'}}])
    OC_uncheck_num = len(list(OC_uncheck_num))
    # cl = collectioncon('business')
    # data = list(cl.find({}, {'_id': False}))
    return render_template('bsrate_chart.html', title=title, user=user, OC=OC,
                           pos=pos, prm=prm, scm=scm, fcm=fcm, hrm=hrm, common=common, etc=etc,
                           OC_total=OC_total, pos_total=pos_total, scm_total=scm_total, fcm_total=fcm_total,
                           hrm_total=hrm_total,
                           common_total=common_total, etc_total=etc_total, prm_total=prm_total,
                           OC_uncheck_num=OC_uncheck_num, OC_checking_num=OC_checking_num,
                           OC_checked_num=OC_checked_num,
                           pos_uncheck_num=pos_uncheck_num, pos_checked_num=pos_checked_num,
                           pos_checking_num=pos_checking_num,
                           prm_uncheck_num=prm_uncheck_num, prm_checking_num=prm_checking_num,
                           prm_checked_num=prm_checked_num,
                           scm_uncheck_num=scm_uncheck_num, scm_checking_num=scm_checking_num,
                           scm_checked_num=scm_checked_num,
                           fcm_uncheck_num=fcm_uncheck_num, fcm_checking_num=fcm_checking_num,
                           fcm_checked_num=fcm_checked_num,
                           hrm_uncheck_num=hrm_uncheck_num, hrm_checking_num=hrm_checking_num,
                           hrm_checked_num=hrm_checked_num,
                           common_uncheck_num=common_uncheck_num, common_checking_num=common_checking_num,
                           common_checked_num=common_checked_num,
                           etc_uncheck_num=etc_uncheck_num, etc_checking_num=etc_checking_num,
                           etc_checked_num=etc_checked_num
                           )


@app.route('/map')
def map():
    user = get_current_user()
    title = '지도'

    return render_template('map.html', user=user, title=title)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
