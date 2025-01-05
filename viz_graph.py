import os
import pygame
import networkx as nx
import math
import json
import argparse
import colorsys

def load_json_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def create_knowledge_graph(data):
    G = nx.DiGraph()
    
    # Create a mapping of node ids to their semantic groups and levels
    node_to_group_n_level = {}
    for group, nodes in data['semantic_groups']['experiment_1'].items():
        for node in nodes:
            node_to_group_n_level[node['id']] = f"{group},{node['level']}"
    
    # Add nodes with labels including semantic group
    for node in data['knowledge_graph']['experiment_1']['nodes']:
        group_n_level = node_to_group_n_level.get(node['id'], 'Unknown')
        label = f"{node['label']} ({group_n_level})"
        G.add_node(node['id'], label=label)
    
    # Add edges
    for edge in data['knowledge_graph']['experiment_1']['edges']:
        G.add_edge(edge['source'], edge['target'], relation=edge['relation'])
    
    return G

def generate_colors(n):
    HSV_tuples = [(x * 1.0 / n, 0.5, 0.5) for x in range(n)]
    return [colorsys.hsv_to_rgb(*x) for x in HSV_tuples]

def get_node_colors(data):
    semantic_groups = data['semantic_groups']['experiment_1']
    group_names = list(semantic_groups.keys())
    colors = generate_colors(len(group_names))
    
    color_map = {}
    for i, group in enumerate(group_names):
        for node in semantic_groups[group]:
            color_map[node['id']] = colors[i]
    
    return color_map

def plot_interactive_graph(G, data):
    pygame.init()

    width, height = 1200, 900
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Interactive Knowledge Graph")

    pos = nx.spring_layout(G, k=0.5, iterations=50)

    for node in pos:
        x = (pos[node][0] + 1) / 2 * (width * 0.8) + (width * 0.1)
        y = (pos[node][1] + 1) / 2 * (height * 0.8) + (height * 0.1)
        pos[node] = (int(x), int(y))

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    
    node_font = pygame.font.Font(None, 24)
    edge_font = pygame.font.Font(None, 18)
    
    color_map = get_node_colors(data)

    def wrap_text(text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = words[0]
        for word in words[1:]:
            if font.size(current_line + ' ' + word)[0] <= max_width:
                current_line += ' ' + word
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
        return lines

    def draw_arrow(surface, start, end, color, width=1, arrow_size=20):
        pygame.draw.line(surface, color, start, end, width)
        angle = math.atan2(start[1] - end[1], start[0] - end[0])
        arrow_end1 = (end[0] + arrow_size * math.cos(angle - math.pi/6),
                      end[1] + arrow_size * math.sin(angle - math.pi/6))
        arrow_end2 = (end[0] + arrow_size * math.cos(angle + math.pi/6),
                      end[1] + arrow_size * math.sin(angle + math.pi/6))
        pygame.draw.polygon(surface, color, [end, arrow_end1, arrow_end2])

    def draw_graph(offset_x, offset_y):
        screen.fill(WHITE)
        
        for edge in G.edges():
            start = (pos[edge[0]][0] + offset_x, pos[edge[0]][1] + offset_y)
            end = (pos[edge[1]][0] + offset_x, pos[edge[1]][1] + offset_y)
            
            # Calculate the position for the arrow (80% along the edge)
            arrow_pos = (0.8 * end[0] + 0.2 * start[0], 0.8 * end[1] + 0.2 * start[1])
            draw_arrow(screen, start, arrow_pos, BLACK, width=2, arrow_size=15)
            
            midpoint = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
            relation = G.edges[edge]['relation']
            text = edge_font.render(relation, True, BLACK)
            screen.blit(text, (midpoint[0] - text.get_width() // 2, midpoint[1] - 10))
        
        for node in G.nodes():
            node_pos = (pos[node][0] + offset_x, pos[node][1] + offset_y)
            color = tuple(int(x * 255) for x in color_map.get(node, (0.5, 0.5, 0.5)))
            pygame.draw.circle(screen, color, node_pos, 30)
            lines = wrap_text(G.nodes[node]['label'], node_font, 200)
            for i, line in enumerate(lines):
                text = node_font.render(line, True, BLACK)
                screen.blit(text, (node_pos[0] - text.get_width() // 2, node_pos[1] - 50 + i*25))

        pygame.display.flip()

    dragging_node = False
    dragging_view = False
    selected_node = None
    offset_x, offset_y = 0, 0
    last_pos = (0, 0)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    for node in G.nodes():
                        node_pos = (pos[node][0] + offset_x, pos[node][1] + offset_y)
                        distance = math.hypot(event.pos[0] - node_pos[0], event.pos[1] - node_pos[1])
                        if distance < 30:
                            dragging_node = True
                            selected_node = node
                            break
                    else:
                        dragging_view = True
                        last_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    dragging_node = False
                    dragging_view = False
                    selected_node = None
            elif event.type == pygame.MOUSEMOTION:
                if dragging_node:
                    pos[selected_node] = (event.pos[0] - offset_x, event.pos[1] - offset_y)
                elif dragging_view:
                    dx, dy = event.pos[0] - last_pos[0], event.pos[1] - last_pos[1]
                    offset_x += dx
                    offset_y += dy
                    last_pos = event.pos

        draw_graph(offset_x, offset_y)

    pygame.quit()

def main():
    parser = argparse.ArgumentParser(description="Interactive Knowledge Graph Visualization")
    parser.add_argument("--json_file", "-f", help="Path to the JSON file containing graph data")
    args = parser.parse_args()

    summary_dir = "outputs/fullpaper_sum_met2_kg_init2_kg_sema2_kg_txt3"
    json_fpath = os.path.join(summary_dir, f"{args.json_file}.json")
    data = load_json_data(json_fpath)
    G = create_knowledge_graph(data)
    plot_interactive_graph(G, data)

if __name__ == "__main__":
    main()