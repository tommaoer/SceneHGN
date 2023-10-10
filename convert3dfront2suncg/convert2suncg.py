import json, copy, math, igl, os
import numpy as np
from dataclasses import dataclass, field
from shutil import copyfile, copytree
def rotation_matrix(axis, theta):
    axis = np.asarray(axis)
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])
@dataclass
class Object():
    id: str = ''
    type: str = ''
    pos: list = field(default_factory=list)
    rot: list = field(default_factory=list)
    scale: list = field(default_factory=list)
    bbox: dict = field(default_factory=dict)

@dataclass
class House(Object):
    rooms: dict = field(default_factory=dict)
    
@dataclass
class Room(Object):
    # models = {}
    # def add_model():
    models: list = field(default_factory=list)
@dataclass
class Model(Object):
    uid: str = ''
    jid: str = ''
    rotm: list = field(default_factory=list)
    valid: bool = False
    obbox: list = field(default_factory=list)
    size: list = field(default_factory=list)


def save_room(jsonfile):
    readpath = 'D:/ali/3D-FRONT-ToolBox/scripts/process/room2/'
    with open(jsonfile,'r',encoding='utf-8') as f:
        data = json.load(f)
        room = data['scene']['room']
        idx = 0
        for r in room:
            # if r['type'] == 'none':
            #     continue
            if os.path.exists(readpath+'/'+data['uid']+'/'+r['instanceid']+'_floor.obj'):
                copyfile(readpath+'/'+data['uid']+'/'+r['instanceid']+'_floor.obj',readpath+'/'+data['uid']+'/'+'fr_0rm'+str(idx)+'f.obj')
            if os.path.exists(readpath+'/'+data['uid']+'/'+r['instanceid']+'_wall.obj'):
                copyfile(readpath+'/'+data['uid']+'/'+r['instanceid']+'_wall.obj',readpath+'/'+data['uid']+'/'+'fr_0rm'+str(idx)+'w.obj')
            idx += 1
