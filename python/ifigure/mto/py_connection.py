from __future__ import print_function
from ifigure.mto.treedict import TreeDict
import ifigure
import os
from ifigure.utils.cbook import isInMainThread, LoadImageFile
import shlex
import subprocess
import threading
import traceback
import wx
import time

from ifigure.utils.get_username import get_username
usr = get_username()

sltime = 0.25  # sleep time during wait



def run_ssh_wait_and_retry(args, kargs, verbose=False):
    retry = 5
    ktry=0
    while (ktry < retry):
        try:
            #if verbose:
            #    p = subprocess.Popen(args,
            #                         universal_newlines=True,
            #                         **kargs)
            #else:
            p = subprocess.Popen(args, stderr=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True,
                                 **kargs)
        except:
            print(traceback.format_exc())

        while p.poll() == None:
            #if isInMainThread(): wx.Yield()
            time.sleep(sltime)
        stat = p.wait()

        err=p.stderr.readlines()
        success=True
        for x in err:
            if x.find('reset connection') != -1:
                print(x)
                success=False
            elif x.find('lost connection') != -1:
                print(x)
                success=False
            elif len(x)>0:
                print(x)
                #success=False                
            else:
                pass
        if success: break
        
        ktry=ktry+1
        print("retrying communicaiton : (" + str(ktry) + ")")
    return p
        
def run_ssh_no_retry(args, kargs, verbose=False):
    try:
        if verbose:
            p = subprocess.Popen(args,
                                 universal_newlines=True,
                                 **kargs)
        else:
            p = subprocess.Popen(args, stderr=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True,
                                 **kargs)
    except:
        print(traceback.format_exc())

    return p

        
