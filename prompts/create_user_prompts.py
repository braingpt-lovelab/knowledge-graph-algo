def summarize_methods(paper_text, v=1):
    if v == 1:
        prompt = f"""
            Now, you are reading a paper, and you want to summarize the methods used in this paper in a few sentences.

            Here is the full paper: {paper_text}

            You should return your answer as a json such as:
            {{
                "methods": your_summary
            }}

            Please summarize the methods:
        """
    elif v == 2:  # For first study/experiment only
        prompt = f"""
            Now, you are reading a paper, and you want to summarize the methods used in the first study/experiment in this paper in a few sentences.

            Here is the full paper: {paper_text}

            You should return your answer as a json such as:
            {{
                "methods": your_summary
            }}

            Please summarize the methods:
        """
    return prompt


def summarize_results_as_sentences(paper_text, v=1):
    if v == 1:
        prompt = f"""
            Now, you are reading a paper, and you want to summarize the results in this paper in a few sentences.

            Be careful about the granularity of the results, only include the findings presented by the paper.

            Often a paper presents results from multiple experiments, if that is the case, make sure you summarize 
            the results by experiment.

            Here is the full paper: {paper_text}

            You should return your answer as a json such as:
            {{
                "results": {{
                    "experiment_1": your summary in a few sentences,
                    "experiment_2": your summary in a few sentences,
                    ...
                }}
            }}

            Please summarize the results:
        """
    return prompt


def create_alternative_results_as_sentences_single_experiment(paper_text, original_results, v=2):
    if v == 2:
        prompt = f"""
            Now, you are reading a paper, 
            
            As a critical thinker, you are always curious about whether different results could have been obtained
            following the same methods and experiments.

            You should come up with alternative patterns of results significantly different, even contradictory to the
            original results presented in the paper. The alternative results do not have to be the exact opposite
            of the original results, but they should be different enough. However the alternative results should always 
            be plausible and consistent with the methods and experiments in the paper.

            Here is the full paper: {paper_text}

            Here are the original results as your reference for style: {original_results}. Write the alternative results
            in the same way as if they were the original results. Avoid using terms such as "unexpectedly", "surprisingly",
            "contrary to", etc. State them as if they were the actual results.

            You should return your answer as a json such as:
            {{
                "alternative_results": your summary in a few sentences
            }}
        """
    return prompt


