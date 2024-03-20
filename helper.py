def read_target():
    target=None
    with open('mining.txt', 'r') as file:
        lines = file.readlines()
        if (len(lines)>0):
            target = lines[0].strip()
    return target

def write_target(target):
    lines=[]
    with open('mining.txt', 'r') as file:
        lines=file.readlines()
    with open('mining.txt', 'w') as file:
        if (len(lines)>0):
                lines[0]=target+'\n'
                file.writelines(lines)
                return True
        else:
            lines.insert(0,target+'\n')
            file.writelines(lines)
            return True

    return False
    

def read_username():
    username=None
    with open('mining.txt', 'r') as file:
        lines = file.readlines()
        if (len(lines)>1):
            username = lines[1].strip()
    return username

def write_username(username):
    lines=[]
    with open('mining.txt', 'r') as file:
        lines=file.readlines()
    with open('mining.txt', 'w') as file:
        if (len(lines)>1):
                lines[1]=username+'\n'
                file.writelines(lines)
                return True
        else:
            lines.insert(1,username+'\n')
            file.writelines(lines)
            return True
    return False
        
