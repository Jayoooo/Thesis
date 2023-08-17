import os
import sys
import glob
import signal
import argparse
import logging
import pickle

bfrt_location = '{}/lib/python*/site-packages/tofino'.format(
    os.environ['SDE_INSTALL'])
sys.path.append(glob.glob(bfrt_location)[0])
import bfrt_grpc.client as gc
import bfrt_grpc.bfruntime_pb2 as bfruntime_pb2

from ports import Ports
from common import front_panel_regex, mac_address_regex, validate_ip

ML_location = '../ML'
sys.path.append(glob.glob(ML_location)[0])
from rf2tna import DMTable, DMLevelEntry, CODE_TABLE


class simple_controller(object):
    def __init__(self):
        super(simple_controller, self).__init__()

        self.log = logging.getLogger(__name__)
        self.log.info('Simple controller')

    def critical_error(self, msg):
        self.log.critical(msg)
        print(msg, file=sys.stderr)
        logging.shutdown()
        # sys.exit(1)
        os.kill(os.getpid(), signal.SIGTERM)

    def setup(self, program, switch_mac,
              switch_ip,
              bfrt_ip,
              bfrt_port,
              ports_file,
              folded_pipe=False):
        # Device 0
        self.dev = 0
        # Target all pipes
        self.target = gc.Target(self.dev, pipe_id=0xFFFF)
        # Folded pipe
        self.folded_pipe = folded_pipe

        # Connect to BFRT server
        try:
            interface = gc.ClientInterface('{}:{}'.format(bfrt_ip, bfrt_port),
                                           client_id=0,
                                           device_id=self.dev)
        except RuntimeError as re:
            msg = re.args[0] % re.args[1]
            self.critical_error(msg)
        else:
            self.log.info('Connected to BFRT server {}:{}'.format(
                bfrt_ip, bfrt_port))

        try:
            interface.bind_pipeline_config(program)
        except gc.BfruntimeForwardingRpcException:
            self.critical_error('P4 program {} not found!'.format(program))

        try:
            # interface.clear_all_tables()

            # Get all tables for program
            self.bfrt_info = interface.bfrt_info_get(program)

            self.addDirectionRule()
            self.setIPv4forward()
            # self.getDirectionRule()

            self.setdecisiontree()

        except KeyboardInterrupt:
            self.critical_error('Stopping controller.')
        except Exception as e:
            self.log.exception(e)
            print(e)
            self.critical_error('Unexpected error. Stopping controller.')

    def addDirectionRule(self, ip="149.171.126.0", prefix_len=24):
        check_direction = self.bfrt_info.table_get("MyIngress.check_direction")

        check_direction.info.key_field_annotation_add(
            'hdr.ipv4.dst_addr', 'ipv4')

        keys = [check_direction.make_key(
            [gc.KeyTuple('hdr.ipv4.dst_addr', ip, prefix_len=prefix_len)])]
        data = [check_direction.make_data(
            data_field_list_in=[], action_name='MyIngress.set_direction')]

        check_direction.entry_add(self.target, keys, data)

    def getDirectionRule(self):
        check_direction = self.bfrt_info.table_get("MyIngress.check_direction")
        check_direction.info.key_field_annotation_add(
            'hdr.ipv4.dst_addr', 'ipv4')
        keys = [check_direction.make_key(
            [gc.KeyTuple('hdr.ipv4.dst_addr', "149.171.126.0", prefix_len=24)])]
        resp = check_direction.entry_get(self.target, keys, {"from_hw": False})
        data_dict = next(resp)[0].to_dict()
        print(data_dict)

    def addLevelEntry(self, tbl, prev_node, isLarge=1, now_node=None, threshold=None, action_name="CheckFeature1", class_num=0):
        keys = [tbl.make_key([gc.KeyTuple('eg_md.eg_meta.node_id', prev_node),
                              gc.KeyTuple('eg_md.meta.isTrue', isLarge)])]
        if "SetClass" in action_name:
            data = [tbl.make_data(data_field_list_in=[gc.DataTuple('class', class_num)],
                                  action_name='MyEgress.classify.SetClass')]

        else:
            data = [tbl.make_data(data_field_list_in=[gc.DataTuple('node_id', now_node),
                                                      gc.DataTuple('threshold', threshold)],
                                  action_name=f'MyEgress.classify.{action_name}')]
        tbl.entry_add(self.target, keys, data)

    def setdecisiontree(self):
        f = open("../ML/DM_rules.pickle", 'rb')
        DM_TABLES = pickle.load(f)
        f.close()

        levels = []
        for lv, dm_tbl in DM_TABLES.items():
            lv_tbl = self.bfrt_info.table_get(
                f"MyEgress.classify.level{lv}")
            for entry in dm_tbl.entries:
                self.addLevelEntry(lv_tbl, **entry.field)

        # check get
        # resp = level1.entry_get(self.target, keys, {"from_hw": False})
        # data_dict = next(resp)[0].to_dict()
        # print(data_dict)

    def setIPv4forward(self):
        ipv4 = self.bfrt_info.table_get(
            "MyIngress.ipv4_lpm")
        ipv4.info.key_field_annotation_add(
            'hdr.ipv4.dst_addr', 'ipv4')

        keys = [ipv4.make_key(
            [gc.KeyTuple('hdr.ipv4.dst_addr', f"0.0.0.0", prefix_len=0)])]
        data = [ipv4.make_data(data_field_list_in=[gc.DataTuple(
            'port', 1)], action_name='MyIngress.ipv4_forward')]
        # ipv4.entry_del(self.target, keys)
        ipv4.entry_add(self.target, keys, data)