def read_json_3dfront(jsonfile):
    
    with open(jsonfile,'r',encoding='utf-8') as f:
        data = json.load(f)
        house = House(id=data['uid'])
        # v, _, _, _, _, _ = igl.read_obj('//10.41.0.202/yangjie/yangjie/scene/data/3D-FRONTnew/meshes/'+data['uid']+'/scene.obj')
        # house.bbox['min'] = np.min(v, axis = 0).tolist()
        # house.bbox['max'] = np.max(v, axis = 0).tolist()
        
        models = {}
        for ff in data['furniture']:
            if 'size' in ff:
                if 'valid' in ff and not ff['valid']:
                    continue
                models[ff['uid']]=Model(uid = ff['uid'], jid = ff['jid'], type='none', size = ff['size'], obbox = ff['bbox'] if 'bbox' in ff else None, valid = ff['valid'] if 'valid' in ff else False)



        room = data['scene']['room']
        rooms = {}
        for r in room:
            if r['instanceid'] == 'none':
                continue
            if not r['type'] in ['DiningRoom','LivingDiningRoom','Bedroom','LivingRoom','SecondBedroom','MasterBedroom']:
                continue
            rooms[r['instanceid']] = Room(id = r['instanceid'],type = r['type'])
            try:
                # v, _, _, _, _, _ = igl.read_obj('D:/ali/3D-FRONT-ToolBox/scripts/process/room/'+data['uid']+'/'+r['instanceid']+'_wall.obj')
                v, _, _, _, _, _ = igl.read_obj('//10.206.32.17/yangjie/yangjie/scene/data/3D-FRONTnew/meshesnoceilling/'+data['uid']+'/'+r['instanceid']+'/'+'mesh_noceilling.obj')
            except:
                continue
            try:
                rooms[r['instanceid']].bbox['min'] = np.min(v, axis = 0).tolist() #*100
                rooms[r['instanceid']].bbox['max'] = np.max(v, axis = 0).tolist() #*100
            except:
                continue
            # print(room_center = rooms[r['instanceid']].bbox)
            # cc()
            number = 1
            for c in r['children']:
                if c['ref'] in models:
                    m = copy.deepcopy(models[c['ref']])
                    # if not os.path.exists('//10.41.0.202/yangjie/yangjie/scene/data/3D-FRONTnew/meshes/'+data['uid']+'/'+r['instanceid']+'/'+str(number)+'_'+m.jid+'.obj'):
                    #     continue
                    #     
                    #     
                    # cc()
                    scale = np.array([1.,1.,1.])
                    if os.path.exists('E:/3D-FUTURE-model/3D-FUTURE-model/' + models[c['ref']].jid + '/raw_model.obj') or os.path.exists('E:/3D-FUTURE-model/3D-FUTURE-model/' + models[c['ref']].jid + '/raw_model_tri.obj'):
                        try:
                            v, _, _, _, _, _ = igl.read_obj('E:/3D-FUTURE-model/3D-FUTURE-model/' + models[c['ref']].jid + '/raw_model.obj')
                        except Exception as e:
                            try:
                                v, _, _, _, _, _ = igl.read_obj('E:/3D-FUTURE-model/3D-FUTURE-model/' + models[c['ref']].jid + '/raw_model_tri.obj')
                            except Exception as e:
                                continue

                        scale = c['scale']
                    elif os.path.exists('D:/ali/3D-FRONT-ToolBox/scripts/process/object/' + models[c['ref']].jid):
                        try:
                            v, _, _, _, _, _ = igl.read_obj('D:/ali/3D-FRONT-ToolBox/scripts/process/object/' + models[c['ref']].jid + '/'+models[c['ref']].jid+'.obj')
                        except:
                            continue
                        if models[c['ref']].size is not None:
                            bbox = np.max(v, axis=0) - np.min(v, axis=0)
                            s = bbox / models[c['ref']].size
                        scale /= s
                        if models[c['ref']].obbox is not None:
                            bbox = np.max(v, axis=0) - np.min(v, axis=0)
                            s = bbox / models[c['ref']].obbox[0]
                            # print(bbox,models[c['ref']].obbox, s)
                        scale /= s
                        scale *= c['scale']
                        # print(scale)
                        # cc()
                    else:
                        continue

                    # print(scale)
                   
                    # cc()
                    # print(models[c['ref']])
                    



                    m.bbox['min'] = np.min(v, axis = 0).tolist()
                    m.bbox['max'] = np.max(v, axis = 0).tolist()


                    m.pos = c['pos']
                    m.rot = c['rot']
                    m.scale = scale
                    ref = [0,0,1]
                    axis = np.cross(ref, m.rot[1:])
                    theta = np.arccos(np.dot(ref, m.rot[1:]))*2
                    # if r['instanceid'] == 'SecondBedroom-12951':
                    #     print(c['ref'],axis,  theta*180/math.pi)
                    t = np.zeros([4,4])
                    t[3,3] = 1
                    if np.sum(axis) != 0 and not math.isnan(theta):
                        t[:3,:3] = rotation_matrix(axis, theta).transpose()
                    else:
                        t[0,0]=1
                        t[1,1]=1
                        t[2,2]=1
                    t_scale = np.asarray([[m.scale[0], 0, 0, 0], \
                                        [0, m.scale[1], 0, 0], \
                                        [0, 0, m.scale[2], 0], \
                                        [0, 0, 0, 1]])
                    t_shift = np.asarray([[1, 0, 0, 0], \
                                        [0, 1, 0, 0], \
                                        [0, 0, 1, 0], \
                                        [m.pos[0],m.pos[1], m.pos[2], 1]])

                    m.rotm = np.dot(np.dot(t_scale, t), t_shift)
                    
                    
                    rooms[r['instanceid']].models.append(m)
        house.rooms = rooms
    return house
