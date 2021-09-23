import csv

def begin(lines, first, last):
    code=''
    for i in range(first,last+1):
        code+=lines[i-1]
    code+='\n'
    return code

def end():
    code=''
    code+='PAUSE\n'
    code+='PAUSE\n'
    code+='ENDFIL\n'
    code+='\n'
    return code


def initial_position(x=843.355,y=-52.23,z=507.975):
    code='$$<MULTI_INSPECT name = "Groupe - PNTStart">\n'
    code+='GOTO/CART,{},{},{}\n'.format(x,y,z)
    code+='$$<\MULTI_INSPECT = Groupe - PNTStart>\n'
    code+='\n'
    return code

def passage(x,y,z):
    code='GOTO/CART,{},{},{}\n'.format(x,y,z)
    return code

def meas(x,y,z,u,v,w,suffix,pre_passage='',post_passage=''):
    code='$$<MULTI_INSPECT name = "Groupe - {}">\n'.format(suffix)
    if pre_passage: code+=pre_passage
    if "F" in suffix or "H" in suffix:
        code+='$$<MEAS_POINT name = "{}: 0.00,0.00,0.00, 0.00,-1.00,0.00">\n'.format(suffix)
        code+='F({})=FEAT/POINT,CART,0,0,0,0,-1,0\n'.format(suffix)
    elif "S" in suffix:
        code+='$$<MEAS_POINT name = "{}: 0.00,0.00,0.00, -1.00,0.00,0.00">\n'.format(suffix)
        code+='F({})=FEAT/POINT,CART,0,0,0,-1,0,0\n'.format(suffix)
    elif "E" in suffix:
        code+='$$<MEAS_POINT name = "{}: 0.00,0.00,0.00, 0.00,0.00,1.00">\n'.format(suffix)
        code+='F({})=FEAT/POINT,CART,0,0,0,0,0,1\n'.format(suffix)
    code+='MEAS/POINT,F({}),1\n'.format(suffix)
    code+='PTMEAS/CART,{},{},{},{},{},{}\n'.format(x,y,z,u,v,w)
    if post_passage: code+=post_passage
    code+='ENDMES\n'
    code+='$$<\MEAS_POINT >\n'
    code+='$$<\MULTI_INSPECT = Groupe - {}>\n'.format(suffix)
    code+='\n'
    return code

def dist(name):
    axis,pln = "Y",'PLN_Gabarit_Décalé'
    if "S" in name: 
        axis,pln = "X",'PNT_Décalé'
    if "E" in name:
        axis,pln = "Z",'LINE001'
    short_name = name.replace('PNT','')
    code = ''
    code+='T({})=TOL/DISTWRT,NOMINL,0,-0.1,0.1,'.format(short_name)
    code+='FA({}),{}AXIS,AVG\n'.format(pln,axis)
    code+='OUTPUT/FA({}),TA({})\n'.format(name,short_name)
    code+='\n'
    return code

def read_file(filename):
    points = ['F1','F2','F3','F4','F5']
    points += ['H1','H2','H3','H4','H5','H6']
    points += ['S1','S2','S3']
    points += ['E1','E2','E3']
    inserts = ['A','B','C','D','E']
    lines = []
    with open(filename, encoding = "ISO-8859-1") as f:
        lines = f.readlines()
    #--------------------#
    f = open('input.csv', 'w')
    for nb,line in enumerate(lines):
        for insert in inserts:
            # 
            for point in points:
                name="PNT{}02{}".format(insert,point)
                if "MEAS/POINT,F({})".format(name) in line and name in line: 
                    row = lines[nb+1].rstrip().replace('PTMEAS/CART',name)
                    #print(row)
                    f.write('{}\n'.format(row))
    f.close()
    return lines
    #--------------------#

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#

if __name__ == "__main__":
    ###
    lines = read_file('Test_Emery-1.dmi')
    modules =['02','04','08']
    rel_dist=[0,199,590]
    ###
    Points,Names=[],[]
    with open('input.csv', newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            Points.append(row)
            name = row[0]
    mMax=len(modules)
    pMax=len(Points)
    ###
    with open("python_test2.dmi","w") as f:
        #############################
        f.write(begin(lines,1,145))
        #############################
        f.write(initial_position(840.45,-65.521,507.968)) #(843.355,-52.23,507.975)
        #############################
        # Modules
        for idx,m in enumerate(modules):
            # All points in module idx
            for p,Point in enumerate(Points):
                name = Point[0]
                x,y,z,u,v,w = Point[1],Point[2],Point[3],Point[4],Point[5],Point[6]
                # translation along X
                if idx>0:
                    s = name
                    name = s.replace(modules[0],m)
                    x = float(x)-rel_dist[idx]
                # temporally removing some points #################################
                if "A04S" in name or "D04S" in name: continue #####################
                #print(name,x,y,z,u,v,w)
                passage_,passage__= '',''
                if "F1" in name:
                    passage_= passage(x,float(y)-50.,z)
                if "S1" in name:
                    passage_= passage(float(x)+2.,float(y)-50.,z)
                if "E1" in name:
                    passage_= passage(x,float(y)-50.,z)
                    #passage_+= passage(x,float(y)-50.,z)
                if p==pMax-1 or 'S3' in name:
                    passage__= passage(x,float(y)-50.,z)
                ##
                f.write(meas(x,y,z,u,v,w,name,passage_,passage__))
                Names.append(name)
            ###
            f.write(4*'\n')
        ###
        for name in Names:
            f.write(dist(name))
            ###
        f.write(4*'\n')
        ###
        f.write(end())