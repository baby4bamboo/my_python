#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys,os,time
from optparse import OptionParser

version_from=sys.argv[2].strip()
version_to=sys.argv[3].strip()
days="1024"
mylist=[]
mylist2=[]
ptoollist=['webex-ptool-mac','webex-ptool-packaging','webex-productivitytools.mac','webex-productivitytools','webex-tp-endpoint','webex-tp-endpoint.mac','webex-calendarintegration']

ARTIFACTS="/cctg/cirepo/artifacts/"
WEBEX_ARTIFACTS_CLIENT="/cctg/cirepo/webex_artifacts/client"
WEBEX_ARTIFACTS_MS="/cctg/cirepo/webex_artifacts/meetingservice"
WEBEX_ARTIFACTS_PTOOL="/cctg/cirepo/webex_artifacts/ptool"
NOW="/Users/bayao/code_base/tmp/testArtifacts"
TEST="/cctg/cirepo/test/testArtifacts/client"
NOW2="/Users/bayao/code_base/tmp/testArtifacts/client"

class CopyArtifacts(object):
    '''
    The main entrance of script.
    '''
    def __init__(self, opts, args):
        self.opts = opts
        self.args = args

    def _CA_copyArtifacts(self, EP=0):
        RealPath=ARTIFACTS
        os.chdir(RealPath)
        if EP==0:
            command="sudo find . -maxdepth 1 -name "+version_from+"'*' -type d -ctime -"+days
        else:
            command="sudo find . -maxdepth 1 -name "+version_from+" -type d -ctime -"+days
    	mylist=os.popen(command).readlines()
        for path_from in  mylist:
            path_from = path_from.strip('\r\n')
            print path_from
            os.chdir(path_from)
            command="sudo find . -maxdepth 1 -type d -ctime -"+days
            mylist2=os.popen(command).readlines()
            if mylist2==[]:
                continue
            os.chdir(RealPath)
            path_to=path_from.replace(version_from,version_to)
            if os.path.exists(path_to):
                #command="sudo rm -rf "+path_to
                command="sudo mv "+path_to+" "+path_to+".bk"
                os.system(command)
            command="sudo mkdir "+path_to
            os.system(command)
            if path_from.endswith(version_from) or ".coverage" in path_from :
                command="sudo cp -rfp "+path_from+"/* "+path_to+"/"
            else:
                command="sudo mv "+path_from+"/* "+path_to+"/"
                print command
                os.system(command)
                command="sudo rm -rf "+path_from
            print command
            os.system(command)
            command="sudo chmod -R 777 "+path_to
            os.system(command)
            command="sudo chown -Rf ccatgbld:ccatgbld "+path_to
            os.system(command)
            

    def _CA_copyWebexArtifacts(self, path, EP=0):
        RealPath=path
        os.chdir(RealPath)
        command="sudo find . -maxdepth 1  -type d "
        mylist=os.popen(command).readlines()
        for repo_name in  mylist:
            repo_name = repo_name.strip('\r\n')
            print ""
            print repo_name
            os.chdir(repo_name)
            if EP==0:
                command="sudo find . -maxdepth 1 -name "+version_from+"'*' -type d -ctime -"+days
            else:
                command="sudo find . -maxdepth 1 -name "+version_from+" -type d -ctime -"+days
            mylist2=os.popen(command).readlines()
            if mylist2==[]:
                os.chdir(RealPath)
                continue
            print mylist2
            for path_from in mylist2:
                path_from = path_from.strip('\r\n')
                if path_from.endswith(version_from):
                    if os.path.exists(version_to):
                        #command="sudo rm -rf "+version_to
                        command="sudo mv "+version_to+" "+version_to+".bk"
                        os.system(command)
                    command="sudo mkdir "+version_to
                    os.system(command)
                    command="sudo cp -rfp "+version_from+"/* "+version_to+"/"
                    print command
                    os.system(command)
                else:
                    path_to=path_from.replace(version_from,version_to)
                    if os.path.exists(path_to):
                        #command="sudo rm -rf "+path_to
                        command="sudo mv "+path_to+" "+path_to+".bk"
                        os.system(command)
                    command="sudo mv "+path_from+" "+path_to
                    print command
                    os.system(command)
            command="sudo chmod -R 777 "+version_to+"*"
            os.system(command)
            command="sudo chown -Rf ccatgbld:ccatgbld "+version_to+"*"
            os.system(command)
            os.chdir(RealPath)

    def _CA_Backup_WebexArtifacts(self, path):
        mv_cp=sys.argv[2].strip()
        bk_from=sys.argv[3].strip()
        bk_to=sys.argv[4].strip()
        print mv_cp+" "+bk_from+" "+bk_to+" in "+path
        RealPath=path
        os.chdir(RealPath)
        command="sudo find . -maxdepth 1 -name '*'"+bk_from+"  -type d "
        print "sudo find . -maxdepth 1 -name '*'"+bk_from+"  -type d "
        mylist=os.popen(command).readlines()
        for path_from in  mylist:
            path_from = path_from.strip('\r\n')
            if not path_from.endswith(bk_from):
                continue
            path_to=path_from.replace(bk_from,bk_to)
            if os.path.exists(path_to):
                #command="sudo rm -rf "+path_to
                command="sudo mv "+path_to+" "+path_to+".bk"
                os.system(command)
            if mv_cp=='mv':
                command="sudo mv "+path_from+" "+path_to
                os.system(command)
            elif mv_cp=='cp':
                command="sudo cp -rfp "+path_from+" "+path_to
                os.system(command)
            print command
            command="sudo chmod -R 777 "+path_to
            os.system(command)
            command="sudo chown -Rf ccatgbld:ccatgbld "+path_to
            os.system(command)

    def _CA_copyWebexArtifactsPtool(self, EP=0):
        RealPath=WEBEX_ARTIFACTS_PTOOL
        os.chdir(RealPath)
        mylist=ptoollist
        for repo_name in  mylist:
            repo_name = repo_name.strip('\r\n')
            print ""
            print repo_name
            os.chdir(repo_name)
            if EP==0:
            command="sudo find . -maxdepth 1 -name "+version_from+"'*' -type d -ctime -"+days
                else:
            command="sudo find . -maxdepth 1 -name "+version_from+" -type d -ctime -"+days
                mylist2=os.popen(command).readlines()
            if mylist2==[]:
                os.chdir(RealPath)
                continue
            print mylist2
            for path_from in mylist2:
                path_from = path_from.strip('\r\n')
                if path_from.endswith(version_from):
                    if os.path.exists(version_to):
                        #command="sudo rm -rf "+version_to
                        command="sudo mv "+version_to+" "+version_to+".bk"
                        os.system(command)
                    command="sudo mkdir "+version_to
                    os.system(command)
                    command="sudo cp -rfp "+version_from+"/* "+version_to+"/"
                    print command
                    os.system(command)
                else:
                    path_to=path_from.replace(version_from,version_to)
                    if os.path.exists(path_to):
                        #command="sudo rm -rf "+path_to
                        command="sudo mv "+path_to+" "+path_to+".bk"
                        os.system(command)
                    command="sudo mv "+path_from+" "+path_to
                    print command
                    os.system(command)
            command="sudo chmod -R 777 "+version_to+"*"
            os.system(command)
            command="sudo chown -Rf ccatgbld:ccatgbld "+version_to+"*"
            os.system(command)
            os.chdir(RealPath)

    def _CA_removeWebexArtifacts(self):
        RealPath=WEBEX_ARTIFACTS
        os.chdir(RealPath)
        command="sudo find . -maxdepth 1  -type d "
        mylist=os.popen(command).readlines()
        for repo_name in  mylist:
            print repo_name
            repo_name = repo_name.strip('\r\n')
            os.chdir(repo_name)
            command="sudo find . -maxdepth 1 -name "+version_from+"'*' -type d"
            mylist2=os.popen(command).readlines()
            if mylist2==[]:
                os.chdir(RealPath)
                continue
            print mylist2
            for path_from in mylist2:
                command="sudo rm  -rf "+path_from
                os.system(command)
            os.chdir(RealPath)

    def run(self):
        if self.opts.ep != '':
            EP=1
        else:
            EP=0
    	if self.opts.artifacts != '':
            self._CA_copyArtifacts(EP)
        elif self.opts.webex_artifacts != '':
            self._CA_copyWebexArtifacts(WEBEX_ARTIFACTS_CLIENT,EP)
            self._CA_copyWebexArtifactsPtool(EP)
            self._CA_copyWebexArtifacts(WEBEX_ARTIFACTS_MS,EP)
        elif self.opts.bk != '':  
            self._CA_Backup_WebexArtifacts(WEBEX_ARTIFACTS_CLIENT)
            print "-------------------------------------------"
            self._CA_Backup_WebexArtifacts(WEBEX_ARTIFACTS_MS)
        elif self.opts.remove != '':
            self._CA_removeWebexArtifacts()
        else:
        	print "error"

def ParserOpts(argv):
        parser = OptionParser()
        parser.usage = ''
        parser.description = ''
        parser.add_option('-a', '--artifacts',
                          help='update artifacts version to newest ',
                          dest='artifacts', default='')
        parser.add_option('-w', '--webex',
                          help='update webex_artifacts version to newest ',
                          dest='webex_artifacts', default='')
        parser.add_option('-r', '--remove',
                          help='remove webex_artifacts version',
                          dest='remove', default='')
        parser.add_option('-b', '--bk',
                          help='backup webex_artifacts version by copy/move',
                          dest='bk', default='')
        parser.add_option('-e', '--ep',
                          help='This is only for EP copy，don not need copy feature',
                          dest='ep', default='')
       
        return parser.parse_args(args=argv)

    

if __name__ == '__main__':   
    start_time = time.time() 
    opts, args = ParserOpts(sys.argv)
    WDM = CopyArtifacts(opts, args)
    WDM.run()