def read_json_suncg_pure(jsonfile):
    with open(jsonfile,'r',encoding='utf-8') as f:
        data = json.load(f)
        house = House(id=data['id'])
        models = {}
        rooms = {}
        for ff in data['levels'][0]['nodes']:
            if 'valid' in ff and ff['type'] in ['Object', 'Box']:
                bbox=[]
                models[ff['id']]=Model(id = ff['id'], uid = ff['modelId'] if 'modelId' in ff else 'Box', jid = ff['modelId'] if 'modelId' in ff else 'Box', bbox = bbox, type='Object', rotm = np.array(ff['transform']).reshape((4,4)),valid = ff['valid'])
        for ff in data['levels'][0]['nodes']:
            if 'valid' in ff and ff['valid'] and ff['type'] == 'Room':
                modelid = ff['modelId']
                # print(modelid)
                rooms[modelid] = Room(id = modelid,type = ff['roomTypes'][0] if len(ff['roomTypes']) > 0 else None)
                if 'nodeIndices' in ff:
                    for nodes in ff['nodeIndices']:
                        rooms[modelid].models.append(models['0_'+str(nodes)])
                # print(room_model)
        house.rooms = rooms
        return house
def read_json_suncg(jsonfile,model_info = None):
    with open(jsonfile,'r',encoding='utf-8') as f:
        data = json.load(f)
        house = House(id=data['id'])
        # front_path = 'D:/ali/3D-FRONT_new/3D-FRONT'
        # front_data = json.load(open((front_path+'/'+data['id']+'.json'),'r',encoding='utf-8'))
        # front_room = []
        # for r in front_data['scene']['room']:
        #     front_room.append(r['instanceid'])
            
        models = {}
        rooms = {}
        for ff in data['levels'][0]['nodes']:
            if 'valid' in ff and ff['valid'] and ff['type'] == 'Object':
                type = 'Object'

                models[ff['id']]=Model(id = ff['id'], uid = ff['modelId'], jid = ff['modelId'], bbox = None, type=type, rotm = np.array(ff['transform']).reshape((4,4)))
        for ff in data['levels'][0]['nodes']:
            if 'valid' in ff and ff['valid'] and ff['type'] == 'Room':
                modelid = ff['modelId']#.split('_')[1][3:]
                rooms[modelid] = Room(id = modelid,type = ff['roomTypes'][0])
                for nodes in ff['nodeIndices']:
                    rooms[modelid].models.append(models['0_'+str(nodes)])
                # print(room_model)
        house.rooms = rooms
        return house
        # cc()

def save_json_3dfront(house, jsonfile):
    results = {}
    results['uid'] = house.id
    results['furniture'] = []
    results['scene'] = {}
    results['scene']['room']=[]
    for room in house.rooms:
        r = {}
        r['type'] = house.rooms[room].type
        # print(r['type'])
        r['instanceid'] = house.rooms[room].id
        r['children'] = []
        for m in house.rooms[room].models:
            child = {}
            child['ref'] = m.id
            rotm = m.rotm
            child['rotscale'] = rotm[:3,:3].tolist()
            child['pos'] = rotm[3,:3].tolist()
            r['children'].append(child)
            f = {}
            f['uid'] = m.id
            f['jid'] = m.jid
            f['category'] = m.type
            f['valid'] = m.valid
            results['furniture'].append(f)
        results['scene']['room'].append(r)
    # cc()
    with open(jsonfile, 'w') as f:
        json.dump(results, f)




def save_json_suncg(house,jsonfile):
    results = {}
    results['id'] = house.id
    results['up'] = [0,1,0]
    results['front'] = [0,0,1]
    results['scaleToMeters'] = 1
    results['levels'] = []
    levels = {}
    levels['id'] = '0'
    levels['bbox'] = house.bbox
    levels['nodes'] = []
    room_num = len(house.rooms)
    room_nodes = []
    models_nodes = []
    bias = room_num
    for r,idx in zip(house.rooms,range(room_num)):
        # print(r)
        # cc()
        room_node = {}
        room_node['id'] = '0_'+str(idx)
        room_node['type'] = 'Room'
        room_node['valid'] = 1
        room_node['modelId'] = 'fr_0rm'+str(idx)
        room_node['roomTypes'] = [house.rooms[r].type]
        room_node['bbox'] = house.rooms[r].bbox
        room_node['nodeIndices'] = []
        room_node['instanceid'] = r

        readpath = 'D:/ali/3D-FRONT-ToolBox/scripts/process/room_/'
        savepath = 'D:/ali/3D-FRONT-ToolBox/scripts/process/room/'
        if not os.path.exists(savepath+'/'+house.id+'/'):
            os.mkdir(savepath+'/'+house.id+'/')
        if os.path.exists(readpath+'/'+house.id+'/'+r+'_floor.obj'):
            copyfile(readpath+'/'+house.id+'/'+r+'_floor.obj',savepath+'/'+house.id+'/'+'fr_0rm'+str(idx)+'f.obj')
        else:
            continue
        if os.path.exists(readpath+'/'+house.id+'/'+r+'_wall.obj'):
            copyfile(readpath+'/'+house.id+'/'+r+'_wall.obj',savepath+'/'+house.id+'/'+'fr_0rm'+str(idx)+'w.obj')
        else:
            continue


        for m in house.rooms[r].models:
            room_node['nodeIndices'].append(bias)
            model_node = {}
            model_node['id'] = '0_'+str(bias)
            model_node['type'] = 'Object'
            model_node['valid'] = 1
            model_node['modelId'] = m.jid
            model_node['transform'] = m.rotm.flatten().tolist()
            model_node['materials'] = []
            model_node['state'] = 0
            model_node['bbox'] = m.bbox
            models_nodes.append(model_node)
            bias += 1
        room_nodes.append(room_node)
    levels['nodes'] = room_nodes + models_nodes
    results['levels'].append(levels)
    with open(jsonfile, 'w') as f:
        json.dump(results, f)


