# coding:utf-8
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage

from models import IDC, Asset, BisGroup
from juser.models import UserGroup
from connect import PyCrypt, KEY
from jumpserver.views import jasset_group_add, jasset_host_edit

cryptor = PyCrypt(KEY)


def index(request):
    return render_to_response('jasset/jasset.html', )


def jadd_host(request):
    login_types = {'L': 'LDAP', 'S': 'SSH_KEY', 'P': 'PASSWORD', 'M': 'MAP'}
    header_title, path1, path2 = u'添加主机 | Add Host', u'资产管理', u'添加主机'
    groups = []
    eidc = IDC.objects.all()
    egroup = BisGroup.objects.filter(type='A')
    eusergroup = UserGroup.objects.all()

    if request.method == 'POST':
        j_ip = request.POST.get('j_ip')
        j_idc = request.POST.get('j_idc')
        j_port = request.POST.get('j_port')
        j_type = request.POST.get('j_type')
        j_group = request.POST.getlist('j_group')
        j_active = request.POST.get('j_active')
        j_comment = request.POST.get('j_comment')
        j_idc = IDC.objects.get(name=j_idc)

        all_group = BisGroup.objects.get(name='ALL')
        for group in j_group:
            c = BisGroup.objects.get(name=group)
            groups.append(c)
        groups.append(all_group)

        if Asset.objects.filter(ip=str(j_ip)):
            emg = u'该IP %s 已存在!' %j_ip
            return render_to_response('jasset/host_add.html', locals(), context_instance=RequestContext(request))

        if j_type == 'M':
            j_user = request.POST.get('j_user')
            j_password = cryptor.encrypt(request.POST.get('j_password'))
            a = Asset(ip=j_ip, port=j_port,
                      login_type=j_type, idc=j_idc,
                      is_active=int(j_active),
                      comment=j_comment,
                      username_common=j_user,
                      password_common=j_password)
        else:
            a = Asset(ip=j_ip, port=j_port,
                      login_type=j_type, idc=j_idc,
                      is_active=int(j_active),
                      comment=j_comment)
        jasset_group_add(j_ip, j_ip, 'P')
        a.save()
        a.bis_group = groups
        a.save()
        smg = u'主机 %s 添加成功' %j_ip

    return render_to_response('jasset/host_add.html', locals(), context_instance=RequestContext(request))


def jadd_host_multi(request):
    header_title, path1, path2 = u'批量添加主机 | Add Hosts', u'资产管理', u'批量添加主机'
    login_types = {'LDAP': 'L', 'SSH_KEY': 'S', 'PASSWORD': 'P', 'MAP': 'M'}
    if request.method == 'POST':
        multi_hosts = request.POST.get('j_multi').split('\n')
        for host in multi_hosts:
            if host == '':
                break
            groups = []
            j_ip, j_port, j_type, j_idc, j_group, j_user_group, j_active, j_comment = host.split()
            j_idc = IDC.objects.get(name=j_idc)
            j_type = login_types[j_type]
            all_group = BisGroup.objects.get(name='ALL')
            j_group = j_group.split(',')
            for group in j_group:
                g = group.strip('[]')
                print g
                c = BisGroup.objects.get(name=g)
                groups.append(c)
            groups.append(all_group)

            if Asset.objects.filter(ip=str(j_ip)):
                emg = u'该IP %s 已存在!' %j_ip
                return render_to_response('jasset/host_add_multi.html', locals(), context_instance=RequestContext(request))

            if j_type == 'M':
                j_user = request.POST.get('j_user')
                j_password = cryptor.encrypt(request.POST.get('j_password'))
                a = Asset(ip=j_ip, port=j_port,
                          login_type=j_type, idc=j_idc,
                          is_active=int(j_active),
                          comment=j_comment,
                          username_common=j_user,
                          password_common=j_password)
            else:
                a = Asset(ip=j_ip, port=j_port,
                          login_type=j_type, idc=j_idc,
                          is_active=int(j_active),
                          comment=j_comment)
            jasset_group_add(j_ip, j_ip, 'P')
            a.save()
            a.bis_group = groups
            a.save()
        smg = u'批量添加添加成功'
        return HttpResponseRedirect('/jasset/host_list/')
    return render_to_response('jasset/host_add_multi.html', locals(), context_instance=RequestContext(request))


