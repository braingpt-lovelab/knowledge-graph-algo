# An example generating possible outcomes of experiments using a knowledge graph approach

## Overview
The current approach relies on prompting strong LLMs (e.g., GPT-4o) for deriving, manipulating, and generating possible knowledge graphs of given experiments. This approach follows the key steps below. Each step, except Step 4, involves prompting LLMs to perform some tasks (see `prompts/` for more details). Knowledge graph permutation is done without a LLM but using a deterministic function (see [Details](#details)).

* Step 1 - Initial Knowledge Graph Creation: extracts a structured knowledge graph from the original paper text using [`create_initial_kg`](prompts/create_user_prompts.py#L99).
* Step 2 - Knowledge Graph to Text: converts the original knowledge graph of an experiment into descriptive text via [`convert_kg_to_text_single_experiment`](prompts/create_user_prompts.py#L197).
* Step 3 - Semantic Group Identification: clusters related nodes in the knowledge graph into semantic groups with [`identify_semantic_groups`](prompts/create_user_prompts.py#L149).
* Step 4 - Knowledge Graph Permutations: generates alternative knowledge graph structures using [`create_permutations`](graphs/permute_knowledge_graph.py#L127)
* Step 5 - Permuted Knowledge Graph to Text: converts sampled permutations into alternative descriptive texts, leveraging the original results for consistency.

## Quickstart

### Work with the repo locally:
```
git clone git@github.com:don-tpanic/knowledge-graph-algo.git
```

### Install dependencies:
```
conda env create -f environment.yml
```

### Setup OpenAI API key
Create `.env` file in root directory of this repo, and insert the following per line
<br>`AZURE_OPENAI_API_KEY=<API_KEY>`<br>
`AZURE_OPENAI_ENDPOINT=<ENDPOINT>`

### Usage example:
1. Save a paper (pdf) in `data/pdf_articles/<paper_name>.pdf`
2. Run `python utils/pdf2txt.py` which will convert all pdf files to txt format, saved in `data/txt_articles/<paper_name>.txt`
3. Run the graph generation script using default configuration on existing papers saved in the above directory.
```
python run_graph.py --sum_met 2 \
                    --kg_init 2 \
                    --kg_sema 2 \
                    --kg_txt 3
```
Explanation of parameters:
* `--sum_met`: the prompt version of summarizing methods of the paper.
* `--kg_init`: the prompt version of creating initial knowledge graph from original results.
* `--kg_sema`: the prompt version of creating semantic groups out of the original knowledge graph.
* `--kg_txt`: the prompt version of converting knowledge graph to natural language.

NOTE: This is a very rudimentary approach of keeping track of prompt versions. For now, prompts are versioned in `prompts/create_sys_prompts.py` or `prompts/create_user_prompts.py`

### Outputs:
Run the above example will generate a json file for each paper (see `outputs/` for a concrete example). Key fields of the outputs are as follows.
| **Key**                      | **Description**                                                                                              | **Unpacked Nested Keys**                                                                                                                                                                | **Key Explanations**                                                                                                         |
|------------------------------|--------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| `methods`                   | Description of the experiment, its purpose, and the methods used to collect and analyze data.                |                                                                                                                                                                                     |                                                                 |
| `knowledge_graph`           | Represents the knowledge graph for `experiment_1`, detailing nodes (entities) and edges (relationships).     | `knowledge_graph['experiment_1']['nodes'] = [{"id": <ID>, "label": <LABEL>}, ...]`<br>`knowledge_graph['experiment_1']['edges'] = [{"source": <SOURCE_ID>, "target": <TARGET_ID>, "relation": <RELATION>}, ...]` | `<ID>` uniquely identifies a node. `<LABEL>` describes the node. `<SOURCE_ID>` and `<TARGET_ID>` represent the edge's start and end points.                        |
| `results`                   | Contains a summary of the findings for `experiment_1`.                                                      | `results['experiment_1'] = <RESULT_STRING>`                                                                                                     |                                                                   |
| `semantic_groups`           | Groups nodes from the knowledge graph into semantic categories for `experiment_1`.                          | `semantic_groups['experiment_1']['<GROUP>'] = [{"id": <ID>, "label": <LABEL>, "level": <LEVEL>}, ...]`                                            | `<GROUP>` specifies a semantic group identified by a LLM among nodes. `<LEVEL>` is the abstraction level of a node within a group (lower values = higher abstraction).                                                           |
| `knowledge_graph_permutations` | Alternative configurations of the knowledge graph nodes and edges for `experiment_1`.                        | `knowledge_graph_permutations['experiment_1']['<PERMUTATION_ID>']['nodes'] = [{"id": <ID>, "label": <LABEL>}, ...]`<br>`knowledge_graph_permutations['experiment_1']['<PERMUTATION_ID>']['edges'] = [{"source": <SOURCE_ID>, "target": <TARGET_ID>, "relation": <RELATION>}, ...]` | `<PERMUTATION_ID>` starts from `2` and represents an alternative knowledge graph configuration. Graphs follow the same data structure as the original.                                                                 |
| `node_swaps_tracker`        | Tracks the changes in node categories across permutations for `experiment_1`.                               | `node_swaps_tracker['experiment_1']['<PERMUTATION_ID>'] = [[<GROUP>, [[<ORIGINAL_LABEL>, <NEW_LABEL>], ...]]]`                                   |                                                 |
| `triple_deviation_pct`      | Deviation percentages for node configurations in different permutations of `experiment_1`.                  | `triple_deviation_pct['experiment_1']['<PERMUTATION_ID>'] = <DEVIATION_PERCENTAGE>`                                                             |               |
| `results_permutations`      | Summarized results of different knowledge graph permutations for `experiment_1`.                            | `results_permutations['experiment_1']['<PERMUTATION_ID>'] = <RESULT_STRING>`                                                                    |                                                       |
| `num_graph_permutations`    | Number of permutations generated for `experiment_1` and overall total.                                      | `num_graph_permutations['experiment_1'] = <NUM>`<br>`num_graph_permutations['total'] = <TOTAL_NUM>`                                               |                                       |
| `token_cost`                | Cost metrics related to computational processing of methods, knowledge graph, and permutations.             | `token_cost['sum_met'] = <VALUE>`<br>`token_cost['res_to_kg'] = <VALUE>`<br>`token_cost['kg_to_text'] = <VALUE>`<br>`token_cost['total'] = <TOTAL_VALUE>` |                               |

## Details
### Knowledge graph permutation
The graph permutation logic is implemented in `graphs/permute_knowledge_graph.py` and done by function `create_permutations`
