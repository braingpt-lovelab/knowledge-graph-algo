import json
import copy
from itertools import permutations, combinations, chain, product


def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)


def get_swappable_nodes(semantic_groups):
    """
    Args:
        semantic_groups: dict (key: group_name, value: list of nodes)
            e.g., 
            {
                "group_name_1": [
                    {
                        "id": 1,
                        "label": "aaa",
                        "level": 1
                    },
                    {
                        "id": 2,
                        "label": "bbb",
                        "level": 2
                    },
                    {
                        "id": 3,
                        "label": "ccc",
                        "level": 2
                    }
                ],
                "group_name_2": [
                    {
                        "id": 4,
                        "label": "ddd",
                        "level": 2
                    },
                    {
                        "id": 5,
                        "label": "eee",
                        "level": 2
                    }
                ]
            }
    
    Returns:
        swappable_nodes: dict (key: group_name, value: tuple of node ids)
            e.g., 
            {
                "group_name_1": (2, 3),
                "group_name_2": (4, 5)
            }
    """
    swappable_nodes = {}
    for group_name, group in semantic_groups.items():
        max_level = max(node['level'] for node in group)
        swappable_nodes[group_name] = tuple([node['id'] for node in group if node['level'] == max_level])
    return swappable_nodes


def apply_permutation(graph, old_order, new_order):
    new_graph = copy.deepcopy(graph)
    id_mapping = {}
    for old, new in zip(old_order, new_order):
        id_mapping[old] = new
    
    for node in new_graph['nodes']:
        if node['id'] in id_mapping:
            node['id'] = id_mapping[node['id']]
    return new_graph


def get_graph_triples(graph):
    id_to_label = {node['id']: node['label'] for node in graph['nodes']}

    source_relation_target = []
    for edge in graph["edges"]:
        source_id = edge["source"]
        target_id = edge["target"]
        relation = edge["relation"]
        source_relation_target.append((id_to_label[source_id], relation, id_to_label[target_id]))
    
    # Sort triples to ensure order doesn't affect comparison
    return sorted(source_relation_target)


def is_unique_permutation(new_graph, existing_graphs):
    new_triples = get_graph_triples(new_graph)
    for i, existing_graph in enumerate(existing_graphs):
        existing_triples = get_graph_triples(existing_graph)
        # print(f"new_triples: {new_triples}")
        # print(f"existing_triple {i}: {existing_triples}")
        if new_triples == existing_triples:
            # print(f"Found duplicate graph at index {i}")
            return False
        # print(f"Current graph is different from existing graph {i}")
    return True


def graph_deviation_from_original(new_graph, original_graph):
    new_graph_triples = get_graph_triples(new_graph)
    original_graph_triples = get_graph_triples(original_graph)
    original_graph_triples_dict = {}
    for triple in original_graph_triples:
        original_graph_triples_dict[triple] = original_graph_triples_dict.get(triple, 0) + 1
    
    deviation_count = 0
    total_triples = len(new_graph_triples)
    assert total_triples == len(original_graph_triples)
    for triple in new_graph_triples:
        if triple not in original_graph_triples_dict:
            deviation_count += 1
        else:
            continue
    
    deviation_pct = deviation_count / total_triples
    return deviation_pct
    