def save_results(jsonpath, savepath,model_info = None):
    import os
    # jsonpath = '//10.41.0.210/zhanglingxiao/deep-synth/deep-synth/results/'
    # model_info = 'E:/3D-FUTURE-model/model_info.json'
    files = os.listdir(jsonpath)
    # savepath = './b/'
    if not os.path.exists(savepath):
        os.mkdir(savepath)
    for j in files:
        if 'png' in j or not 'final' in j:
            continue
        print(jsonpath+'/'+j)
        # cc()
        if model_info is None:
            h = read_json_suncg_pure(jsonpath+'/'+j)
        else:
            h = read_json_suncg(jsonpath+'/'+j,model_info)
        save_json_3dfront(h,savepath+'/'+j)

def copy_ori(jsonpath):
    import os
    # jsonpath = 'D:/ali/3D-FRONT-ToolBox/scripts/b/'
    files = os.listdir(jsonpath)
    for j in files:
        if not 'json' in j:
            continue
        data = json.load(open(jsonpath+'/'+j,'r'))
        if not os.path.exists(jsonpath+'/ori/'):
            os.mkdir(jsonpath+'/ori/')
        if not os.path.exists(jsonpath+'/ori/'+j[:-5]):
            os.mkdir(jsonpath+'/ori/'+j[:-5])
        if os.path.exists(jsonpath+'ori/'+j[:-5]+'/'+data['scene']['room'][0]['instanceid']):
            continue
        copytree('D:/ali/3D-FRONT-ToolBox/scripts/outputs/'+data['uid']+'/'+data['scene']['room'][0]['instanceid'],jsonpath+'ori/'+j[:-5]+'/'+data['scene']['room'][0]['instanceid'])

        copyfile('//10.41.0.202/yangjie/yangjie/scene/data/3D-FRONTnew/meshesnoceilling/'+data['uid']+'/'+data['scene']['room'][0]['instanceid']+'/mesh_noceilling.obj',jsonpath+'ori/'+j[:-5]+'/'+data['scene']['room'][0]['instanceid']+'/mesh.obj')
        # cc()
        
        


if __name__ == "__main__":


    # jsonpath = 'D:/ali/3D-FRONT-ToolBox\scripts\exp\scene_gen\suncg/living'
    # savepath = 'D:/ali/3D-FRONT-ToolBox\scripts\exp\scene_gen\suncg/living_2_3dfront'
    # save_results(jsonpath, savepath)


    # copy_ori(savepath)

    # jsonfile = 'house.json'
    # model_info = 'E:/3D-FUTURE-model/model_info.json'
    # # read_json_suncg(jsonfile,model_info)

    # h = read_json_3dfront('D:/ali/3d-front_test/a.json')
    # save_json_suncg(h,'D:/ali/3d-front_test/b.json')
    # h = read_json_suncg('D:/ali/3d-front_test/b.json')
    # save_json_3dfront(h,'D:/ali/3d-front_test/c.json')
