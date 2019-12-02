# -*- coding: utf-8 -*-
import argparse
import os
import re


# 所有支持的环境
env_dict = dict()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# constant
ip_str = "IP"
account_str = "Account"
password_str = "Password"


class ServerInfo(object):
    def __init__(self, ip, account, password):
        self.ip = ip
        self.account = account
        self.password = password


def init_config():
    '''
    初始化配置
    :return: none
    '''
    server_info_name = "server.info"
    child_files = os.listdir(CURRENT_DIR)
    for child in child_files:
        child_path = os.path.join(CURRENT_DIR, child)
        if not os.path.isdir(child_path):
            continue
        server_info_path = os.path.join(child_path, server_info_name)
        server_info = parse_server_info(server_info_path)
        if not server_info:
            continue
        env_dict[child] = server_info


def parse_server_info(server_path):
    """
    解析 server.info
    return: type - ServerInfo; 
    """
    if not os.path.isfile(server_path):
        return None

    with open(server_path, mode='r') as reader:
        lines = reader.readlines()

    if not lines:
        return None

    server_info = ServerInfo('', '', '')
    for line in lines:
        if line.strip().startswith("#"):
            continue
        pairs = re.split('[\t ]+', line.strip())

        if len(pairs) != 2:
            continue
        if pairs[0] == ip_str:
            server_info.ip = pairs[1]
        elif pairs[0] == account_str:
            server_info.account = pairs[1]
        elif pairs[0] == password_str:
            server_info.password = pairs[1]
    return server_info


