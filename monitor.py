import subprocess
import time
from pymongo import MongoClient


def cpu_output_parse(output):
    row_data = output.split("load average:")[1].split("\n")[0]
    str_data = row_data.split(',')
    data = [float(d) for d in str_data]
    data = dict(
        cpu_load_data=dict(
            lables=['1min', '5min', '10min'],
            data=data,
        ),
    )
    return data


#  1min  5min  10min
# [0.48, 0.54, 0.45]


def memory_output_parse(output):
    str_data = output.split("Mem:")[1].split('\n')[0].split(' ')
    data = [int(d) for d in str_data if d != '']
    data = dict(
        mem_io_data=dict(
            lables=['total', 'used', 'free ', 'shared', 'buffers', 'cached'],
            data=data,
        ),
    )
    return data


#  total    used     free    shared  buffers  cached
# [4047400, 3563016, 484384, 23796, 113028, 1319404]


def disk_output_parse(output):
    avg_cpu_row_data = output.split('""')[3].strip().split(' ')
    avg_cpu_data = [float(d) for d in avg_cpu_row_data if d != '']
    device_disk_row_data = output.split('da')[1].split('\n')[0].split(' ')
    device_disk_data = [d for d in device_disk_row_data if d != '']
    for k, v in enumerate(device_disk_data):
        if str.isdigit(v):
            device_disk_data[k] = int(v)
        else:
            device_disk_data[k] = float(v)
    data = dict(
        avg_cpu_data=dict(
            lables=['user', 'nice', 'system', 'iowait', 'steal', 'idle'],
            data=avg_cpu_data,
        ),
        device_disk_data=dict(
            lables=['tps', 'kB_read/s', 'kB_wrtn/s', 'kB_read', 'kB_wrtn'],
            data=device_disk_data,
        ),
    )
    return data


#  user   nice system iowait steal idle
# [9.55, 0.05, 4.35, 0.04, 0.0, 86.01]
#  tps    kB_read/s   kB_wrtn/s    kB_read    kB_wrtn
# [3.63,  35.48,      51.4,       1180775,   1710696]


def get_output(message):
    output = ''
    pipe = subprocess.Popen(message, shell=True, stdout=subprocess.PIPE)
    output_for_line = (line.decode('utf-8') for line in pipe.stdout)
    for o in output_for_line:
        output += '"{}"'.format(o)
    return output


def db_init():
    client = MongoClient()
    db = client.monitor
    collection = db.dataset
    return collection


coll = db_init()

cmd = {'iostat': disk_output_parse,
       'uptime': cpu_output_parse,
       'free': memory_output_parse,
       }


# 查看cpu负载
# uptime

# 查看磁盘使用
# iostat

# 查看内存使用
# free
def write_document():
    data = {}
    document = {}
    for message, func in cmd.items():
        output = get_output(message)
        parsed_output = func(output)
        data.update(parsed_output)
    document.update({'datasets': data, 'created_time': time.time()})
    coll.insert_one(document)


def monitor():
    while True:
        write_document()
        time.sleep(5)


if __name__ == "__main__":
    monitor()
    # document = {'created_time': 1470197630.909462,
    #         'datasets': {
    #             'mem_io_data': {'lables': ['total', 'used', 'free ', 'shared', 'buffers', 'cached'],
    #                             'data': [4047400, 2312772, 1734628, 14168, 82656, 983368]},
    #             'device_disk_data': {'lables': ['tps', 'kB_read/s', 'kB_wrtn/s', 'kB_read', 'kB_wrtn'],
    #                                  'data': [28.52, 501.87, 152.95, 940691, 286692]},
    #             'avg_cpu_data': {'lables': ['user', 'nice', 'system', 'iowait', 'steal', 'idle'],
    #                              'data': [13.94, 0.85, 3.98, 0.19, 0.0, 81.04]},
    #             'cpu_load_data': {'lables': ['1min', '5min', '10min'], 'data': [0.01, 0.21, 0.31]}}}