class PyConnection(TreeDict):
    def __init__(self, *args, **kargs):
        super(PyConnection, self).__init__(*args, **kargs)
        self.setvar('server', 'cmodws60')
        self.setvar('port', 22)
        self.setvar('user', usr)
        self.setvar('use_ssh', True)
        self.setvar('verbose', True)
        self.setvar('queue_type', 'sbatch')
        self.setvar('check', False)

    @classmethod
    def isPyConnection(self):
        return True

    @classmethod
    def get_namebase(self):
        return 'connection'

    @classmethod
    def load_classimage(self):
        from ifigure.ifigure_config import icondir as path
        idx1 = LoadImageFile(path, 'world_link.png')
        return [idx1]

    def tree_viewer_menu(self):
        # return MenuString, Handler, MenuImage
        menu = [('Setting...', self.onSetting, None),
                ('---', None, None), ]
        return menu + super(PyConnection, self).tree_viewer_menu()

    def setSetting(self, value):
        self.setvar('use_ssh', value[1][0])
        self.setvar('server', str(value[1][1][0]))
        self.setvar('port', int(value[1][1][1]))
        self.setvar('user', str(value[1][1][2]))
        self.setvar('queue_type', str(value[2]))
        self.setvar('nocheck', not bool(value[3]))        

    def onSetting(self, evt=None):
        server, port, user, use_ssh, queue_type, nocheck = self.getvar('server', 'port',
                                                              'user',
                                                              'use_ssh',
                                                                       'queue_type',
                                                                        'nocheck' )
        if use_ssh is None:
            use_ssh = True
        if server is None:
            server = 'cmodws60.psfc.mit.edu'
        if port is None:
            port = 22
        if user is None:
            user = usr  # os.getnev('USER')
        if queue_type is None:
            queue_type = 'sbatch'  # os.getnev('USER')
        if nocheck is None:
            nocheck = False

        s_queue = {"style": wx.CB_DROPDOWN,
                   "choices": ["sbatch", "qsub"]}
        l2 = [["server", str(server), 0],
              ["port", str(port), 0],
              ["user", str(user), 0], ]

        l1 = [["", "SSH connection", 2],
              [None, (use_ssh, [server, str(port), user]), 27,
               ({'text': 'use SSH'}, {'elp': l2})],
              ["queue type", str(queue_type), 4, s_queue], 
              [None, not nocheck, 3, {"text":"connection check/retry"}], ]        
        proj_tree_viewer = wx.GetApp().TopWindow.proj_tree_viewer
        proj_tree_viewer.OpenPanel(l1, self, 'setSetting',
                                   title='Connection setting')

    def PutFile(self, src, dest, nowait=False):
        '''
        put a file in a remote server
        '''
        server, port, user, use_ssh, nocheck = self.getvar('server', 'port',
                                                  'user', 'use_ssh', 'nocheck')
        
        if nocheck is None:  nocheck = False

        if use_ssh:
            command = 'scp -P '+str(port) + ' ' + src + \
                ' ' + user + '@' + server+':' + dest
            args = shlex.split(command)
            args = command
            kargs = {'shell': True}
        else:
            command = 'cp ' + src + ' ' + dest
            args = command
            kargs = {'shell': True}
        if self.getvar('verbose'):
            print(command)

        verbose=self.getvar('verbose')
        if verbose: print(command)        
        if nowait:
            p = run_ssh_no_retry(args, kargs, verbose=verbose)
        elif nocheck:
            p = run_ssh_no_retry(args, kargs, verbose=verbose)
            p.wait()
        else:
            p = run_ssh_wait_and_retry(args, kargs, verbose=verbose)
        return p
        
    def GetFile(self, src, dest, nowait=False, nocheck=False):
        '''
        get a file in a remote server
        '''
        server, port, user,  use_ssh, nocheck = self.getvar('server', 'port',
                                                   'user', 'use_ssh', 'nocheck')
        if nocheck is None:  nocheck = False
        if use_ssh:
            command = 'scp -P '+str(port) + ' ' + user + \
                '@'+server+':'+src + ' ' + dest
            args = shlex.split(command)
            kargs = {}
            args = command
            kargs = {'shell': True}
        else:
            command = 'cp ' + src + ' ' + dest
            args = command
            kargs = {"shell": True}

        verbose=self.getvar('verbose')

        if verbose: print(command)
        if nowait:
            p = run_ssh_no_retry(args, kargs, verbose=verbose)
        elif nocheck:
            p = run_ssh_no_retry(args, kargs, verbose=verbose)
            p.wait()
        else:
            p = run_ssh_wait_and_retry(args, kargs, verbose=verbose)
        return p
        '''            
        try:
            if self.getvar('verbose'):
                p = subprocess.Popen(args,
                                     universal_newlines=True,                                     
                                     **kargs)

            else:
                p = subprocess.Popen(args, stderr=subprocess.STDOUT,
                                     stdout=subprocess.PIPE,
                                     universal_newlines=True,
                                     **kargs)
        except:
            print(traceback.format_exc())

        if not nowait:
            while p.poll() == None:
                #if isInMainThread(): wx.Yield()
                time.sleep(sltime)
            # print p.wait()
        return p
        '''
        
    def Execute(self, command, nowait=False, nocheck=False):
        server, port, user,  use_ssh, nocheck = self.getvar('server', 'port',
                                                   'user', 'use_ssh', 'nocheck')
        if nocheck is None:  nocheck = False
        if use_ssh:
            command = 'ssh -x -p '+str(port)+' ' + \
                user+'@'+server + ' "' + command + '"'
            args = shlex.split(command)
            kargs = {}
            args = command
            kargs = {'shell': True}
        else:
            args = command
            kargs = {"shell": True}


        verbose=self.getvar('verbose')

        if verbose: print(command)
        if nowait:
            p = run_ssh_no_retry(args, kargs, verbose=verbose)
        elif nocheck:
            p = run_ssh_no_retry(args, kargs, verbose=verbose)
            p.wait()
        else:
            p = run_ssh_wait_and_retry(args, kargs, verbose=verbose)
        return p

        '''    
        if self.getvar('verbose'):
            print(command)

        try:
            p = subprocess.Popen(args, stderr=subprocess.STDOUT,
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True,
                                 **kargs)
        except:
            print(traceback.format_exc())
        print('a new process (id =' + str(p.pid) + ') is running')
        if not nowait:
            while p.poll() == None:
                #if isInMainThread(): wx.Yield()
                time.sleep(sltime)
            print(p.wait())
        return p
        '''