def create_permutations(knowledge_graph, semantic_groups):
    """
    Basic idea:

    For each experiment's kg:
        1. Get the swappable nodes for each semantic group
        2. Generate all possible combinations of valid semantic groups

        for each combo of groups:  # leads to multiple new graphs
            3. Get all possible permutations of swaps for each group
            4. Generate all combinations of swaps across groups
            
            for each swap permutation:  # leads to a new graph (1 permutation from each group)
                5. Swap the nodes in the graph
    """
    num_experiments = len(knowledge_graph)
    knowledge_graph_permutations = {}
    node_swaps_tracker = {}
    triple_deviation_pct = {}
    
    for experiment_i in range(1, num_experiments+1):
        knowledge_graph_i = knowledge_graph[f'experiment_{experiment_i}']
        semantic_group_i = semantic_groups[f'experiment_{experiment_i}']
    
        swappable_nodes = get_swappable_nodes(semantic_group_i)
        permutations_i = {1: knowledge_graph_i}  # Include original graph
        total_permutation_count_i = len(permutations_i)
        unique_permutation_count_i = len(permutations_i)
        node_swaps_tracker_i = {}   # For each permutation, track pairs of nodes (labels) swapped for post-analysis.
        triple_deviation_pct_i = {} # For each permutation, track % of deviating triples to original
        
        # Filter out groups with only one node
        valid_groups = {group: nodes for group, nodes in swappable_nodes.items() if len(nodes) > 1}
        
        # Generate all possible combinations of semantic groups
        group_combinations = list(chain.from_iterable(
            combinations(valid_groups.keys(), r) 
            for r in range(1, len(valid_groups) + 1)
        ))
        
        print(f"Num. unique groups: {len(valid_groups)}")
        print(f"Num. group combinations: {len(group_combinations)}")
        
        for group_combo in group_combinations:
            print(f"\nProcessing group combination: {group_combo}")  
            # e.g., ('group_name_1', 'group_name_2')
            
            # Generate all possible swaps for each group
            # List of lists, where each sublist contains all possible swaps for a group
            group_swaps = [] 
            for group_name in group_combo:
                nodes = valid_groups[group_name]
                group_swaps.append(list(permutations(nodes)))
            # e.g., group_swaps = [[(2, 3), (3, 2)], [(4, 5), (5, 4)]]

            # Generate all combinations of permutations across groups
            print(f" Group swaps: {group_swaps}")
            for perm_combo in product(*group_swaps):
                print(f"  Applying perm_combo: {perm_combo}")
                # e.g., ((2, 3), (4, 5)); (tuple of tuples)

                # Each perm_combo leads to a ***new graph***
                new_graph = copy.deepcopy(knowledge_graph_i)
                for group_name, perm in zip(group_combo, perm_combo):
                    old_order = valid_groups[group_name]
                    new_graph = apply_permutation(new_graph, old_order, perm)
                    print(f"   group_name: {group_name}")   # e.g., group_name_1; (str)
                    print(f"   old_order: {old_order}")     # e.g., (2, 3); (tuple)
                    print(f"   new_order: {perm}")          # e.g., (3, 2); (tuple)

                # Check if the new graph is unique
                if is_unique_permutation(new_graph, permutations_i.values()):
                    unique_permutation_count_i += 1
                    permutations_i[unique_permutation_count_i] = new_graph
                    
                    permuted_nodes = []
                    for group_name, perm in zip(group_combo, perm_combo):
                        old_order = valid_groups[group_name]
                        group_permutation = []
                        for old_id, new_id in zip(old_order, perm):
                            old_label = [node['label'] for node in knowledge_graph_i['nodes'] if node['id'] == old_id][0]
                            new_label = [node['label'] for node in knowledge_graph_i['nodes'] if node['id'] == new_id][0]
                            group_permutation.append((old_label, new_label))
                        permuted_nodes.append((group_name, group_permutation))
                    
                    # Track the nodes permuted for post-analysis
                    node_swaps_tracker_i[unique_permutation_count_i] = permuted_nodes

                    # Track % of deviating triples to original
                    triple_deviation_pct_i[unique_permutation_count_i] \
                        = graph_deviation_from_original(new_graph, knowledge_graph_i)
                
                total_permutation_count_i += 1

        print(f"Exp. {experiment_i}: Total permutations: {total_permutation_count_i}, Unique permutations: {unique_permutation_count_i}")
        del permutations_i[1]  # Remove original graph
        knowledge_graph_permutations[f'experiment_{experiment_i}'] = permutations_i
        node_swaps_tracker[f'experiment_{experiment_i}'] = node_swaps_tracker_i
        triple_deviation_pct[f'experiment_{experiment_i}'] = triple_deviation_pct_i

    return knowledge_graph_permutations, node_swaps_tracker, triple_deviation_pct