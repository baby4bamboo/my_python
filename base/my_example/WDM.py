

from optparse import OptionParser
import xml.dom.minidom
import sys,os,time,platform,urllib2,re,string
import getpass,commands,json

cctg_repo = os.environ.get('CCTG_REPO')
if cctg_repo == "/cctg/cirepo-rcdn":
    WEBEX_ARTIFACTS="/cctg/cirepo-rcdn/webex_artifacts/"
    HTTP_WEBEX_ARTIFACTS = "https://cctg-rcdn-cirepo.cisco.com/cirepo/artifacts/"
else:
    WEBEX_ARTIFACTS="/cctg/cirepo/webex_artifacts/"
    HTTP_WEBEX_ARTIFACTS="https://cctg-cirepo.cisco.com/cirepo/webex_artifacts/"

FILENAME="dep.xml"
FILENAME2="dependencies.xml"
WGET="wget -o- "
opener=None
XMLFILE="revisions.xml"
TXTFILE="revisions.txt"
download_success=True
DEPINFO="depinfo.txt"

repoconfig_json="repoconfig.json"
dependencies_json="WDM.json"
json_dir="webex-wdm/bin/"

class WebexDependenMgr(object):
    '''
    The main entrance of script.
    '''
    def __init__(self, opts, args):
        self.opts = opts
        self.args = args
    
    def _PrepareXML(self):
        filename='./' + FILENAME
        if not os.path.exists(filename):
            file_path = '../build/' + self.opts.myos
            filename= file_path  + '/'+self.opts.platform + '/' + FILENAME
            if not os.path.exists(filename):
                filename= file_path + '/' + FILENAME
                if os.path.exists(filename):
                    command = "cp -Rf " + filename + ' ./'
                    os.system(command)
                elif self.opts.list == '':
                    print 'error : ' + FILENAME  + ' not found, so do nothing...'
                    sys.exit(0)
                else:
                    sys.exit(0)
                
        return filename

    def _SubstitutionDict(self,mydict,filename=json_dir+dependencies_json):
        need_download_json=0
        for i in mydict:
            if i != "myrepo":
                for j in mydict[i]:
                    if mydict[i][j] !=[] and mydict[i][j].find("${") != -1:
                        print mydict[i][j]
                        need_download_json=1
        if need_download_json != 0:
            json_dict={0:{'group': u'client', 'platform': [], 'maps': [], 'destination': [], 'source': [], 'version': [], 'reponame': u'webex-wdm', 'os': []}}
            flag = self._WDM_download(json_dict)
            load_f=open(filename, 'r')
            variable_dict=json.load(load_f)
            load_f.close()
            for i in mydict:
                if i != "myrepo":
                    for j in mydict[i]:
                        if mydict[i][j] !=[] and mydict[i][j].find("${") != -1:
                            variable=mydict[i][j]
                            variable = variable.strip('\r\n')
                            mydict[i][j]=variable_dict[variable]
        return mydict

    def _SubstitutionRepoconfigDict(self,mydict,filename=repoconfig_json):
        need_repoconfig_json=0
        for i in mydict:
            if i == "myrepo":
                for j in mydict[i]:
                    if mydict[i][j] !=[] and mydict[i][j].find("${") != -1:
                        need_repoconfig_json=1
        if need_repoconfig_json == 1:
            repoconfig_json_file="../build/"+repoconfig_json
            if not os.path.exists(repoconfig_json_file):
                print 'error : need ' + repoconfig_json  + ' , but not found...'
                sys.exit(0)
            load_f=open(repoconfig_json_file, 'r')
            variable_dict=json.load(load_f)
            load_f.close()
            for i in mydict:
                if i == "myrepo":
                    for j in mydict[i]:
                        if mydict[i][j] !=[] and mydict[i][j].find("${") != -1:
                            variable=mydict[i][j]
                            variable = variable.strip('\r\n')
                            mydict[i][j]=variable_dict[variable]
        return mydict

            
    def _ParserXML(self,filename):
        WDMdict={}
        WDMdictTemp={}
        DOMTree = xml.dom.minidom.parse(filename)
        config = DOMTree.documentElement

        repoconfig = config.getElementsByTagName("repoconfig")[0]
        if repoconfig.hasAttribute("reponame"):
            WDMdictTemp['reponame'] = repoconfig.getAttribute("reponame")
            if repoconfig.hasAttribute("windowsSDK"):
                WDMdictTemp['windowsSDK']=repoconfig.getAttribute("windowsSDK")
            else:
                WDMdictTemp['windowsSDK']="v7.1A"
            if repoconfig.getElementsByTagName("version") != []:
                WDMdictTemp['version']=repoconfig.getElementsByTagName("version")[0].childNodes[0].data
            else:
                WDMdictTemp['version']=[]
            if repoconfig.getElementsByTagName("group") != []:
                WDMdictTemp['group']=repoconfig.getElementsByTagName("group")[0].childNodes[0].data
            else:
                WDMdictTemp['group']=[]
            if repoconfig.getElementsByTagName("os") != []:
                WDMdictTemp['os']=repoconfig.getElementsByTagName("os")[0].childNodes[0].data
            else:
                WDMdictTemp['os']=[]
        else:
            WDMdictTemp['reponame'] = []
        WDMdict['myrepo']=WDMdictTemp

        dependencies = config.getElementsByTagName("dependencies")[0]
        ds = dependencies.getElementsByTagName("dependency")
        i=0
        for dependency in ds:
            WDMdictTemp={}
            if dependency.hasAttribute("reponame"):
                WDMdictTemp['reponame']=dependency.getAttribute("reponame")
                if dependency.getElementsByTagName("version") != []:
                    WDMdictTemp['version']=dependency.getElementsByTagName("version")[0].childNodes[0].data
                else:
                    WDMdictTemp['version']=[]
                if dependency.getElementsByTagName("group") != []:
                    WDMdictTemp['group']=dependency.getElementsByTagName("group")[0].childNodes[0].data
                else:
                    print "<group> info is missing in XML file <dependency> part"
                    sys.exit(1)
                if dependency.getElementsByTagName("os") != []:
                    WDMdictTemp['os']=dependency.getElementsByTagName("os")[0].childNodes[0].data
                else:
                    WDMdictTemp['os']=[]
                if dependency.getElementsByTagName("platform") != []:
                    WDMdictTemp['platform']=dependency.getElementsByTagName("platform")[0].childNodes[0].data
                else:
                    WDMdictTemp['platform']=[]
                if dependency.getElementsByTagName("source") != []:
                    WDMdictTemp['source']=dependency.getElementsByTagName("source")[0].childNodes[0].data
                else:
                    WDMdictTemp['source']=[]
                if dependency.getElementsByTagName("destination") != []:
                    WDMdictTemp['destination']=dependency.getElementsByTagName("destination")[0].childNodes[0].data
                else:
                    WDMdictTemp['destination']=[]
                if dependency.getElementsByTagName("maps") != []:
                    WDMdictTemp['maps']=dependency.getElementsByTagName("maps")[0].childNodes[0].data
                else:
                    WDMdictTemp['maps']=[]
                WDMdict[i]=WDMdictTemp
            i=i+1
        return WDMdict

    def revisions(self,download_path,download_reponame,build_number,latest):
        component = download_reponame
        buildtype = self.opts.buildtype
        buildnumber = build_number
        tmp = latest.split('-')[-1]
        version_in_latest = '.'.join(tmp.split('.')[0:-1])
        dependency_component = '-'.join(latest.split('-')[0:-1])
        filename = download_path+"/build_history."+dependency_component+"."+version_in_latest+".txt"
        #command = 'egrep -A 4 "^Buildnumber: '+buildnumber+'" '+filename+' | grep "@" | tail -1'
        command = 'egrep -A 100 "^Buildnumber: '+buildnumber+'" '+filename+' | egrep -B 100 -m 1 "^=========="| grep "@" | uniq'
        revisions=commands.getstatusoutput(command)[1]
        if revisions=="":
            command = 'egrep -A 100 "^Buildnumber: '+buildnumber+'" '+filename+'| grep "@" | uniq'
            revisions=commands.getstatusoutput(command)[1]
        if revisions.find("@") == -1:
            revisions=""

        f=open(XMLFILE,'aw+')
        xml_str="<component>"+"\n"+"\t<name>"+component+"</name>"+"\n"+"\t<version>"+version_in_latest+"</version>"+"\n"+"\t<buildtype>"+buildtype+"</buildtype>"+"\n"+"\t<buildnumber>"+buildnumber+"</buildnumber>"+"\n"+"\t<revision>"+revisions+"</revision>"+"\n"+"</component>"+"\n"
        f.write(xml_str)
        f.close()
        f=open(TXTFILE,'aw+')
        f.write(revisions)
        f.close()

    def prepare_userpass(self):
        if os.path.exists(WEBEX_ARTIFACTS) or self.opts.list != '':
            username=""
            password=""
            pass
        elif self.opts.userpass != '':
            up = self.opts.userpass.split('/')
            username=up[0]
            password=up[1]
        else:
            username=raw_input("please input your CEC username:")
            password=getpass.getpass("Please input your CEC password:")
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, "https://cctg-cirepo.cisco.com", username, password)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        global opener
        opener = urllib2.build_opener(handler)
        #print password_mgr
        #print handler


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

    def test(self,mydict):
        pass


    def  _WDM_key(self,mydict):
        if mydict['myrepo']['reponame']==[] or mydict['myrepo']['group']==[] :
            print 'reponame or group is null'
            sys.exit(1)
        publish_group=mydict['myrepo']['group']
        publish_reponame=mydict['myrepo']['reponame']
        if mydict['myrepo']['version'] == []:
            publish_version= self.opts.version
        else:
            publish_version= mydict['myrepo']['version']
        if mydict['myrepo']['os'] == []:
            publish_os='.'+self.opts.myos
        else:
            publish_os='.'+mydict['myrepo']['os']
        if (publish_group=="meetingservice" or publish_group=="client") and (publish_os==".mac" or publish_os==".linux" or publish_os==".java" or publish_os==".iOS" or publish_os==".Android" or publish_os==".ubuntu"):
            my_version=int(self.opts.version[:2])
            if self.opts.platform != "" and my_version < 39:
                repolatest='webex_artifacts/'+publish_group+'/'+publish_reponame+ publish_os +'.' +self.opts.platform +'/'+publish_version
            else:
                repolatest='webex_artifacts/'+publish_group+'/'+publish_reponame+ publish_os +'/'+publish_version
        else:
            repolatest='webex_artifacts/'+publish_group+'/'+publish_reponame+'/'+publish_version

        return_key=self.opts.key
        if return_key=='repolatest':
            print repolatest
        if return_key=='reponame':
            print publish_reponame
        if return_key=='group':
            print publish_group
        if return_key=='version':
            print publish_version 

            
    def _WDM_download(self,mydict):
        global download_success
        for i in mydict:
            try:
                if str(i).isdigit() and download_success==True:
                    download_group=mydict[i]['group']
                    download_reponame=mydict[i]['reponame']
                    bv = self.opts.version.split('.')
                    if mydict[i]['version'] == []:
                        base_version=bv[0]+'.'+bv[1]+'.'+bv[2]   
                    else:
                        base_version=mydict[i]['version']
                    if mydict[i]['os'] == []:
                        download_os='.'+self.opts.myos
                    else:
                        download_os='.'+mydict[i]['os']
                    if (bv[-1] == 'coverage' and download_os==".windows" and mydict[0]['reponame']!="webex-wdm" and mydict['myrepo']['reponame']!="webex-client-packaging"):
                        download_version=base_version
                    elif bool(re.search(r'[a-zA-Z]', bv[-1])):
                        download_version=base_version+'.'+bv[-1]
                    else:
                        download_version=base_version
                    if mydict[i]['platform'] == [] :
                        if self.opts.platform == '':
                            download_platform=''
                        else:
                            download_platform=self.opts.platform+':'+'.'
                    else:
                        download_platform = mydict[i]['platform']
                    download_platform_list = download_platform.split(',')
                    for current_platfrom in download_platform_list:
                        platforms = current_platfrom.split(':')
                        folder = ''
                        if len(platforms) >2 or len(platforms) < 1:
                            raise Exception('Invalid parameter: platform.')
                        elif len(platforms) == 2:
                            platform = platforms[0]
                            folder = platforms[1]
                        else:
                            platform = platforms[0]
                            folder = platforms[0]
                        if platform == '':
                            filename_ext = download_os+'.zip' 
                        else:
                            filename_ext = download_os+'.'+platform+'.zip'
                        tag_list=self.get_tag_list()
                        is_download_success=False
                        for TAG in tag_list:
                            if is_download_success == True:
                                break
                            self.prepare_userpass()
                            if TAG==tag_list[-1]:
                                is_last_tag=True
                            else:
                                is_last_tag=False
                            if os.path.exists(WEBEX_ARTIFACTS):
                                download_path1=download_path=WEBEX_ARTIFACTS+download_group+'/'+download_reponame+download_os+'.'+platform+'/'+download_version
                                if not os.path.exists(download_path):
                                    download_path2=download_path=WEBEX_ARTIFACTS+download_group+'/'+download_reponame+download_os+'.'+platform+'/'+base_version
                                    if not os.path.exists(download_path):
                                        download_path3=download_path=WEBEX_ARTIFACTS+download_group+'/'+download_reponame+download_os+'/'+download_version
                                        if not os.path.exists(download_path):
                                            download_path4=download_path=WEBEX_ARTIFACTS+download_group+'/'+download_reponame+download_os+'/'+base_version
                                            if not os.path.exists(download_path):
                                                download_path5=download_path=WEBEX_ARTIFACTS+download_group+'/'+download_reponame+'/'+download_version
                                                if not os.path.exists(download_path):
                                                    download_path6=download_path=WEBEX_ARTIFACTS+download_group+'/'+download_reponame+'/'+base_version
                                                    if not os.path.exists(download_path):
                                                        print "Error latest : can't find "+download_reponame+" in the following path. Please check it!"
                                                        print download_path1
                                                        print download_path2
                                                        print download_path3
                                                        print download_path4
                                                        print download_path5
                                                        print download_path6
                                                        download_success=False
                                                        break
                                if os.path.exists(download_path +'/' + TAG):
                                    f=open(download_path +'/' + TAG,'r')
                                    file_name=f.read().strip()
                                    f.close()
                                    unzip_filename=download_filename = file_name + filename_ext 
                                    command = 'cp -Rf ' + download_path+'/'+ file_name + '/' + download_filename + ' ./ 1>/dev/null 2>&1'
                                    flag = os.system(command)
                                    if flag != 0:
                                        command = 'cp -Rf ' + download_path+'/'+ file_name + '/' + file_name + download_os+'.zip' + ' ./ 1>/dev/null 2>&1'
                                        unzip_filename=file_name + download_os+'.zip'
                                        flag = os.system(command)
                                        if flag != 0:
                                            command = 'cp -Rf ' + download_path+'/'+ file_name + '/' + file_name + '.zip ./ 1>/dev/null 2>&1'
                                            unzip_filename=file_name +'.zip'
                                            flag = os.system(command)
                                            if flag != 0:    
                                                print "Download failed: can't find in "+download_path+'/'+ file_name + '/' + download_filename
                                                print "Download failed: can't find in "+download_path+'/'+ file_name + '/' + file_name+download_os+'.zip'
                                                print "Download failed: can't find in "+download_path+'/'+ file_name + '/' + file_name
                                                download_success=False
                                                break
                                    build_number = file_name.split('.')[-1]
                                    print('%-30s%-15s%-10s%-60s' % (download_reponame,build_number,platform,download_path))
                                    is_download_success=True
                                else:
                                    if(is_last_tag):
                                        print "Download error ! Can't find TAG of "
                                        print download_path +'/' + TAG
                                        download_success=False
                                        break
                                    else:
                                        continue
                            else:
                                http_download_path1=http_download_path=HTTP_WEBEX_ARTIFACTS+download_group+'/'+download_reponame+download_os+'.'+platform+'/'+download_version
                                ret = self._WDM_wget(http_download_path+'/'+TAG)
                                if ret != 0:
                                    http_download_path2=http_download_path=HTTP_WEBEX_ARTIFACTS+download_group+'/'+download_reponame+download_os+'.'+platform+'/'+base_version
                                    ret = self._WDM_wget(http_download_path+'/'+TAG)
                                    if ret != 0:
                                        http_download_path3=http_download_path=HTTP_WEBEX_ARTIFACTS+download_group+'/'+download_reponame+download_os+'/'+download_version
                                        ret = self._WDM_wget(http_download_path+'/'+TAG)
                                        if ret != 0:
                                            http_download_path4=http_download_path=HTTP_WEBEX_ARTIFACTS+download_group+'/'+download_reponame+download_os+'/'+base_version 
                                            ret = self._WDM_wget(http_download_path+'/'+TAG)
                                            if ret != 0:
                                                http_download_path5=http_download_path=HTTP_WEBEX_ARTIFACTS+download_group+'/'+download_reponame+'/'+download_version
                                                ret = self._WDM_wget(http_download_path+'/'+TAG)
                                                if ret != 0:
                                                    http_download_path6=http_download_path=HTTP_WEBEX_ARTIFACTS+download_group+'/'+download_reponame+'/'+base_version
                                                    ret = self._WDM_wget(http_download_path+'/'+TAG)
                                                    if ret != 0 and is_last_tag:
                                                        print "Error TAG: can't find "+download_reponame+'/'+TAG+" in the following path. Please check it!"
                                                        print http_download_path1
                                                        print http_download_path2
                                                        print http_download_path3
                                                        print http_download_path4
                                                        print http_download_path5
                                                        print http_download_path6
                                                        download_success=False
                                                        break
                                                    elif ret != 0:
                                                        continue
                                f=open(TAG,'r')
                                file_name=f.read().strip()
                                f.close()
                                unzip_filename=download_filename = file_name + filename_ext 
                                if self.opts.myos == 'mac' or self.opts.myos == 'linux' or self.opts.myos == 'java' or self.opts.myos == 'iOS' or self.opts.myos == 'Android' or self.opts.myos == 'ubuntu':
                                    command = "rm "+TAG
                                    os.system(command)
                                else:
                                    command = "del "+TAG
                                    os.system(command)
                                if not os.path.exists(download_filename) and not os.path.exists(file_name+'.'+self.opts.myos+'.zip') and not os.path.exists(file_name+'.zip'):
                                    flag = self._WDM_wget(http_download_path + '/' + file_name + '/'+ download_filename)
                                    if flag != 0:
                                        flag = self._WDM_wget(http_download_path + '/' + file_name + '/'+ file_name +'.'+self.opts.myos+ '.zip' )
                                        unzip_filename=file_name +'.'+self.opts.myos+ '.zip'
                                        if flag != 0:
                                            flag = self._WDM_wget(http_download_path + '/' + file_name + '/'+ file_name + '.zip')
                                            unzip_filename=file_name + '.zip'
                                else:
                                    flag = 0
                                build_number = file_name.split('.')[-1]
                                print('%-30s%-15s%-10s%-60s' % (download_reponame,build_number,platform,http_download_path))
                                is_download_success=True
                                if flag != 0:
                                    print "Download failed: can't find in "+http_download_path + '/' + file_name + '/'+ download_filename
                                    print "Download failed: can't find in "+http_download_path + '/' + file_name + '/'+ file_name +'.'+self.opts.myos+ '.zip'
                                    print "Download failed: can't find in "+http_download_path + '/' + file_name + '/'+ file_name + '.zip'
                                    download_success=False
                                    break
                            #Begin to unzip the zip file
                            if self.opts.myos == 'windows' and not os.path.exists(WEBEX_ARTIFACTS):
                                if folder == '' or folder =='.':
                                    folder = download_reponame
                                else:
                                    folder = download_reponame +"\\" +  folder
                                command = "mkdir " + folder 
                                os.system(command)
                                command =  "unzip -o -d "+ folder +" -q "+ unzip_filename 
                                flag =os.system(command)
                            else:
                                if folder == '' or folder =='.':
                                    folder = download_reponame
                                else:
                                    folder = download_reponame +"/" +  folder
                                command = "mkdir -p " + folder + " ; unzip -o -d "+ folder +" -q "+ unzip_filename
                                flag =os.system(command)
                            if flag != 0:
                                print "unzip failed: can't find "+unzip_filename
                                download_success=False
                                break
                            try:
                                if  mydict[i]['source'] != [] and mydict[i]['destination'] != []:
                                    if not os.path.exists(mydict[i]['destination']):
                                        command = "mkdir -p "+mydict[i]['destination']
                                        os.system(command)
                                    command = "cp -Rf "+folder+"/"+mydict[i]['source']+" "+mydict[i]['destination']+"/"
                                    os.system(command)
                            except:
                                pass
                            if self.opts.buildtype != '' and os.path.exists(WEBEX_ARTIFACTS):
                                self.revisions(download_path,download_reponame,build_number,file_name)
                                dep_path=download_path+'/'+ file_name
                                self.depinfo(dep_path)
                            try:
                                if  mydict[i]['maps'] != [] and os.path.exists(WEBEX_ARTIFACTS):
                                    if platform == '':
                                        filename_ext_maps = download_os+'.maps.zip' 
                                    else:
                                        filename_ext_maps = download_os+'.'+platform+'.maps.zip'
                                    download_filename_maps = file_name + filename_ext_maps 
                                    command = 'cp -Rf ' + download_path+'/'+ file_name + '/' + download_filename_maps + ' ./ 1>/dev/null 2>&1'
                                    flag = os.system(command)
                                    if flag != 0:
                                        command = 'cp -Rf ' + download_path+'/'+ file_name + '/' + file_name + '.maps.zip ./ 1>/dev/null 2>&1'
                                        flag = os.system(command)
                                        if flag != 0:
                                            command = 'cp -Rf ' + download_path+'/'+ file_name + '/' + file_name + download_os + '.maps.zip ./ 1>/dev/null 2>&1'
                                            flag = os.system(command)
                                            if flag != 0:
                                                print "can't download maps of "+file_name
                            except:
                                pass
                            try:
                                if  mydict[i]['maps'] != [] and not os.path.exists(WEBEX_ARTIFACTS):
                                    if platform == '':
                                        filename_ext_maps = download_os+'.maps.zip' 
                                    else:
                                        filename_ext_maps = download_os+'.'+platform+'.maps.zip'
                                    download_filename_maps = file_name + filename_ext_maps 
                                    flag = self._WDM_wget(http_download_path + '/' + file_name + '/'+ download_filename_maps)
                                    if flag != 0:
                                        flag = self._WDM_wget(http_download_path + '/' + file_name + '/'+ file_name + '.maps.zip')
                                        if flag != 0:
                                            flag = self._WDM_wget(http_download_path + '/' + file_name + '/'+ file_name + download_os +'.maps.zip')
                            except:
                                pass
                else:
                    pass
            except:
                pass

    def _WDM_list(self,filename,mydict):
        try:
            if os.path.exists(filename):
                for i in mydict:
                    if i == 'windowsSDK' or i == 'talist' or i == 'myrepo' or re.match("^\.", str(i)):
                        continue
                    else:
                        print mydict[i]['reponame']
            else:
                print ""
        except:
            pass

    def _WDM_wget(self, url, path=""):
        try:
            f = opener.open(url)
            dest = os.path.basename(url)
            if path != "":
                dest = path + "/" + dest
            local_file = open(dest, "wb")
            local_file.write(f.read())
            local_file.close() 
        except urllib2.HTTPError, e:
            #print "HTTP Error:" , e.code, url
            return 1            
        except urllib2.URLError, e:
            #print "URL Error:" , e.code, url
            return 1
        except:
            return 1
        return 0
      

      
    def run(self):
        filename=self._PrepareXML()
        mydict=self._ParserXML(filename)
        if self.opts.download != '':
            mydict=self._SubstitutionDict(mydict)
            self._WDM_download(mydict)
        if self.opts.key != '':
            mydict=self._SubstitutionRepoconfigDict(mydict)
            self._WDM_key(mydict)
        if self.opts.list != '':
            self._WDM_list(filename,mydict)
        if self.opts.download == '' and self.opts.key == '' and self.opts.list == '':
            self.test(mydict)


