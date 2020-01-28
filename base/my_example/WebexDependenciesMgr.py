import sys
import os
import time
from optparse import OptionParser
import xml.dom.minidom
import platform
import urllib2
import getpass
import re,commands

CIREPO_CENTRAL_VERSION = "33.0.0"
cctg_repo = os.environ.get('CCTG_REPO')
if cctg_repo == "/cctg/cirepo-rcdn":
    CIREPO_CENTRAL_HTTP_ARTIFACTS = "http://cctg-rcdn-cirepo.cisco.com/cirepo/artifacts/"
    CIREPO="/cctg/cirepo-rcdn/artifacts/"+CIREPO_CENTRAL_VERSION
else:
    #CIREPO_CENTRAL_HTTP_ARTIFACTS = "http://ccatg-build2.cisco.com/cirepo/artifacts/"
    CIREPO_CENTRAL_HTTP_ARTIFACTS = "http://cctg-cirepo.cisco.com/cirepo/artifacts/"
    CIREPO="/cctg/cirepo/artifacts/"+CIREPO_CENTRAL_VERSION
    
CIREPO_HTTP=CIREPO_CENTRAL_HTTP_ARTIFACTS+CIREPO_CENTRAL_VERSION
FILENAME="dependencies.xml"
CIREPO_CENTRAL_HTTP_URL = CIREPO_CENTRAL_HTTP_ARTIFACTS + CIREPO_CENTRAL_VERSION
LOG_FILE    = "headerlibs.log"
WME_WIN32_ZIP   = "wme4train_win32"
WME_MAC_ZIP     = "wme4train_macos"  # need improve later for wme name rule
LATEST_TXT  = "latest.txt"
WGET="wget -o- "
opener=None
XMLFILE="revisions_1.0.xml"
DEPINFO="depinfo.txt"