def batch_host_edit(request):
    if request.method == 'POST':
        len_table = request.POST.get('len_table')
        for i in range(int(len_table)):
            j_id = "editable["+str(i)+"][j_id]"
            j_ip = "editable["+str(i)+"][j_ip]"
            j_port = "editable["+str(i)+"][j_port]"
            j_idc = "editable["+str(i)+"][j_idc]"
            j_type = "editable["+str(i)+"][j_type]"
            j_group = "editable["+str(i)+"][j_group]"
            j_active = "editable["+str(i)+"][j_active]"
            j_comment = "editable["+str(i)+"][j_comment]"

            j_id = request.POST.get(j_id).strip()
            j_ip = request.POST.get(j_ip).strip()
            j_port = request.POST.get(j_port).strip()
            j_idc = request.POST.get(j_idc).strip()
            j_type = request.POST.get(j_type).strip()
            j_group = request.POST.getlist(j_group)
            j_active = request.POST.get(j_active).strip()
            j_comment = request.POST.get(j_comment).strip()
            print j_ip

            jasset_host_edit(j_id, j_ip, j_idc, j_port, j_type, j_group, j_active, j_comment)

        return render_to_response('jasset/host_list.html')


def jlist_host(request):
    header_title, path1, path2 = u'查看主机 | List Host', u'资产管理', u'查看主机'
    login_types = {'L': 'LDAP', 'S': 'SSH_KEY', 'P': 'PASSWORD', 'M': 'MAP'}
    posts = contact_list = Asset.objects.all().order_by('ip')
    print posts
    p = paginator = Paginator(contact_list, 20)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        contacts = paginator.page(page)
    except (EmptyPage, InvalidPage):
        contacts = paginator.page(paginator.num_pages)

    return render_to_response('jasset/host_list.html', locals(), context_instance=RequestContext(request))


def host_del(request, offset):
    print offset
    if offset == 'multi':
        len_list = request.POST.get("len_list")
        for i in range(int(len_list)):
            key = "id_list["+str(i)+"]"
            print key
            jid = request.POST.get(key)
            print jid
            Asset.objects.filter(id=jid).delete()
    else:
        jid = int(offset)
        Asset.objects.filter(id=jid).delete()
    return HttpResponseRedirect('/jasset/host_list/')


def host_edit(request, offset):
    actives = {1: u'激活', 0: u'禁用'}
    login_types = {'L': 'LDAP', 'S': 'SSH_KEY', 'P': 'PASSWORD', 'M': 'MAP'}
    header_title, path1, path2 = u'修改主机 | Edit Host', u'资产管理', u'修改主机'
    groups, e_group = [], []
    eidc = IDC.objects.all()
    egroup = BisGroup.objects.filter(type='A')
    for g in Asset.objects.get(id=int(offset)).bis_group.all():
        e_group.append(g)
    post = Asset.objects.get(id=int(offset))
    if request.method == 'POST':
        j_ip = request.POST.get('j_ip')
        j_idc = request.POST.get('j_idc')
        j_port = request.POST.get('j_port')
        j_type = request.POST.get('j_type')
        j_group = request.POST.getlist('j_group')
        j_active = request.POST.get('j_active')
        j_comment = request.POST.get('j_comment')
        j_idc = IDC.objects.get(name=j_idc)
        print j_group
        for group in j_group:
            c = BisGroup.objects.get(name=group)
            groups.append(c)

        a = Asset.objects.get(id=int(offset))

        if j_type == 'M':
            j_user = request.POST.get('j_user')
            j_password = cryptor.encrypt(request.POST.get('j_password'))
            a.ip = j_ip
            a.port = j_port
            a.login_type = j_type
            a.idc = j_idc
            a.is_active = j_active
            a.comment = j_comment
            a.username = j_user
            a.password = j_password
        else:
            a.ip = j_ip
            a.port = j_port
            a.idc = j_idc
            a.login_type = j_type
            a.is_active = j_active
            a.comment = j_comment

        a.save()
        a.bis_group = groups
        a.save()
        smg = u'主机 %s 修改成功' %j_ip
        return HttpResponseRedirect('/jasset/host_list')

    return render_to_response('jasset/host_edit.html', locals(), context_instance=RequestContext(request))