class KnowledgeGraphCreator(object):
    """
    A series of prompts to create a knowledge graph from a paper
    in order to perform permutation to get sensible alternative results
    within the search space of the paper.

    step1: 
    `create_initial_kg` - create a knowledge graph from the full paper

    step2:
    `identify_semantic_groups` - group nodes into semantic groups/categories and note the level of granularity of each node
    """
    def __init__(self, paper_text):
        self.paper_text = paper_text

    def create_initial_kg(self, v):
        if v == 1:
            prompt = f"""
                Now, you are reading a paper, as follows: {self.paper_text}.
                
                Now you want to construct a knowledge graph of the results. Make sure you always label every edge and node. 
                It is important to correctly represent the relationships between the nodes.

                Organize the knowledge graph by experiment numbers.


                You should return your answer as a json such as:
                {{
                    "knowledge_graph": {{
                        "experiment_1": {{
                            "nodes": [{{"id": 1, "label": "node1"}}, {{"id": 2, "label": "node2"}}, ...],
                            "edges": [{{"source": 1, "target": 2, "relation": "edge1"}}, {{"source": 2, "target": 3, "relation": "edge2"}}, ...]
                        }},
                        "experiment_2": {{
                            "nodes": [{{"id": 1, "label": "node1"}}, {{"id": 2, "label": "node2"}}, ...],
                            "edges": [{{"source": 1, "target": 2, "relation": "edge1"}}, {{"source": 2, "target": 3, "relation": "edge2"}}, ...]
                        }},
                        ...
                    }}
                }}

                Please create the knowledge graph:
            """
        elif v == 2:
            prompt = f"""
                Now, you are reading a paper, as follows: {self.paper_text}.
                
                Now you want to construct a knowledge graph of the results of the first study/experiment only. 
                Make sure you always label every edge and node. 
                It is important to correctly represent the relationships between the nodes.

                You should return your answer as a json such as below, respect the keys.
                {{
                    "knowledge_graph": {{
                        "experiment_1": {{
                            "nodes": [{{"id": 1, "label": "node1"}}, {{"id": 2, "label": "node2"}}, ...],
                            "edges": [{{"source": 1, "target": 2, "relation": "edge1"}}, {{"source": 2, "target": 3, "relation": "edge2"}}, ...]
                        }},
                    }}
                }}

                Please create the knowledge graph:
            """
        return prompt

    def identify_semantic_groups(self, initial_kg, v):
        if v == 1:
            prompt = f"""
                Now, you are reading a paper, and you have constructed a knowledge graph for the results of this paper 
                as follows: {initial_kg}.

                Now focus on all the nodes and group them into semantic groups/categories. 
                Notice, nodes belonging to the same group might have hierarchical relationships due to difference in 
                granularity or abstraction level. When grouping, make sure to note the level of granularity of each node.
                The top level is 1 and the level increases as the granularity decreases.

                You should return your answer as a json such as:
                {{
                    "semantic_groups": {{
                        "experiment_1": {{
                            "group_name_1": [{{"id": 1, "label": "node1", "level": "granularity_level"}}, {{"id": 2, "label": "node2", "level": "granularity_level"}}, ...],
                            "group_name_2": [{{"id": 1, "label": "node1", "level": "granularity_level"}}, {{"id": 2, "label": "node2", "level": "granularity_level"}}, ...],
                        }},
                    "experiment_2": {{
                            "group_name_1": [{{"id": 1, "label": "node1", "level": "granularity_level"}}, {{"id": 2, "label": "node2", "level": "granularity_level"}}, ...],
                            "group_name_2": [{{"id": 1, "label": "node1", "level": "granularity_level"}}, {{"id": 2, "label": "node2", "level": "granularity_level"}}, ...],
                        }},
                        ...
                    }}  
                }}
            """
        elif v == 2:
            prompt = f"""
                Now, you are reading a paper, and you have constructed a knowledge graph for the results of the first study/experiment
                as follows: {initial_kg}.

                Now focus on all the nodes and group them into semantic groups/categories. 
                Notice, nodes belonging to the same group might have hierarchical relationships due to difference in 
                granularity or abstraction level. When grouping, make sure to note the level of granularity of each node.
                The top level is 1 and the level increases as the granularity decreases.

                You should return your answer as a json such as:
                {{
                    "semantic_groups": {{
                        "experiment_1": {{
                            "group_name_1": [{{"id": 1, "label": "node1", "level": "granularity_level"}}, {{"id": 2, "label": "node2", "level": "granularity_level"}}, ...],
                            "group_name_2": [{{"id": 1, "label": "node1", "level": "granularity_level"}}, {{"id": 2, "label": "node2", "level": "granularity_level"}}, ...],
                        }}
                    }}  
                }}
            """
        return prompt
        
    def convert_kg_to_text_single_experiment(self, kg, v, orig_results_as_example=None):
        if v == 1:
            prompt = f"""
                From this knowledge graph, write a brief paragraph describing the results of the experiment.
                Write the paragraph in standard prose, You are describing the results of a scientific
                paper to others. Do not refer to the knowledge graph in your answer.
                Also only describe the results. Do not provide theoretical interpretations of 
                the results.

                Here is the knowledge graph: {kg}

                You should return your answer as a json such as:
                {{
                    "results": your summary in a few sentences
                }}

                Please convert the knowledge graph back to sentences:
            """
        elif v == 2:
            prompt = f"""
                From this knowledge graph, write a brief paragraph describing the results of main study/experiment.
                Write the paragraph in standard prose, You are describing the results of a scientific
                paper to others. Do not refer to the knowledge graph in your answer.
                Also only describe the results. Do not provide theoretical interpretations of 
                the results.

                Here is the knowledge graph: {kg}

                You should return your answer as a json such as:
                {{
                    "results": your summary in a few sentences
                }}

                Please convert the knowledge graph back to sentences:
            """
        elif v == 3:
            if not orig_results_as_example:  # Do not use example; this is when converting orig kg to text
                prompt = f"""
                    From this knowledge graph, write a brief paragraph describing the results of main study/experiment.
                    Write the paragraph in standard prose, You are describing the results of a scientific
                    paper to others. Do not refer to the knowledge graph in your answer.
                    Also only describe the results. Do not provide theoretical interpretations of 
                    the results.

                    Here is the knowledge graph: {kg}

                    You should return your answer as a json such as:
                    {{
                        "results": your summary in a few sentences
                    }}

                    Please convert the knowledge graph back to sentences:
                """
            else:   # Use example; this is when converting alternative kg to text
                prompt = f"""
                    From this knowledge graph, write a brief paragraph describing the results of main study/experiment.
                    Write the paragraph in standard prose, You are describing the results of a scientific
                    paper to others. Do not refer to the knowledge graph in your answer.
                    Also only describe the results. Do not provide theoretical interpretations of 
                    the results.

                    Here is the knowledge graph: {kg}

                    Your paragraph should follow a similar writing style but not its content in this example: {orig_results_as_example}.

                    You should return your answer as a json such as:
                    {{
                        "results": your summary in a few sentences
                    }}

                    Please convert the knowledge graph back to sentences:
                """
        return prompt