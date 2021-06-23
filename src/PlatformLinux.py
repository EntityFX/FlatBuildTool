# FlatBuildTool 2017/07/23 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

import  os
import  PlatformCommon
import  BuildUtility
from BuildUtility import Log


class TargetEnvironment( PlatformCommon.TargetEnvironmentCommon ):

    def __init__( self, tool, parent= None ):
        super().__init__( tool, parent )

        # --opt CC=clang-9
        # --opt CC=gcc
        self.CMD_CC= self.getUserOption( 'CC', 'clang' )
        self.CMD_LINK= self.CMD_CC
        self.CMD_LIB= 'ar'

        self.ARM7ABI= 'hard'
        if self.isTermux():
            if self.getHostArch() == 'arm7':
                self.ARM7ABI= 'softfp'

        # --opt ARM7ABI=hard
        # --opt ARM7ABI=softfp
        # --opt ARM7ABI=soft
        # or 'ARM7ABI hard' in local_config.txt
        self.ARM7ABI= self.getUserOption( 'ARM7ABI', self.ARM7ABI )
        # --opt ARM7FP=neon
        # --opt ARM7FP=vfpv3-d16
        # --opt ARM7FP=neon-vfpv4
        # or 'ARM7FP neon-vfpv4' in local_config.txt
        self.ARM7FP= self.getUserOption( 'ARM7FP', 'neon' )
        # --opt ARM8ARCH=armv8-a+simd+crypto
        # --opt ARM8ARCH=armv8.2-a+simd+crypto+fp16
        # --opt ARM8ARCH=armv8.3-a+simd+crypto+fp16+dotprod
        # or 'ARM8ARCH armv8.2-a+simd+crypto+fp16' in local_config.txt
        self.ARM8ARCH= self.getUserOption( 'ARM8ARCH', 'armv8-a+simd+crypto' )
        # --opt HOST_ARCH=x86
        # or 'HOST_ARCH x86' in local_config.txt
        host_arch= self.getUserOption( 'HOST_ARCH', None )
        if host_arch is not None:
            self.setHostArch( host_arch )
            self.setTargetArch( host_arch )
        # --opt SSE=AVX2
        # --opt SSE=AVX512
        # or 'SSE AVX512' in local_config.txt
        self.SSE= self.getUserOption( 'SSE', 'SSE' )
        self.STD= self.getUserOption( 'STD', '17' )

        self.setDefault()


    def summary( self ):
        super().summary()

    def isValid( self ):
        return  True

    def isTermux( self ):
        if 'HOME' in os.environ:
            if 'com.termux' in os.environ['HOME']:
                return  True
        return  False

    def setDefault( self ):
        self.setTargetPlatform( 'Linux' )

        self.setConfig( 'Debug' )
        self.addCCFlags( '-fpic -Wall -fno-rtti -fno-exceptions -ffast-math'.split() )
        self.addCCFlags( ['-std=c++'+self.STD] )
        self.addCCFlags( '-fmessage-length=0 -pipe -Wno-trigraphs -Wreturn-type -gdwarf-2 -DFLB_FORCE_LINUX=1 -DFLB_TARGET_LINUX=1'.split() )
        #self.addCCFlags( '-funwind-tables -fstack-protector-strong -no-canonical-prefixes'.split() )

        self.addLibraries( [ 'stdc++', 'pthread', 'm'] )

        self.refresh()

    #--------------------------------------------------------------------------

    def setupCCFlags( self ):

        self.CC_FLAGS_R= []
        table_config= {
                'Debug'   : "-O0 -g -D_DEBUG",
                'Release' : "-Os -g -O3 -DNDEBUG",
                'Retail'  : "-Os -O3 -DNDEBUG -DFLB_RETAIL=1",
            }
        self.CC_FLAGS_R.extend( table_config[ self.getConfig() ].split() )

        avx_opt= ''
        if self.SSE == 'AVX512':
            avx_opt= ' -mavx2 -mfma -mavx512f -mavx512vl -mavx512bw -mavx512dq -mavx512vnni -mf16c'
        elif self.SSE == 'AVX2':
            avx_opt= ' -mavx2 -mfma -mf16c'
        table_arch= {
            'x86':   '-m32 -msse -msse2 -msse3 -mssse3 -maes' + avx_opt,
            'x64':   '-m64 -msse -msse2 -msse3 -mssse3 -msse4.1 -msse4.2 -maes' + avx_opt,
            'arm7':  '-march=armv7-a -fPIC -marm -mfpu=%s -mfloat-abi=%s' % (self.ARM7FP, self.ARM7ABI),
            'arm6':  '-march=armv6 -marm -mfpu=vfp -mfloat-abi=hard',
            'arm64': '-march=' + self.ARM8ARCH,
            'e2k':   '',
            }
        self.CC_FLAGS_R.extend( table_arch[ self.getTargetArch() ].split() )

        for inc in self.INCLUDE_PATH_R:
            #print( 'INCLUDE=' + inc )
            self.CC_FLAGS_R.append( '-I' + inc )
        self.CC_FLAGS_R.extend( self.CC_FLAGS )

    #--------------------------------------------------------------------------

    def getBuildCommand_CC( self, target, src_list ):
        command= []
        command.append( self.CMD_CC )
        command.append( '-c' )
        command.extend( self.CC_FLAGS_R )
        for src in src_list:
            command.append( src )
        command.append( '-o' )
        command.append( target )
        return  command

    def getBuildCommand_Link( self, target, src_list ):
        command= []
        command.append( self.CMD_CC )
        command.append( '-o' )
        command.append( target )
        for src in src_list:
            command.append( src )
        command.extend( self.LINK_FLAGS_R )
        return  command

    def getBuildCommand_Dll( self, target, src_list ):
        command= []
        command.append( self.CMD_CC )
        command.append( '-shared' )
        command.append( '-o' )
        command.append( target )
        for src in src_list:
            command.append( src )
        command.extend( self.LINK_FLAGS_R )
        return  command

    def getBuildCommand_Lib( self, target, src_list ):
        command= []
        command.append( BuildUtility.RemoveFile )
        command.append( target )
        command.append( ';;' )
        command.append( self.CMD_LIB )
        command.append( 'crs' )
        command.append( target )
        for src in src_list:
            command.append( src )
        command.extend( self.LIB_FLAGS_R )
        return  command

