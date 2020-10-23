import py4cytoscape as py4
import pandas as pd
import os
import uuid
from logging import getLogger, INFO
from concurrent_log_handler import ConcurrentRotatingFileHandler
from time import sleep
import json


class NetworkTool:

    def __init__(self):
        self.session_folder = 'uploads/cytoscape/session/'
        self.network_folder = 'uploads/cytoscape/network/'
        self.session_name = None

    def create_session(self):
        self.session_name = uuid.uuid4().hex
        py4.save_session(self.session_folder + self.session_name)
        return self.session_name

    def get_session(self):
        session_name = py4.commands.cyrest_get('session/name')
        return os.path.basename(session_name['name'])

    def delete_session(self):
        py4.session.close_session(False)

    def read_excel(self, input_excel):
        results = pd.read_excel(input_excel)
        results = results.rename(columns={'gene1': 'source', 'gene2': 'target'})
        return results

    def create_network(self, input, network_name):
        network_suid = py4.networks.create_network_from_data_frames(
            edges=input,
            title=network_name,
            collection=network_name + '_collection'
        )
        return network_suid

    def analyze_network(self):
        analyze = py4.commands.commands_post('analyzer/analyze')
        return analyze

    def run_mcode(self):
        mcode = py4.commands.commands_post(
            'mcode cluster degreeCutoff=2 fluff=false fluffNodeDensityCutoff=0.1 haircut=true includeLoops=false kCore=2 maxDepthFromStart=100 network=current nodeScoreCutoff=0.2 scope=NETWORK')
        sleep(3)
        return mcode

    def get_clusters(self, mcode, min_nodes):

        if mcode is not None:

            limited_clusters = [i for i in range(len(mcode['clusters'])) if len(mcode['clusters'][i]['nodes']) >= min_nodes]
            clusters = []
            for i in range(len(limited_clusters)):
                view_id = py4.commands.commands_post('mcode view id=1 rank=' + str(i + 1))
                hash = uuid.uuid4().hex

                data = {
                    "id": i,
                    "hash": hash,
                    "node": py4.networks.get_node_count(),
                    "edge": py4.networks.get_edge_count(),
                    "score": mcode['clusters'][i]['score'],
                    "table": py4.tables.get_table_columns() \
                        .drop(columns=['id', 'name', 'selected', 'MCODE::Clusters (1)', 'SUID']) \
                        .rename(columns={'shared name': 'gene', 'MCODE::Node Status (1)': 'node_status', 'MCODE::Score (1)': 'mcode_score'}) \
                        .sort_values(by=['mcode_score'], ascending=False) \
                        .reset_index(drop=True) \
                        .to_dict()
                }

                clusters.append(data)
                py4.export_image(self.network_folder + str(hash))

            return json.dumps(clusters), None  # None means no error

        else:
            return "", "no clusters found."

    def set_style(self, number):
        styles = ['Marquee', 'Universe', 'Directed', 'DisGeNETstyleV2', 'default', 'Minimal', 'Sample3', 'Ripple', 'Sample1', 'Big Labels', 'default black', 'Sample2', 'Gradient1',
                  'Nested Network Style', 'Solid', 'Curved']
        return py4.set_visual_style(styles[number])
