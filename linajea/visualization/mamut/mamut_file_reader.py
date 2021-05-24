from .mamut_reader import MamutReader
from linajea import parse_tracks_file
import networkx as nx
import logging

logger = logging.getLogger(__name__)


class MamutFileReader(MamutReader):
    def read_data(self, data):
        filename = data['filename']
        locations, track_info = parse_tracks_file(filename)
        graph = nx.DiGraph()
        for loc, info in zip(locations, track_info):
            node_id = info[0]
            parent_id = info[1]
            graph.add_node(node_id, position=loc.astype(int))
            if parent_id != -1:
                graph.add_edge(node_id, parent_id)

        logger.info("Graph has %d nodes and %d edges"
                    % (len(graph.nodes), len(graph.edges)))
        track_graphs = [graph.subgraph(g).copy()
                        for g in nx.weakly_connected_components(graph)]
        logger.info("Found {} tracks".format(len(track_graphs)))
        track_id = 0
        tracks = []
        cells = []
        for track in track_graphs:
            if not track.nodes:
                logger.info("track has no nodes. skipping")
                continue
            if not track.edges:
                logger.info("track has no edges. skipping")
                continue
            for node_id, node in track.nodes(data=True):
                position = node['position']
                score = node['score'] if 'score' in node else 0
                cells.append(self.create_cell(position, score, node_id))
            track_edges = []
            for u, v, edge in track.edges(data=True):
                score = edge['score'] if 'score' in edge else 0
                track_edges.append(self.create_edge(u,
                                                    v,
                                                    score=score))
            cell_frames = [cell['position'][0]
                           for _, cell in track.nodes(data=True)]
            start_time = min(cell_frames)
            end_time = max(cell_frames)

            num_cells = len(track.nodes)
            tracks.append(self.create_track(start_time,
                                            end_time,
                                            num_cells,
                                            track_id,
                                            track_edges))
            track_id += 1
        return cells, tracks