def jlist_ip(request, offset):
    header_title, path1, path2 = u'主机详细信息 | Host Detail.', u'资产管理', u'主机详情'
    print offset
    post = contact_list = Asset.objects.get(ip=str(offset))
    return render_to_response('jasset/jlist_ip.html', locals(), context_instance=RequestContext(request))


def jadd_idc(request):
    header_title, path1, path2 = u'添加IDC | Add IDC', u'资产管理', u'添加IDC'
    if request.method == 'POST':
        j_idc = request.POST.get('j_idc')
        j_comment = request.POST.get('j_comment')
        print j_idc,j_comment

        if IDC.objects.filter(name=j_idc):
            emg = u'该IDC已存在!'
            return render_to_response('jasset/idc_add.html', locals(), context_instance=RequestContext(request))
        else:
            smg = u'IDC:%s添加成功' %j_idc
            IDC.objects.create(name=j_idc, comment=j_comment)

    return render_to_response('jasset/idc_add.html', locals(), context_instance=RequestContext(request))


def jlist_idc(request):
    header_title, path1, path2 = u'查看IDC | List IDC', u'资产管理', u'查看IDC'
    posts = IDC.objects.all().order_by('id')
    return render_to_response('jasset/idc_list.html', locals(), context_instance=RequestContext(request))


def idc_del(request, offset):
    IDC.objects.filter(id=offset).delete()
    return HttpResponseRedirect('/jasset/idc_list/')


def jadd_group(request):
    header_title, path1, path2 = u'添加主机组 | Add Group', u'资产管理', u'添加主机组'
    if request.method == 'POST':
        j_group = request.POST.get('j_group')
        j_comment = request.POST.get('j_comment')

        if BisGroup.objects.filter(name=j_group):
            emg = u'该主机组已存在!'
            return render_to_response('jasset/group_add.html', locals(), context_instance=RequestContext(request))
        else:
            smg = u'主机组%s添加成功' %j_group
            BisGroup.objects.create(name=j_group, comment=j_comment, type='A')

    return render_to_response('jasset/group_add.html', locals(), context_instance=RequestContext(request))


def jlist_group(request):
    header_title, path1, path2 = u'查看主机组 | List Group', u'资产管理', u'查看主机组'
    posts = BisGroup.objects.filter(type='A').order_by('id')
    return render_to_response('jasset/group_list.html', locals(), context_instance=RequestContext(request))


def group_detail(request, offset):
    header_title, path1, path2 = u'主机组详情 | Group Detail', u'资产管理', u'主机组详情'
    login_types = {'L': 'LDAP', 'S': 'SSH_KEY', 'P': 'PASSWORD', 'M': 'MAP'}
    group_name = BisGroup.objects.get(id=offset).name
    b = BisGroup.objects.get(id=offset)
    posts = contact_list = Asset.objects.filter(bis_group=b).order_by('ip')
    p = paginator = Paginator(contact_list, 5)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        contacts = paginator.page(page)
    except (EmptyPage, InvalidPage):
        contacts = paginator.page(paginator.num_pages)
    return render_to_response('jasset/group_detail.html', locals(), context_instance=RequestContext(request))


def idc_detail(request, offset):
    header_title, path1, path2 = u'主机组详情 | Group Detail', u'资产管理', u'主机组详情'
    login_types = {'L': 'LDAP', 'S': 'SSH_KEY', 'P': 'PASSWORD', 'M': 'MAP'}
    idc_name = IDC.objects.get(id=offset).name
    b = IDC.objects.get(id=offset)
    posts = contact_list = Asset.objects.filter(idc=b).order_by('ip')
    p = paginator = Paginator(contact_list, 5)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        contacts = paginator.page(page)
    except (EmptyPage, InvalidPage):
        contacts = paginator.page(paginator.num_pages)
    return render_to_response('jasset/idc_detail.html', locals(), context_instance=RequestContext(request))


def group_del(request, offset):
    BisGroup.objects.filter(id=offset).delete()
    return HttpResponseRedirect('/jasset/group_list/')


def test(request):
    return render_to_response('jasset/test.html', locals())