class WebexDependenMgr(object):
    '''
    The main entrance of script.
    '''
    def __init__(self, opts, args):
        self.opts = opts
        self.args = args

    def _PrepareXML(self):
        filename = FILENAME
        if self.opts.myos=="":
            build_os="windows"
        else:
            build_os=self.opts.myos
        if not os.path.exists(filename):
            file_path = '../build/' + build_os
            filename= file_path  + '/'+self.opts.platform + '/' + FILENAME
            if not os.path.exists(filename):
                filename= file_path + '/' + FILENAME
                if self.opts.list == '' and self.opts.talist == '' and not os.path.exists(filename):
                    print "Warning : Can not find dependencies.xml , so do nothing..."
                    return ""
        return filename
        

    def _ParserXML(self,filename):
        WDMdict={}
        DOMTree = xml.dom.minidom.parse(filename)
        config = DOMTree.documentElement

        dependencies = config.getElementsByTagName("dependencies")[0]
        ds = dependencies.getElementsByTagName("dependency")
        i=0
        for dependency in ds:
            if dependency.hasAttribute("reponame"):
                WDMdict[i] = dependency.getAttribute("reponame")
            i=i+1
        WDMdict['.type'] = 'include_libs'
        if dependencies.hasAttribute('type'):
            WDMdict['.type'] = dependencies.getAttribute('type') 


        if config.getElementsByTagName("tadependents"):
            tadependencies = config.getElementsByTagName("tadependents")[0]
            tads = tadependencies.getElementsByTagName("tadependent")
            tastring=''
            for tadependency in tads:
                if tadependency.hasAttribute("reponame"):
                    if tastring != '':
                        tastring = tastring + ','
                    tastring = tastring + tadependency.getAttribute("reponame")
            WDMdict['talist'] = tastring
        else:
            WDMdict['talist'] = ''

        repoconfig = config.getElementsByTagName("repoconfig")[0]
        WDMdict["windowsSDK"]="v7.1A"
        if repoconfig.hasAttribute("windowsSDK"):
            WDMdict["windowsSDK"]=repoconfig.getAttribute("windowsSDK")
        return WDMdict

    def revisions(self,download_path,download_reponame,latest):
        component = download_reponame
        buildtype = "none"
        buildnumber = latest.split('.')[-1]
        tmp = latest.split('-')[-1]
        version_in_latest = '.'.join(tmp.split('.')[0:-1])
        dependency_component = '-'.join(latest.split('-')[0:-1])
        filename = download_path+"/build_history."+dependency_component+"."+version_in_latest+".txt"
        command = 'egrep -A 4 "^Buildnumber: '+buildnumber+'" '+filename+' | grep "@" | tail -1'
        revisions=commands.getstatusoutput(command)[1]

        f=open(XMLFILE,'aw+')
        xml_str="<component>"+"\n"+"\t<name>"+component+"</name>"+"\n"+"\t<version>"+version_in_latest+"</version>"+"\n"+"\t<buildtype>"+buildtype+"</buildtype>"+"\n"+"\t<buildnumber>"+buildnumber+"</buildnumber>"+"\n"+"\t<revision>"+revisions+"</revision>"+"\n"+"</component>"+"\n"
        f.write(xml_str)
        f.close()

    def depinfo(self,dep_path):
        dep_path=dep_path+"\n"
        f=open(DEPINFO,'aw+')
        f.write(dep_path)
        f.close()
        
    def get_tag_list(self):
        tag_list=[]
        if self.opts.tag != '':
            tag_list=self.opts.tag.split(',')
        else:
            tag_list=['latest.txt']
        return tag_list

    def _WDM_download(self):
        global CIREPO
        if self.opts.version != '':
            CIREPO="/cctg/cirepo/artifacts/"+self.opts.version
            bv = self.opts.version.split('.')
            base_version=bv[0]+'.'+bv[1]+'.'+bv[2]
        filename=self._PrepareXML()
        if filename == "":
            return
        mydict=self._ParserXML(filename)
        if self.opts.myos == 'mac' or self.opts.myos == 'linux' or self.opts.myos == 'java':
            myos = '.' + self.opts.myos
            print "myos is "+ myos
            for i in mydict:
                if i == 'windowsSDK' or i == 'talist' or re.match("^\.", str(i)):
                    continue 
                if self.opts.version != '':
                    CIREPO="/cctg/cirepo/artifacts/"+self.opts.version

                tag_list=self.get_tag_list()
                is_download_success=False
                for TAG in tag_list:
                    if is_download_success == True:
                        break
                    if TAG==tag_list[-1]:
                        is_last_tag=True
                    else:
                        is_last_tag=False
                    if not os.path.exists(CIREPO +"/" + mydict[i] + myos +"/" + TAG):
                        CIREPO="/cctg/cirepo/artifacts/"+base_version
                    if os.path.exists(CIREPO +"/" + mydict[i] + myos +'/' + TAG):
                        f=open(CIREPO +"/" + mydict[i] + myos +"/" + TAG,"r")
                        file_name =  f.read().strip()
                        f.close()
                        is_download_success=True
                        print('%-30s%-30s' % (mydict[i],file_name))
                    else:
                        if(is_last_tag):
                            print "Download error ! Can't find in "+CIREPO +"/" + mydict[i] + myos +'/' + TAG
                            sys.exit(1)
                        else:
                            continue
                
                if self.opts.revisions != "":
                    if os.path.isfile(self.opts.revisions):
                        f = open(self.opts.revisions, "a")
                    else:
                        f = open(self.opts.revisions, "w")
                    version_build = file_name.split('-')[-1].split('.')
                    rev_version = '.'.join(version_build[:-1])
                    rev_build = version_build[-1]
                
                    history_file = CIREPO + '/' + mydict[i] + myos +'/build_history.' + mydict[i] + myos + '.' + rev_version + '.txt'
                    build_start = False
                    if os.path.isfile(history_file):