if __name__ == '__main__':

    # Parse arguments
    argparser = argparse.ArgumentParser(description='simple controller.')
    argparser.add_argument('--program',
                           type=str,
                           default='switchtree',
                           help='P4 program name.')
    argparser.add_argument(
        '--bfrt-ip',
        type=str,
        default='127.0.0.1',
        help='Name/address of the BFRuntime server. Default: 127.0.0.1')
    argparser.add_argument('--bfrt-port',
                           type=int,
                           default=50052,
                           help='Port of the BFRuntime server. Default: 50052')
    argparser.add_argument(
        '--switch-mac',
        type=str,
        default='00:11:22:33:44:55',
        help='MAC address of the switch. Default: 00:11:22:33:44:55')
    argparser.add_argument('--switch-ip',
                           type=str,
                           default='10.0.0.254',
                           help='IP address of the switch. Default: 10.0.0.254')
    argparser.add_argument(
        '--ports',
        type=str,
        default='ports.yaml',
        help='YAML file describing machines connected to ports. Default: ports.yaml')
    argparser.add_argument(
        '--enable-folded-pipe',
        default=False,
        action='store_true',
        help='Enable the folded pipeline (requires a 4 pipes switch)')
    argparser.add_argument('--log-level',
                           default='INFO',
                           choices=['ERROR', 'WARNING', 'INFO', 'DEBUG'],
                           help='Default: INFO')

    args = argparser.parse_args()

    # Configure logging
    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        sys.exit('Invalid log level: {}'.format(args.log_level))

    logformat = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='copy_switchtree.log',
                        filemode='w',
                        level=numeric_level,
                        format=logformat,
                        datefmt='%H:%M:%S')

    args.switch_mac = args.switch_mac.strip().upper()
    args.switch_ip = args.switch_ip.strip()
    args.bfrt_ip = args.bfrt_ip.strip()

    if not mac_address_regex.match(args.switch_mac):
        sys.exit('Invalid Switch MAC address')
    if not validate_ip(args.switch_ip):
        sys.exit('Invalid Switch IP address')
    if not validate_ip(args.bfrt_ip):
        sys.exit('Invalid BFRuntime server IP address')

    controller = simple_controller()
    controller.setup(args.program, args.switch_mac, args.switch_ip, args.bfrt_ip,
                     args.bfrt_port, args.ports, args.enable_folded_pipe)