def ParserOpts(argv):
        parser = OptionParser()
        parser.usage = ''
        parser.description = ''
        parser.add_option('-d', '--download',
                          help='Download the dependency files from CIrepo',
                          dest='download', default='')
        parser.add_option('-k', '--key', 
                          help='retrun key value',
                          dest='key', default='')
        parser.add_option('-o', '--os', 
                          help='send os as parameter',
                          dest='myos', default='')
        parser.add_option('-p', '--platform', 
                          help='platform',
                          dest='platform', default='')
        parser.add_option('-v', '--version', 
                          help='version',
                          dest='version', default='')
        parser.add_option('-u', '--user/pass', 
                          help='user/pass',
                          dest='userpass', default='')
        parser.add_option('-l', '--list', 
                          help='List the dependency',
                          dest='list', default='')
        parser.add_option('-e', '--buildtype', 
                          help='give a build type ,return a json',
                          dest='buildtype', default='')
        parser.add_option('-a', '--tag', 
                          help='tag',
                          dest='tag', default='latest.txt')
        return parser.parse_args(args=argv)


if __name__ == '__main__':   
    start_time = time.time() 
    opts, args = ParserOpts(sys.argv)
    WDM = WebexDependenMgr(opts, args)
    WDM.run()
    if download_success==False:
        sys.exit(1)






