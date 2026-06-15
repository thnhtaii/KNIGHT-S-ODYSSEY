# def extract_platform_nodes(spawn_objects):
#     """
#     Trích xuất các node từ spawn_objects, mỗi node đại diện cho một platform.
#     spawn_objects: List các dict chứa thông tin đối tượng từ TMX.
#     Trả về: List các dict {'center': (x, y), 'rect': (x, y, width, height)}.
#     """
#     nodes = []
#     print(f"[Platform Graph] Input spawn_objects: {spawn_objects}")
    
#     for i, obj in enumerate(spawn_objects):
#         print(f"[Platform Graph] Processing object {i}: {obj}")
#         if obj.get("name") == "gnd":
#             x = obj["x"]
#             y = obj["y"]
#             width = obj["width"]
#             height = obj["height"]
#             center_x = x + width / 2
#             center_y = y
#             node = {
#                 "center": (center_x, center_y),
#                 "rect": (x, y, width, height)
#             }
#             nodes.append(node)
#             print(f"[Platform Graph] Added node {len(nodes)-1} at ({center_x}, {center_y}), rect: ({x}, {y}, {width}, {height})")
#         else:
#             print(f"[Platform Graph] Skipped object {i}: name={obj.get('name')}")

#     if not nodes:
#         print("[Platform Graph] ERROR: No 'gnd' objects found in spawn_objects!")
    
#     print(f"[Platform Graph] Total nodes extracted: {len(nodes)}")
#     return nodes

# def build_platform_graph(nodes):
#     """
#     Xây dựng đồ thị platform từ danh sách nodes.
#     nodes: List các dict {'center': (x, y), 'rect': (x, y, width, height)}.
#     Trả về: Dict {node_id: [neighbor_id, ...]}.
#     """
#     if not nodes:
#         print("[Platform Graph] ERROR: No nodes available")
#         return {}

#     graph = {i: [] for i in range(len(nodes))}
    
#     for i in range(len(nodes)):
#         node_i = nodes[i]
#         rect_i = node_i["rect"]
#         center_i = node_i["center"]
        
#         for j in range(len(nodes)):
#             if i == j:
#                 continue
#             node_j = nodes[j]
#             rect_j = node_j["rect"]
#             center_j = node_j["center"]
            
#             # Kiểm tra giao nhau ngang (cùng hoặc gần y)
#             y_diff = abs(rect_i[1] - rect_j[1])
#             x_overlap = (rect_i[0] <= rect_j[0] + rect_j[2] and rect_i[0] + rect_i[2] >= rect_j[0])
            
#             # Kiểm tra khả năng nhảy hoặc rơi
#             can_jump_up = (rect_j[1] < rect_i[1] and y_diff <= 200)  # Nhảy lên (max 200px)
#             can_fall_down = (rect_j[1] > rect_i[1] and y_diff <= 300)  # Rơi xuống (max 300px)
#             x_distance = abs(center_i[0] - center_j[0])
            
#             if (x_overlap and y_diff <= 50) or (x_distance <= 400 and (can_jump_up or can_fall_down)):
#                 graph[i].append(j)
#                 print(f"[Platform Graph] Added edge {i} -> {j}: y_diff={y_diff}, x_distance={x_distance}, "
#                       f"jump_up={can_jump_up}, fall_down={can_fall_down}, x_overlap={x_overlap}")
    
#     print(f"[Platform Graph] Full graph: {graph}")
#     return graph

# def find_nearest_node(x, y, nodes):
#     """
#     Tìm node gần nhất với tọa độ (x, y).
#     nodes: List các dict {'center': (x, y), 'rect': (x, y, width, height)}.
#     Trả về: Index của node gần nhất, hoặc None nếu không có node.
#     """
#     if not nodes:
#         print("[Platform Graph] ERROR: No nodes available for find_nearest_node")
#         return None
    
#     min_dist = float('inf')
#     nearest = None
    
#     for i, node in enumerate(nodes):
#         center_x, center_y = node["center"]
#         dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
#         if dist < min_dist:
#             min_dist = dist
#             nearest = i
#             print(f"[Platform Graph] Node {i} at ({center_x}, {center_y}), dist={dist:.1f}")
    
#     if nearest is not None:
#         print(f"[Platform Graph] Nearest node to ({x}, {y}) is {nearest}, dist={min_dist:.1f}")
#     else:
#         print(f"[Platform Graph] No nearest node found for ({x}, {y})")
    
#     return nearest