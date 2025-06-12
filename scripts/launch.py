from package import package
import run
from sys import argv
import subprocess

MODLIST = [
    'Multiverse 5.5 - Assets (Patch above Data).zip',
    'Multiverse 5.5.1 - Data.zip',
    'choiceInfo-test.zip',
]

if __name__ == '__main__':
    if len(argv) > 1 and argv[1] == '--run':
        run.main()

    package('choiceInfo-test', 'SlipstreamModManager_1.9.1-Win/mods')
    subprocess.run(['SlipstreamModManager_1.9.1-Win/modman.exe', '--runftl', '--patch'] + MODLIST)