class RemoteDeploy(object):
    def __init__(self):
        self.ssh_client = paramiko.SSHClient()

    def is_current_branch(self, branch):
        '''
        判断给定的分支是否是当前代码分支。
        :param branch: 输入的分支
        :return: True，是当前分支；False， 不是当前分支
        '''
        getbranch_cmds = list()
        getbranch_cmds.append('cd ' + BASE_DIR)
        getbranch_cmds.append('git branch')
        getbranch_merge_cmd = ' && '.join(getbranch_cmds)
        local_client = os.popen(getbranch_merge_cmd)
        out_str = local_client.read()
        local_client.close()
        is_current = False
        if out_str and re.findall('\* {0}'.format(branch), out_str):
            is_current = True

        return is_current

    def pack_code(self, branch, local_file):
        '''
        打包code
        :return: 成功，返回True; 否则 返回 False
        '''
        is_current = self.is_current_branch(branch)

        pack_cmds = list()
        pack_cmds.append('cd ' + BASE_DIR)  # 切换目录
        if not is_current:
            pack_cmds.append('git fetch origin {0}:{1}'.format(branch, branch))  # 同步分支code
        pack_cmds.append('git archive --format=tar {0} -o {1}'.format(branch, local_file))  # 打包code到tar
        pack_cmds.append('cd -')

        merged_cmd = ' && '.join(pack_cmds)
        result = os.system(merged_cmd)

        if result == 0:
            return True

        return False

    def unpack_remote(self, tar_name_without_extension):
        '''
        在远程主机上解压文件。文件路径，文件命名规则是约定俗称。
        :param tar_name_without_extension: 无tar的文件名
        :return:True 成功，否则 False
        '''
        unpack_cmds = list()
        unpack_cmds.append('mkdir -p /home/work/docker/{0}'.format(tar_name_without_extension))
        unpack_cmds.append('cd /home/work/docker/{0}'.format(tar_name_without_extension))
        unpack_cmds.append('tar -xf ../{0}.tar'.format(tar_name_without_extension))
        unpack_cmd_merge = ' && '.join(unpack_cmds)

        print('begin unpack in remote')
        stdin, stdout, stderr = self.ssh_client.exec_command(unpack_cmd_merge)
        print('end unpack')

        err_str = stderr.read()
        if not (err_str is None) and len(err_str) != 0:
            print('failed -- unpack')
            print(err_str)
            return False

        return True

    def create_code_tag(self, branch, version, message):
        '''
        给代码打tag并push到远程仓库
        :return: True，成功，False, 失败
        '''
        is_current = self.is_current_branch(branch)
        get_commit_id_cmds = list()
        get_commit_id_cmds.append('cd ' + BASE_DIR)
        if is_current:
            get_commit_id_cmds.append("git log | head -n 1 | awk '{print $2}'")
        else:
            get_commit_id_cmds.append("git log origin " + branch + " | head -n 1 | awk '{print $2}'")

        get_commit_id_merge = ' && '.join(get_commit_id_cmds)
        local_client = os.popen(get_commit_id_merge)
        commit_id = local_client.read().strip().split('\n')[-1]
        local_client.close()

        if not commit_id:
            print('获取commit id失败，请检查错误!')
            return False

        add_tag_cmds = list()
        add_tag_cmds.append('cd ' + BASE_DIR)
        add_tag_cmds.append('git tag -a v{0} -m "{1}" {2}'.format(version, message, commit_id))
        add_tag_cmds.append('git push origin --tags')
        add_tag_merge_cmd = ' && '.join(add_tag_cmds)
        result = os.system(add_tag_merge_cmd)
        if result != 0:
            print('打tag失败')
            return False
        return True

    def build_deploy_remote(self, code_path, environment, version, pwd):
        '''
        在远程主机上，build 镜像及部署code
        :param code_path:源码所在远程目录
        :param environment: 所发布到的环境
        :param version: 对应的镜像版本
        :param pwd: 对应的用户账号密码，可能需要sudo权限
        :return:True 成功，否则 False
        '''
        print('connecting...')
        stdin, stdout, stderr = self.ssh_client.exec_command('date')
        print(stdout.read())
        print('begin apply config')
        apply_path = os.path.join(code_path, '.dmp-for-k8s', environment, 'apply.sh').replace('\\', '/')
        apply_cmd = 'sh {0} {1}'.format(apply_path, version)
        stdin, stdout, stderr = self.ssh_client.exec_command(apply_cmd)
        err_str = stderr.read()
        if err_str and len(err_str) != 0:
            print('failed -- apply!')
            print(err_str)
            return False
        print('end apply config')

        print('begin build docker image. This will take some minitues, please wait patiently!')
        build_path = os.path.join(code_path, '.dmp-for-k8s', 'dockerbuild.sh').replace('\\', '/')
        build_cmd = 'sh {0} {1}'.format(build_path, version)
        stdin, stdout, stderr = self.ssh_client.exec_command(build_cmd)
        out_str = str(stdout.read())
        if not out_str or out_str.find('Successfully built') < 0:
            print('failed -- build docker')
            print(out_str)
            print('error:', stderr.read())
            return False
        print('end build')

        print('begin deploy docker')
        compose_dir = os.path.join(code_path, '.dmp-for-k8s', environment).replace('\\', '/')
        deploy_cmds = list()
        deploy_cmds.append('cd {0}'.format(compose_dir))
        deploy_cmds.append('echo {0} | sudo -S docker-compose up -d'.format(pwd))
        # deploy_cmds.append('echo {0} | sudo -S nvidia-docker-compose up -d -f {1}'.format(pwd, compose_name))
        deploy_merge_cmd = ' && '.join(deploy_cmds)
        stdin, stdout, stderr = self.ssh_client.exec_command(deploy_merge_cmd)
        err_str = str(stderr.read())
        out_str = str(stdout.read())
        if err_str and err_str.lower().find('error:') >= 0:
            print('failed -- deploy docker')
            print('stdout:' + out_str + '\nstderr:' + err_str)
            return False
        print('stdout:' + out_str + '\nstderr:' + err_str)
        print('end -- deploy')
        return True

    def ssh_scp_put(self, local_file, remote_file):
        '''
        通过ssh将本地文件复制到远程
        :param local_file: 本地文件路径
        :param remote_file: 远程文件路径
        :return: None
        '''
        print('connecting...')
        stdin, stdout, stderr = self.ssh_client.exec_command('date')
        print(stdout.read())
        print('begin put file')
        sftp = paramiko.SFTPClient.from_transport(self.ssh_client.get_transport())
        sftp = self.ssh_client.open_sftp()
        sftp.put(local_file, remote_file)
        print('end put')

    def ssh_scp_get(self, remote_file, local_file):
        '''
        通过ssh将远程文件复制到本地
        :param remote_file:远程文件
        :param local_file:本地文件
        :return:
        '''
        print('connecting...')
        stdin, stdout, stderr = self.ssh_client.exec_command('date')
        print(stdout.read())
        print('begin get file')
        sftp = paramiko.SFTPClient.from_transport(self.ssh_client.get_transport())
        sftp = self.ssh_client.open_sftp()
        sftp.get(remote_file, local_file)
        print('end get')

    def run(self, web_version, code_branch, environment):
        # web_version = '0.0.0.0'
        # code_branch = 'yuzhe'
        # environment = 'test'

        # project 名字
        project_name = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        print(environment)
        server_ip = env_dict[environment].ip if environment in env_dict else 'local'
        user_str = env_dict[environment].account if environment in env_dict else ''
        pwd_str = env_dict[environment].password if environment in env_dict else ''

        # 不带文件后缀的文件名
        tar_name = project_name + "_" + code_branch + "_" + environment

        tar_path = os.path.join(BASE_DIR, '{0}.tar'.format(tar_name)).replace('\\', '/')

        remote_base_dir = '/home/work/docker/'
        remote_tar_path = os.path.join(remote_base_dir, tar_name + ".tar").replace('\\', '/')

        if server_ip == 'local':
            print('本地不用通过远程部署。')
            return

        if not user_str or not pwd_str:
            print("用户名或者密码不能为空")
            return

        # 本地代码打包
        if not self.pack_code(code_branch, tar_path):
            print('打包失败，请根据错误提示修复！')
            return

        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(hostname=server_ip, port=22, username=user_str, password=pwd_str)

        # 复制打包文件到远程主机
        self.ssh_scp_put(tar_path, remote_tar_path)

        # 远程解压
        if not self.unpack_remote(tar_name):
            print('远程解压失败，请解决错误，再继续！')
            return

        # 运行远程构建及发布版本
        remote_code_path = os.path.join(remote_base_dir, tar_name).replace('\\', '/')
        result = self.build_deploy_remote(remote_code_path, environment, web_version, pwd_str)

        if not result:
            print('远程构建发布失败，请解决错误，再继续！')
            return
        print('远程发布成功')

        # if environment != "prod":
        #     return

        # # 自动打Tag，并提交
        # while True:
        #     message = str(input('正在打tag，请先输入版本信息，按回车结束！\n版本信息:')).strip()
        #     message = message.replace('\n', '**')
        #
        #     if message and message != '':
        #         break
        #     print('输入信息为空，请重新输入\n版本信息:')
        #
        # if not self.create_code_tag(branch=code_branch, version=web_version, message=message):
        #     print('自动给code打Tag失败，请手动打Tag!')
        #     return
        # print('打Tag成功')


