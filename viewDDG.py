import json
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict, deque
def compute_layer_map(edges, nodes):
    in_deg = defaultdict(int)
    graph = defaultdict(list)
    for src, dst in edges:
        graph[src].append(dst)
        in_deg[dst] += 1

    layer = {}
    queue = deque([n["id"] for n in nodes if in_deg[n["id"]] == 0])
    for nid in queue:
        layer[nid] = 0

    while queue:
        u = queue.popleft()
        for v in graph[u]:
            in_deg[v] -= 1
            if in_deg[v] == 0:
                layer[v] = layer[u] + 1
                queue.append(v)
    return layer

def visualize_ddg(json_path, save_path=None):
    with open(json_path, 'r') as f:
        ddg = json.load(f)

    G = nx.DiGraph()
    pos = {}
    labels = {}

    # 添加节点
    for node in ddg["nodes"]:
        nid = node["id"]
        x, y = node["x"], node["y"]
        G.add_node(nid)
        pos[nid] = (x, -y)  # 反转 y 轴使其视觉与图像方向一致
        labels[nid] = str(nid)

    # 添加边
    for src, dst in ddg["edges"]:
        G.add_edge(src, dst)

    # 绘图
    plt.figure(figsize=(14, 12))
    layer_map = compute_layer_map(ddg["edges"], ddg["nodes"])
    node_colors = [layer_map.get(n["id"], 0) for n in ddg["nodes"]]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, cmap=plt.cm.viridis, node_size=30)
    # nx.draw_networkx_labels(G, pos, labels=labels, font_size=5)

    plt.title(f"DDG Visualization: {json_path}", fontsize=12)
    plt.axis("off")
    if save_path:
        plt.savefig(save_path, dpi=300)
    plt.show()

# ✅ 示例调用
#
if __name__ == "__main__":
    visualize_ddg(r"D:\Users\13321\PycharmProjects\Tar5Stego\results\0.3_8_ddg\aspensegment000\aspensegment000\frame_1_ddg.json")