from os import path, system

def init():
    if (not path.exists('database.db')):
        system('python3 init.py')

    
if __name__ == '__main__':
    init()
