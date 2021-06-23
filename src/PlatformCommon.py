# FlatBuildTool 2017/07/21 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

import  os
import  BuildUtility
import  copy
import  platform
import  Depend
from BuildUtility import Log

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

class TargetEnvironmentCommon:

    def __init__( self, tool, parent= None ):
        self.tool= tool

        self.CONFIG= 'Debug'

        self.TARGET_PLATFORM= 'Unknown'
        self.TARGET_ARCH= 'Unknown'
        self.HOST_PLATFORM= 'Unknown'
        self.HOST_ARCH= 'Unknown'

        self.setupHostPlatform()
        self.setTargetArch( self.getHostArch() )
        self.setTargetPlatform( self.getHostPlatform() )

        self.OUTPUT_OBJ_DIR= 'obj'
        self.OUTPUT_EXE_DIR= 'obj'
        self.OUTPUT_LIB_DIR= 'lib'
        self.OUTPUT_DLL_DIR= 'lib'

        self.INCLUDE_PATH= []
        self.LIB_PATH= []
        self.BIN_PATH= []

        self.CC_FLAGS= []
        self.LINK_FLAGS= []
        self.LIB_FLAGS= []
        self.LINK_LIBS= []

        self.INCLUDE_PATH_R= []
        self.LIB_PATH_R= []
        self.BIN_PATH_R= []
        self.LINK_LIBS_R= []

        self.CC_FLAGS_R= []
        self.LINK_FLAGS_R= []
        self.LIB_FLAGS_R= []
        self.USER_OPTION= {}

        self.EXE_NAME_FUNC= None

        if parent != None:
            inherit_attribute= [
                    'OUTPUT_OBJ_DIR',
                    'OUTPUT_EXE_DIR',
                    'OUTPUT_LIB_DIR',
                    'OUTPUT_DLL_DIR',

                    'INCLUDE_PATH',
                    'LIB_PATH',
                    'BIN_PATH',

                    'CC_FLAGS',
                    'LINK_FLAGS',
                    'LIB_FLAGS',
                    'LINK_LIBS',
                ]
            for attr in inherit_attribute:
                data= getattr( parent, attr, None )
                if data != None:
                    setattr( self, attr, copy.deepcopy(data) )
            self.USER_OPTION= parent.USER_OPTION

    def summary( self ):
        Log.p( 'HostArch = ' + self.getHostArch() )
        Log.p( 'HostPlatform = ' + self.getHostPlatform() )

    def isValid( self ):
        return  True

    #--------------------------------------------------------------------------

    def getUserOption( self, name, def_value= None ):
        if name in self.USER_OPTION:
            return  self.USER_OPTION[ name ]
        return  def_value

    def getEnv( self, name, def_value= None ):
        if name in self.USER_OPTION:
            return  self.USER_OPTION[ name ]
        if name in os.environ:
            return  os.environ[name]
        return  def_value

    def setEnv( self, name, value ):
        self.USER_OPTION[ name ]= value

    #--------------------------------------------------------------------------

    def clone( self ):
        tool= self.tool
        self.tool= None
        env2= copy.deepcopy( self )
        self.tool= tool
        env2.tool= tool
        return  env2

    #--------------------------------------------------------------------------

    def setupHostPlatform( self ):
        Log.d( 'system= ' + platform.system() )
        Log.d( 'machine= ' + platform.machine() )
        Log.d( 'processor= ' + platform.processor() )
        machine= platform.machine()
        table_arch= {
                'x64'     : 'x64',
                'AMD64'   : 'x64',
                'x86_64'  : 'x64',
                'x86'     : 'x86',
                'i686'    : 'x86',
                'i386'    : 'x86',
                'armv8l'  : 'arm64',
                'armv7l'  : 'arm7',
                'armv6l'  : 'arm6',
                'aarch64' : 'arm64',
                'arm64'   : 'arm64',
                'e2k'     : 'e2k',
            }
        if machine in table_arch:
            self.HOST_ARCH= table_arch[machine]
        table_platform= {
                'Windows' : 'Windows',
                'Linux'   : 'Linux',
                'Unix'    : 'Linux',
                'Darwin'  : 'macOS',
            }
        system= platform.system()
        if system in table_platform:
            self.HOST_PLATFORM= table_platform[system]

    #--------------------------------------------------------------------------

    def getSupportArchList( self ):
        return  [ self.getHostArch() ]

    #--------------------------------------------------------------------------

    def getTargetArch( self ):
        return  self.TARGET_ARCH

    def getHostArch( self ):
        return  self.HOST_ARCH

    def getTargetPlatform( self ):
        return  self.TARGET_PLATFORM

    def getHostPlatform( self ):
        return  self.HOST_PLATFORM

    def setTargetArch( self, target ):
        self.TARGET_ARCH= target

    def setTargetPlatform( self, target ):
        self.TARGET_PLATFORM= target

    def setHostArch( self, arch ):
        self.HOST_ARCH= arch

    def getConfig( self ):
        return  self.CONFIG

    def setConfig( self, config ):
        self.CONFIG= config


    def isDebug( self ):
        return  self.CONFIG == 'Debug'

    def isRelease( self ):
        return  self.CONFIG == 'Release'

    def isRetail( self ):
        return  self.CONFIG == 'Retail'


    def setApiLevel( self, api ):
        pass

    def setApiName( self, api ):
        pass

    #--------------------------------------------------------------------------

    def setObjDir( self, path ):
        self.OUTPUT_OBJ_DIR= path

    def setExeDir( self, path ):
        self.OUTPUT_EXE_DIR= path

    def setLibDir( self, path ):
        self.OUTPUT_LIB_DIR= path

    def setDllDir( self, path ):
        self.OUTPUT_DLL_DIR= path

    #--------------------------------------------------------------------------

    def addIncludePaths( self, paths ):
        for path in paths:
            self.INCLUDE_PATH.append( self.tool.getGenericPath( path ) )
        #self.INCLUDE_PATH.extend( paths )

    def addLibPaths( self, paths ):
        for path in paths:
            self.LIB_PATH.append( self.tool.getGenericPath( path ) )
        #self.LIB_PATH.extend( paths )

    def addCCFlags( self, flags ):
        self.CC_FLAGS.extend( flags )

    def addLinkFlags( self, flags ):
        self.LINK_FLAGS.extend( flags )

    def addLibFlags( self, flags ):
        self.LIB_FLAGS.extend( flags )

    def addLibraries( self, libs ):
        self.LINK_LIBS.extend( libs )

    #--------------------------------------------------------------------------

    def searchIncludePath( self, base_file, file_name ):
        if os.path.exists( file_name ):
            if os.path.isfile( file_name ):
                return  os.path.abspath( file_name )
        dir,name= os.path.split( base_file )
        cur_path= os.path.join( dir, file_name )
        if os.path.exists( cur_path ):
            if os.path.isfile( cur_path ):
                return  os.path.abspath( cur_path )
        for path in self.INCLUDE_PATH:
            cur_path= os.path.join( path, file_name )
            #print( cur_path )
            if os.path.exists( cur_path ):
                if os.path.isfile( cur_path ):
                    return  os.path.abspath( cur_path )
        #print( 'include not found %s from %s' % (file_name, base_file) )
        return  None

    def searchCommandPath( self, command_name ):
        for path in self.BIN_PATH_R:
            cur_path= os.path.join( path, command_name )
            if os.path.exists( cur_path ):
                return  cur_path
        return  None

    #--------------------------------------------------------------------------

    def splitExt( self, file_name ):
        return  os.path.splitext( file_name )[0]


    def findPath( self, path_list ):
        for path in path_list:
            if os.path.exists( path ):
                return  path
        return  None

    def findPathPair( self, path_list ):
        for path in path_list:
            if os.path.exists( path[0] ):
                return  path
        return  None,None

    def makeOutputDirectory( self, path ):
        obj_dir= os.path.dirname( path )
        if obj_dir != '' and not os.path.exists( obj_dir ):
            try:
                os.makedirs( obj_dir )
            except FileExistsError:
                pass


    def getOutputPath( self, output_dir, src_file= None ):
        obj_dir= os.path.join( os.path.abspath(output_dir), self.getTargetPlatform(), self.getTargetArch(), self.getConfig() )
        if src_file:
            return  os.path.join( obj_dir, src_file )
        return  obj_dir

    def getObjPath( self, src_file= None ):
        if src_file:
            name= os.path.basename( src_file )
            name= self.splitExt( name )
            src_file= self.getObjName( name )
        return  self.getOutputPath( self.OUTPUT_OBJ_DIR, src_file )

    def getExePath( self, src_file= None ):
        if self.EXE_NAME_FUNC:
            return  os.path.abspath( self.EXE_NAME_FUNC( self, src_file ) )
        if src_file:
            src_file= self.getExeName( src_file )
        return  self.getOutputPath( self.OUTPUT_EXE_DIR, src_file )

    def getLibPath( self, src_file= None ):
        if src_file:
            src_file= self.getLibName( src_file )
        return  self.getOutputPath( self.OUTPUT_LIB_DIR, src_file )

    def getDllPath( self, src_file= None ):
        if src_file:
            src_file= self.getDllName( src_file )
        return  self.getOutputPath( self.OUTPUT_DLL_DIR, src_file )


    def getObjName( self, obj_name ):
        return  obj_name + '.o'

    def getExeName( self, exe_name ):
        return  exe_name

    def getLibName( self, lib_name ):
        return  'lib' + lib_name + '.a'

    def getDllName( self, lib_name ):
        return  'lib' + lib_name + '.so'

    #--------------------------------------------------------------------------

    def getBuildCommand_Link( self, target, src_list ):
        raise   BuildUtility.FLB_Error( 'not implement: getBuildCommand_Link' )
        return  None

    def getBuildCommand_Dll( self, target, src_list ):
        raise   BuildUtility.FLB_Error( 'not implement: getBuildCommand_Dll' )
        return  None

    def getBuildCommand_CC( self, target, src_list ):
        raise   BuildUtility.FLB_Error( 'not implement: getBuildCommand_CC' )
        return  None

    def getBuildCommand_Lib( self, target, src_list ):
        raise   BuildUtility.FLB_Error( 'not implement: getBuildCommand_Lib' )
        return  None

    def getBuildCommand_Lipo( self, target, src_list ):
        raise   BuildUtility.FLB_Error( 'not implement: getBuildCommand_Lipo' )
        return  None

    def createSourceFile( self, file_name ):
        ext= self.splitExt( file_name )
        parser= {
            '.cpp' : Depend.SourceFileC,
            '.cc'  : Depend.SourceFileC,
            '.c'   : Depend.SourceFileC,
            '.mm'  : Depend.SourceFileC,
            '.m'   : Depend.SourceFileC,
            '.metal': Depend.SourceFileC,
            }
        if ext in parser:
            return  parser[ ext ]( self, file_name )
        return  Depend.SourceFileC( self, file_name )

    #--------------------------------------------------------------------------

    def setupBinPath( self ):
        self.BIN_PATH_R= []
        self.BIN_PATH_R.extend( self.BIN_PATH )

    def setupIncludePath( self ):
        self.INCLUDE_PATH_R= []
        self.INCLUDE_PATH_R.extend( self.INCLUDE_PATH )

    def setupLinkLib( self ):
        self.LINK_LIBS_R= []
        self.LINK_LIBS_R.extend( self.LINK_LIBS )

    def setupLibPath( self ):
        self.LIB_PATH_R= []
        self.LIB_PATH_R.extend( self.LIB_PATH )

    def setupCCFlags( self ):
        self.CC_FLAGS_R= []
        self.CC_FLAGS_R.extend( self.CC_FLAGS )

    def setupLinkFlags( self ):
        self.LINK_FLAGS_R= []
        for lib in self.LIB_PATH_R:
            self.LINK_FLAGS_R.append( '-L' + lib )
        self.LINK_FLAGS_R.extend( self.LINK_FLAGS )
        for lib in self.LINK_LIBS_R:
            self.LINK_FLAGS_R.append( '-l' + lib )

    def setupLibFlags( self ):
        self.LIB_FLAGS_R= []
        self.LIB_FLAGS_R.extend( self.LIB_FLAGS )

    def refresh( self ):
        self.setupBinPath()
        self.setupIncludePath()
        self.setupLinkLib()
        self.setupLibPath()

        self.setupCCFlags()
        self.setupLinkFlags()
        self.setupLibFlags()


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

class PlatformError( TargetEnvironmentCommon ):
    def isValid( self ):
        return  False

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

