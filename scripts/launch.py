from package import package
import subprocess

MODLIST = [
    'Multiverse 5.5 - Assets (Patch above Data).zip',
    'Multiverse 5.5.1 - Data.zip',
    'choiceInfo-test.zip',
]

package('choiceInfo-test', 'SlipstreamModManager_1.9.1-Win/mods')
subprocess.run(['SlipstreamModManager_1.9.1-Win/modman.exe', '--runftl', '--patch'] + MODLIST)