#                       with open(history_file, 'r') as file:
                        file = open(history_file, 'r')
                        for line in file:
                            line=line.strip()
                            if line == "Buildnumber: " + rev_build:
                                build_start = True
                            if "@" in line:
                                f.write("<component>\n\t<name>" + mydict[i] + myos + "</name>\n\t<version>" + rev_version + \
                                      "</version>\n\t<buildnumber>" + rev_build + "</buildnumber>\n\t<revision>" + line + "</revision>\n</component>\n")
                                break
                        file.close()
                    f.close()
                    
                if self.opts.platform=="":
                    build_platform=""
                else:
                    build_platform="."+self.opts.platform
                if mydict[i] != 'wme':
                    if self.opts.myos == 'java':
                        command = "cp " + CIREPO +"/" + mydict[i]+ myos + "/" +file_name + "/" +file_name + ".java.zip ./"
                    else:
                        command = "cp " + CIREPO +"/" + mydict[i]+ myos + "/" +file_name + "/" +file_name +build_platform+ "." + mydict['.type'] + ".zip ./"
                    print command
                    flag = os.system(command)
                    if flag != 0:
                        sys.exit(1)
                    command = "unzip -o -q "+mydict[i] + "*.zip"
                    os.system(command)
                else:
                    command = "cp " + CIREPO +"/" + mydict[i]+ myos + "/" +file_name + "/"+ 'wme4train_macos'+'*'+'.tar.gz ./'
                    print command
                    os.system(command)
                    command = "mkdir wme"
                    os.system(command)
                    command = "tar -zxvf "+mydict[i] + "*.tar.gz -C wme"
                    os.system(command)
                if  os.path.exists(CIREPO):
                    download_path=CIREPO +"/" + mydict[i]+ myos 
                    self.revisions(download_path,mydict[i]+ myos,file_name)
                    dep_path=download_path+'/'+ file_name
                    self.depinfo(dep_path)
        else:
            myos = '.windows'
            print "myos is "+ myos
            for i in mydict:
                if i == 'windowsSDK' or i == 'talist' or re.match("^\.", str(i)):
                    continue
                print 'start download '+mydict[i]
                if ".coverage" in self.opts.version:
                    CIREPO="/cctg/cirepo/artifacts/"+base_version
                elif self.opts.version != '':
                    CIREPO="/cctg/cirepo/artifacts/"+self.opts.version

                tag_list=self.get_tag_list()
                is_download_success=False
                for TAG in tag_list:
                    if is_download_success == True:
                        break
                    if TAG==tag_list[-1]:
                        is_last_tag=True
                    else:
                        is_last_tag=False
                    if not os.path.exists(CIREPO +"/" + mydict[i] +"/"+TAG):
                        CIREPO="/cctg/cirepo/artifacts/"+base_version
                    if os.path.exists(CIREPO +"/" + mydict[i]+'/' + TAG):
                        f=open(CIREPO +"/" + mydict[i] +"/"+TAG,"r")
                        file_name =  f.read().strip()
                        f.close()
                        is_download_success=True
                    else:
                        if(is_last_tag):
                            print "Download error ! Can't find in "+CIREPO +"/" + mydict[i] +"/"+TAG
                            sys.exit(1)
                        else:
                            continue
                
                if mydict[i] != 'wme': 
                    command = "cp " + CIREPO +"/" + mydict[i]+ "/" +file_name + "/" +file_name  + "." + mydict['.type'] + ".zip ./"
                    print command
                    flag2=os.system(command)
                    if flag2 != 0:
                        command = "cp " + CIREPO +"/" + mydict[i]+ "/" +file_name + "/" +file_name + myos + "." + mydict['.type'] + ".zip ./"
                        print command
                        flag3 = os.system(command)
                        if flag3 != 0:
                            sys.exit(1)
                    command = "unzip -o -q "+file_name + "." + mydict['.type'] + ".zip"
                    os.system(command)

                    bin_path = CIREPO +"/" + mydict[i]+ "/" +file_name + "/" +file_name  + ".bin.zip"
                    flag4 = os.path.isfile(bin_path)
                    if flag4 == True:
                        command = "cp " + CIREPO +"/" + mydict[i]+ "/" +file_name + "/" +file_name  + ".bin.zip ./"
                        os.system(command)
                        command = "unzip -o -q "+file_name + ".bin.zip"
                        os.system(command)
                else:
                    command = "cp " + CIREPO +"/" + mydict[i]+ "/" +file_name + "/" + 'wme4train_win32'+'*'+'.zip ./'
                    print command
                    os.system(command)
                    command = "unzip -o -q -d wme "+mydict[i] + "*.zip"
                    os.system(command)
                if  os.path.exists(CIREPO):
                    download_path=CIREPO +"/" + mydict[i]
                    self.revisions(download_path,mydict[i],file_name)
                    dep_path=download_path+'/'+ file_name
                    self.depinfo(dep_path)




    def _WDM_Dev_writelog(self,log):
        # write log time.time().strftime("%a, %d %b %Y %H:%M:%S" )
        log_command =  log + "\n"
        logfile = open(LOG_FILE, "a+")
        logfile.write(log_command)
        logfile.close()

    def _WDM_Dev_flushlog(self):
        logfile = open(LOG_FILE, "w")
        logfile.close()

    def _WDM_Dev_getHeaderLibsNameFromLatestFile(self):
        f=open(self.opts.tag,"r")
        file_name =  f.read().strip()
        f.close()
        
        return file_name

    def _WDM_Dev_DelLatestFile(self):
        command ="del %s" % self.opts.tag
        os.system(command)

    def _WDM_Dev_DelLatestFile_osx(self):
        command ="rm %s" % self.opts.tag
        os.system(command)

    def _WDM_Dev_downloadWME_Mac(self, cirepo_http, reponame,myos, file_name):
        wme_ver = self._WDM_Dev_GetWmeVersionNumber(file_name)
        if  wme_ver == '':
            print "can not get wme version number"
            return

        flag = self._WDM_wget(cirepo_http +"/" + reponame+ myos + "/" +file_name + "/"+ WME_MAC_ZIP +'-' + wme_ver +'.tar.gz')
        #command = WGET + cirepo_http +"/" + reponame+ myos + "/" +file_name + "/"+ WME_MAC_ZIP +'-' + wme_ver +'.tar.gz'
        #flag = os.system(command)
        if flag != 0:
            print "download wme fail"
            return
        command = "mkdir wme"
        os.system(command)
        command = "tar -zxvf "+reponame + "*.tar.gz -C wme"
        os.system(command)
        return

    def _WDM_Dev_GetWmeVersionNumber(self, wme_file_name):
        #wme-31.0.0.519 
        if wme_file_name == '':
            return ''

        return wme_file_name[wme_file_name.rfind('.') + 1 : len(wme_file_name)]

    def _WDM_Dev_downloadWME_Win(self, cirepo_http, reponame, file_name):
        self._WDM_Dev_DelLatestFile()
        command = 'mkdir wme'
        os.system(command)
        wme_ver = self._WDM_Dev_GetWmeVersionNumber(file_name)
        if  wme_ver == '':
            print "can not get wme version number"
            return

        ret = self._WDM_wget(cirepo_http +"/" + reponame+ "/" +file_name + "/" + WME_WIN32_ZIP + "-" + wme_ver + ".zip")
        #command = WGET + cirepo_http +"/" + reponame+ "/" +file_name + "/" + WME_WIN32_ZIP + "-" + wme_ver + ".zip"
        #ret = os.system(command)
        if ret != 0:
            log = "wme download fail " + command
            self._WDM_Dev_writelog(log)
            print log
            return

        command = "unzip -o -d wme " + reponame + "*.zip "
        os.system(command)
        return

    def _WDM_Dev_download_one(self,realCIREPO_HTTP,reponame, myos):
        #return # for test WME
        file_name =  self._WDM_Dev_getHeaderLibsNameFromLatestFile()
        self._WDM_Dev_DelLatestFile()
        
        flag2 = self._WDM_wget(realCIREPO_HTTP +"/" + reponame+ "/" +file_name + "/" + file_name + ".include_libs.zip")
        #command = WGET + realCIREPO_HTTP +"/" + reponame+ "/" +file_name + "/" + file_name + ".include_libs.zip"
        #print command
        #flag2=os.system(command)
        if flag2 != 0:
            self._WDM_wget(realCIREPO_HTTP +"/" + reponame+ "/" +file_name + "/" + file_name + myos + ".include_libs.zip")
            #command = WGET + realCIREPO_HTTP +"/" + reponame+ "/" +file_name + "/" + file_name + myos + ".include_libs.zip"
            #os.system(command)
        
        #self._WDM_Dev_writelog(command)

        command = "unzip -o "+reponame + "*.zip"
        os.system(command)
        return

    def _WDM_Dev_download_latestfile(self,realCIREPO_HTTP, reponame,myos):
        print 'start download '+reponame
        flag = self._WDM_wget(realCIREPO_HTTP +"/" +reponame + myos +'/' + self.opts.tag)
        #command = WGET +realCIREPO_HTTP +"/" +reponame + myos +'/' + LATEST_TXT
        #flag = os.system(command)
        if myos != '.windows':
            return flag

        #try again for windows
        if flag != 0:
            flag = self._WDM_wget(realCIREPO_HTTP +"/" +reponame + '/' + self.opts.tag)
            #command = WGET+realCIREPO_HTTP +"/" +reponame + '/' + LATEST_TXT
            #flag = os.system(command)

        return flag

    def _WDM_Dev_download(self):
        global CIREPO_HTTP
        if self.opts.version != '':
            #CIREPO_HTTP="http://ccatg-build2.cisco.com/cirepo/artifacts/"+self.opts.version
            CIREPO_HTTP="http://cctg-cirepo.cisco.com/cirepo/artifacts/"+self.opts.version
            bv = self.opts.version.split('.')
            base_version=bv[0]+'.'+bv[1]+'.'+bv[2]
            BASE_CIREPO_HTTP= "http://cctg-cirepo.cisco.com/cirepo/artifacts/"+base_version
        filename=self._PrepareXML()
        mydict=self._ParserXML(filename)
        if self.opts.myos == 'mac' or self.opts.myos == 'linux' or self.opts.myos == 'java':
            myos = '.' + self.opts.myos
            print "myos is "+ myos
            for i in mydict:
                if i == 'windowsSDK' or i == 'talist':
                    continue 
                print 'start download '+mydict[i]
                # first to download the feature branch version 
                reponame = mydict[i]
                realCIREPO_HTTP = CIREPO_HTTP
                flag = self._WDM_Dev_download_latestfile(realCIREPO_HTTP,reponame,myos)
                
                if flag != 0:  #try to use base version
                   realCIREPO_HTTP = BASE_CIREPO_HTTP
                   flag = self._WDM_Dev_download_latestfile(realCIREPO_HTTP,reponame,myos)

                   if flag != 0:
                       print "error : Can't find the repo named "+ reponame + "  in platform "+ myos
                       continue 
    
                file_name =  self._WDM_Dev_getHeaderLibsNameFromLatestFile()
                self._WDM_Dev_DelLatestFile_osx()
                if self.opts.platform=="":
                    build_platform=""
                else:
                    build_platform="."+self.opts.platform

                if reponame != 'wme':
                    if self.opts.myos == 'java':
                        self._WDM_wget(realCIREPO_HTTP +"/" + mydict[i]+ myos +"/" +file_name + "/" + file_name  + ".java.zip")
                        #command = WGET + realCIREPO_HTTP +"/" + mydict[i]+ myos +"/" +file_name + "/" + file_name  + ".java.zip"
                    else:
                        if not os.path.exists(file_name  + ".include_libs.zip"):
                            self._WDM_wget(realCIREPO_HTTP +"/" + mydict[i]+ myos +"/" +file_name + "/" + file_name  + build_platform+"." + mydict['.type'] + ".zip")
                            #command = WGET + realCIREPO_HTTP +"/" + mydict[i]+ myos +"/" +file_name + "/" + file_name  + ".include_libs.zip"
                        #else:
                        #    command = ""
                    #print command
                    #os.system(command)
                    command = "unzip -o "+mydict[i] + "*.zip"
                    os.system(command)
                else:
                    self._WDM_Dev_downloadWME_Mac(realCIREPO_HTTP,reponame,myos,file_name)
        else:
            self._WDM_Dev_flushlog()

            myos = '.windows'
            print "myos is "+ myos
            if not os.path.exists("./unzip.exe"):
                self._WDM_wget("https://cctg-cirepo.cisco.com/cirepo/artifacts/buildtools/unzip.exe")
                #command = WGET+"http://cctg-cirepo.cisco.com/cirepo/artifacts/buildtools/unzip.exe"
                #os.system(command)
            for i in mydict:
                if i == 'windowsSDK' or i == 'talist':
                    continue 

                reponame = mydict[i]
                realCIREPO_HTTP = CIREPO_HTTP
                flag = self._WDM_Dev_download_latestfile(realCIREPO_HTTP,reponame,myos)
                
                if flag != 0:  #try to use base version
                   realCIREPO_HTTP = BASE_CIREPO_HTTP
                   flag = self._WDM_Dev_download_latestfile(realCIREPO_HTTP,reponame,myos)

                   if flag != 0:
                       print "error : Can't find the repo named "+ reponame + "  in platform "+ myos
                       continue 

                if reponame == 'wme':
                    file_name_wme = self._WDM_Dev_getHeaderLibsNameFromLatestFile()
                    self._WDM_Dev_downloadWME_Win(realCIREPO_HTTP,reponame,file_name_wme)
                else:
                    self._WDM_Dev_download_one(realCIREPO_HTTP, reponame,myos)

        
    def _WDM_list(self):
        filename=self._PrepareXML()
        if os.path.exists(filename):
            mydict=self._ParserXML(filename)
            for i in mydict:
                if i == 'windowsSDK' or i == 'talist' or re.match("^\.", str(i)):
                    continue
                print mydict[i]
        else:
            print ""

    def _WDM_sdk(self):
        filename=self._PrepareXML()
        mydict=self._ParserXML(filename)
        windowsSDK = mydict['windowsSDK']
        return os.system(windowsSDK)

    def _WDM_repo(self):
        global CIREPO_HTTP
        if self.opts.version != '':
            CIREPO_HTTP="http://cctg-cirepo.cisco.com/cirepo/artifacts/"+self.opts.version
        if not os.path.exists("./unzip.exe"):
            self._WDM_wget("https://cctg-cirepo.cisco.com/cirepo/artifacts/buildtools/unzip.exe")
            #command = WGET+"http://cctg-cirepo.cisco.com/cirepo/artifacts/buildtools/unzip.exe"
            #os.system(command)

        if self.opts.myos == 'mac' or self.opts.myos == 'linux' or self.opts.myos == 'java':
            myos = '.' + self.opts.myos
            repo = self.opts.repo
            flag = self._WDM_wget(CIREPO_HTTP +"/" +repo + myos +'/'+self.opts.tag)
            #command = WGET+CIREPO_HTTP +"/" +repo + myos +'/latest.txt'
            #flag = os.system(command)
            if flag == 0:
                f=open(self.opts.tag,"r")
                file_name =  f.read().strip()
                f.close()
                command ="rm "+self.opts.tag
                os.system(command)
                self._WDM_wget(CIREPO_HTTP +"/" + repo + myos + "/" +file_name + "/" + file_name + ".include_libs.zip")
                #command = WGET + CIREPO_HTTP +"/" + repo + myos + "/" +file_name + "/" + file_name + ".include_libs.zip"
                #print command
                #os.system(command)
                command = "unzip -o -q "+repo + "*.zip"
                os.system(command)
            else:
                print "error : Can't find the repo named "+ repo + "  in platform "+ myos
        else:        
            myos = '.windows'
            repo = self.opts.repo
            flag = self._WDM_wget(CIREPO_HTTP +"/" +repo +'/'+self.opts.tag)
            #command = WGET+CIREPO_HTTP +"/" +repo +'/latest.txt'
            #flag = os.system(command)
            if flag == 0:
                f=open(self.opts.tag,"r")
                file_name =  f.read().strip()
                f.close()
                command ="del "+self.opts.tag
                os.system(command)
                flag2 = self._WDM_wget(CIREPO_HTTP +"/" + repo+ "/" +file_name + "/" + file_name  + ".include_libs.zip")
                #command = WGET + CIREPO_HTTP +"/" + repo+ "/" +file_name + "/" + file_name  + ".include_libs.zip"
                #flag2=os.system(command)
                if flag2 != 0:
                    self._WDM_wget(CIREPO_HTTP +"/" + repo+ "/" +file_name + "/" + file_name + myos + ".include_libs.zip")
                    #command = WGET + CIREPO_HTTP +"/" + repo+ "/" +file_name + "/" + file_name + myos + ".include_libs.zip"
                    #os.system(command)
                command = "unzip -o -q "+repo + "*.zip"
                os.system(command)
            else:
                print "error : Can't find the repo named "+ repo + "  in platform "+ myos

    def _WDM_bin(self):
        global CIREPO_HTTP
        if self.opts.version != '':
            CIREPO_HTTP="http://cctg-cirepo.cisco.com/cirepo/artifacts/"+self.opts.version
        if not os.path.exists("./unzip.exe"):
            self._WDM_wget("http://cctg-cirepo.cisco.com/cirepo/artifacts/buildtools/unzip.exe")
            #command = WGET+"http://cctg-cirepo.cisco.com/cirepo/artifacts/buildtools/unzip.exe"
            #os.system(command)

        if self.opts.myos == 'mac' or self.opts.myos == 'linux' or self.opts.myos == 'java':
            myos = '.' + self.opts.myos
            repo = self.opts.bin
            flag = self._WDM_wget(CIREPO_HTTP +"/" +repo + myos +'/'+self.opts.tag)
            #command = WGET+CIREPO_HTTP +"/" +repo + myos +'/latest.txt'
            #flag = os.system(command)
            if flag == 0:
                f=open(self.opts.tag,"r")
                file_name =  f.read().strip()
                f.close()
                command ="rm "+self.opts.tag
                os.system(command)
                self._WDM_wget(CIREPO_HTTP +"/" + repo + myos + "/" +file_name + "/" + file_name + ".bin.zip")
                #command = WGET + CIREPO_HTTP +"/" + repo + myos + "/" +file_name + "/" + file_name + ".bin.zip"
                #print command
                #os.system(command)
                command = "unzip -o "+repo + "*.zip"
                os.system(command)
            else:
                print "error : Can't find the repo named "+ repo + "  in platform "+ myos
        else:        
            myos = '.windows'
            repo = self.opts.bin
            flag = self._WDM_wget(CIREPO_HTTP +"/" +repo +'/'+self.opts.tag)
            #command = WGET+CIREPO_HTTP +"/" +repo +'/latest.txt'
            #flag = os.system(command)
            if flag == 0:
                f=open(self.opts.tag,"r")
                file_name =  f.read().strip()
                f.close()
                command ="rm "+self.opts.tag
                os.system(command)
                flag2 = self._WDM_wget(CIREPO_HTTP +"/" + repo+ "/" +file_name + "/" + file_name  + ".bin.zip")
                #command = WGET+ CIREPO_HTTP +"/" + repo+ "/" +file_name + "/" + file_name  + ".bin.zip"
                #flag2=os.system(command)
                if flag2 != 0:
                    self._WDM_wget(CIREPO_HTTP +"/" + repo+ "/" +file_name + "/" + file_name + myos + ".bin.zip")
                    #command = WGET + CIREPO_HTTP +"/" + repo+ "/" +file_name + "/" + file_name + myos + ".bin.zip"
                    #os.system(command)
                command = "unzip -o "+repo + "*.zip"
                os.system(command)
            else:
                print "error : Can't find the repo named "+ repo + "  in platform "+ myos
    

    def _WDM_getdll(self):
        CLIENT_PACKAGE="http://cctg-cirepo.cisco.com/cirepo/Train_Client/"+ CIREPO_CENTRAL_VERSION + "/"
        self._WDM_wget(CLIENT_PACKAGE +"latestsuccess.txt")
        #command = WGET+CLIENT_PACKAGE +"latestsuccess.txt"
        #os.system(command)
        f=open("latestsuccess.txt","r")
        file_name =  f.read().strip()
        f.close()
        command ="del latestsuccess.txt"
        os.system(command)
        self._WDM_wget(CLIENT_PACKAGE + file_name + '/' + self.opts.getdll, "../../output/bin_test/release")
        #command =WGET+"-P ../../output/bin_test/release "+ CLIENT_PACKAGE + file_name + '/' + self.opts.getdll 
        #print command
        #os.system(command)

    def _WDM_mapcollect(self):
        url="http://10.194.242.175/ci/Default.aspx?Source="+self.opts.mapcollect
        request=urllib2.Request(url)  
        html_str=urllib2.urlopen(request).read()  
        print html_str

    def _WDM_talist(self):
        filename=self._PrepareXML()
        if os.path.exists(filename):
            mydict=self._ParserXML(filename)
            print mydict['talist']

    def _WDM_revisions(self):
        print "hello revisions"


    # added by Quick to replace command wget
    def _WDM_wget(self, url, path=""):
        try:
            print "get ", url
            f = opener.open(url)
            dest = os.path.basename(url)
            if path != "":
                dest = path + "/" + dest