def deploy_by_local(version, environment):
    print('begin apply config')
    apply_path = os.path.join(BASE_DIR, '.dmp-for-k8s', environment, 'apply.sh').replace('\\', '/')
    apply_cmd = 'sh {0} {1}'.format(apply_path, version)
    result = os.system(apply_cmd)
    if result != 0:
        print(u'can\'t apply config. ')
        print(u'you can run command by manual. ')
        print('command: {}'.format(apply_cmd))
        return
    print('begin build image')
    build_path = os.path.join(BASE_DIR, '.dmp-for-k8s', 'dockerbuild.sh').replace('\\', '/')
    build_cmd = 'sh {0} {1}'.format(build_path, version)
    result = os.system(build_cmd)
    if result != 0:
        print(u'can\'t build image. ')
        print(u'you can run command by manual. ')
        print('command: {}'.format(build_cmd))
        return
    print('begin deploy docker')
    compose_dir = os.path.join((BASE_DIR), '.dmp-for-k8s', environment).replace('\\', '/')
    deploy_cmds = list()
    deploy_cmds.append('cd {0}'.format(compose_dir))
    deploy_cmds.append('docker-compose up -d')
    # deploy_cmds.append('echo {0} | sudo -S nvidia-docker-compose up -d -f {1}'.format(pwd, compose_name))
    deploy_merge_cmd = ' && '.join(deploy_cmds)
    result = os.system(deploy_merge_cmd)
    if result != 0:
        print(u'can\'t deploy docker. ')
        print(u'you can run command by manual. ')
        print('command: {}'.format(deploy_merge_cmd))
        return
    print('deploy docker successfully')


def test_tag(code_branch, web_version):
    # python2 为 raw_input ; python3 为 input
    message = input('正在打tag，请先输入版本信息，按回车结束！\n版本信息:').strip()
    message = message.replace('\n', '**')
    remote_deploy = RemoteDeploy()

    if not remote_deploy.create_code_tag(branch=code_branch, version=web_version, message=message):
        print('自动给code打Tag失败，请手动打Tag!')
        return
    print('打Tag成功')


if __name__ == '__main__':
    init_config()
    env_choices_list = env_dict.keys()
    parser = argparse.ArgumentParser(description="远程自动部署发布脚本")
    parser.add_argument('--version', '-v', required=True)
    parser.add_argument('--branch', '-b', required=True)
    parser.add_argument('--environment', '-e', required=True, choices=env_choices_list)
    parser.add_argument('--type', '-t', required=False, choices=["local", "remote"])
    args = parser.parse_args()

    if not args.type or args.type == 'remote':
        # test_tag(args.branch, args.version)
        import paramiko

        remote_deploy = RemoteDeploy()
        remote_deploy.run(args.version, args.branch, args.environment)
    elif args.type == 'local':
        deploy_by_local(args.version, args.environment)