#            with open(dest, "wb") as local_file:
#                local_file.write(f.read())
            local_file = open(dest, "wb")
            local_file.write(f.read())
            local_file.close() 
        except urllib2.HTTPError, e:
            #print "HTTP Error:" , e.code, url
            return 1			
        except urllib2.URLError, e:
            #print "URL Error:" , e.code, url
            return 1
        return 0			
		
    def run(self):
        if self.opts.download != '' or self.opts.list != '' or self.opts.talist != '':
            username=""
            password=""
            pass
        elif self.opts.userpass != '':
            up = self.opts.userpass.split('/')
            username=up[0]
            password=up[1]
			
            global WGET
            WGET="wget -o- --user="+username+" --password='"+password+"' "
        else:
            username=raw_input("please input your CEC username:")
            password=getpass.getpass("Please input your CEC password:")
            WGET="wget -o- --user="+username+" --password='"+password+"' "

        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, "https://cctg-cirepo.cisco.com", username, password)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        global opener
        opener = urllib2.build_opener(handler)
        filename=self._PrepareXML()
        if self.opts.download != '':
            self._WDM_download()
        elif self.opts.sdk != '':
            self._WDM_sdk()
        elif self.opts.repo != '':
            self._WDM_repo()
        elif self.opts.bin != '':
            self._WDM_bin()
        elif self.opts.getdll != '':
            self._WDM_getdll()
        elif self.opts.mapcollect != '':
            self._WDM_mapcollect()
        elif self.opts.talist != '':
            self._WDM_talist()
        elif self.opts.list != '':
            self._WDM_list()
        else :
            self._WDM_Dev_download()



    
def ParserOpts(argv):
        '''
        '''
        parser = OptionParser()
        parser.usage = ''
        parser.description = ''
        parser.add_option('-d', '--download',
                          help='Download the dependency files from CIrepo',
                          dest='download', default='')
        parser.add_option('-l', '--list', 
                          help='List the dependency',
                          dest='list', default='')
        parser.add_option('-s', '--sdk', 
                          help='get windowsSDK version',
                          dest='sdk', default='')
        parser.add_option('-o', '--os', 
                          help='send os as parameter',
                          dest='myos', default='')
        parser.add_option('-r', '--repo', 
                          help='download the repo in opts',
                          dest='repo', default='')
        parser.add_option('-v', '--version', 
                          help='receive project version',
                          dest='version', default='')
        parser.add_option('-b', '--bin', 
                          help='download repo bin',
                          dest='bin', default='')
        parser.add_option('-g', '--getdll', 
                          help='download dll',
                          dest='getdll', default='')
        parser.add_option('-m', '--map', 
                          help='download dll',
                          dest='mapcollect', default='')
        parser.add_option('-t', '--talist',
                          help='ta list',
                          dest='talist', default='')
        parser.add_option('-u', '--user/pass', 
                          help='user/pass',
                          dest='userpass', default='')
        parser.add_option('-p', '--platform',
                          help='platform',
                          dest='platform', default='')
        parser.add_option('-a', '--tag', 
                          help='tag',
                          dest='tag', default='latest.txt')
        parser.add_option('-e', '--revisions', 
                          help='revisions',
                          dest='revisions', default='')
        return parser.parse_args(args=argv)


if __name__ == '__main__':   
    start_time = time.time() 
    opts, args = ParserOpts(sys.argv)
    WMG = WebexDependenMgr(opts, args)
    WMG.run()






