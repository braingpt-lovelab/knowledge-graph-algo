# An example generating possible outcomes of experiments using a knowledge graph approach

## Knowledge graph approach overview
The current approach relies on prompting strong LLMs (e.g., GPT-4o) for deriving, manipulating, and generating possible knowledge graphs of given experiments. This approach follows the key steps below. Each step, except Step 4, involves prompting LLMs to perform some tasks (see `prompts/` for more details). Knowledge graph permutation is done outside LLMs using a deterministic function.

* Step 1 - Initial Knowledge Graph Creation: extracts a structured knowledge graph from the original paper text using `KnowledgeGraphCreator.create_initial_kg`.
* Step 2 - Knowledge Graph to Text: converts the original knowledge graph of an experiment into descriptive text via `KnowledgeGraphCreator.convert_kg_to_text_single_experiment`.
* Step 3 - Semantic Group Identification: clusters related nodes in the knowledge graph into semantic groups with `KnowledgeGraphCreator.identify_semantic_groups`.
* Step 4 - Knowledge Graph Permutations: generates alternative knowledge graph structures using `graph.permute_knowledge_graph.create_permutations`.
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

### Usage example:
Run knowledge graph possible results generation using default configuration on an example paper:
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

This is a very rudimentary approach of keeping track of prompt versions. For now, prompts are versioned in `prompts/create_sys_prompts.py` or `prompts/create_user_prompts.py`

### Outputs:
Run the above example will generate a json file for each paper (see `outputs/` for a concrete example). Key fields of the outputs are as follows.
| **Key**                              | **Type**         | **Description**                                                                                                                                     | **Example**                                                                                                                                                 | **Unpacked Nested Keys**                                                                                                             |
|--------------------------------------|------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| `methods`                            | String           | Description of the experiment, its purpose, and the methods used to collect and analyze data.                                                       | "The first experiment involved participants designing a robot by selecting attributes..."                                                                   | None                                                                                                                               |
| `knowledge_graph`                    | Object           | Represents the knowledge graph for `experiment_1`, detailing nodes (entities) and edges (relationships).                                             | See nested structure.                                                                                                                                       | `experiment_1.nodes`: List of entities with `id` and `label`. `experiment_1.edges`: Relationships with `source`, `target`, and `relation`.                            |
| `results`                            | Object           | Contains a summary of the findings for `experiment_1`.                                                                                              | "The unique pattern was ranked highest..."                                                                                                                  | None                                                                                                                               |
| `semantic_groups`                    | Object           | Groups nodes from the knowledge graph into semantic categories for `experiment_1`.                                                                   | "Human Elements", "Design Elements", "Pattern Categories", "Outcome Metrics".                                                                               | Nested categories like `Human Elements`, `Design Elements`, and `Outcome Metrics`, each listing nodes with `id`, `label`, and `level`.                                 |
| `knowledge_graph_permutations`       | Object           | Alternative configurations of the knowledge graph nodes and edges for `experiment_1`.                                                               | See nested structure for multiple permutations.                                                                                                             | Each permutation (e.g., `"2"`, `"3"`) lists `nodes` (entities) and `edges` (relationships). Nodes and edges follow the same structure as `knowledge_graph`.          |
| `node_swaps_tracker`                 | Object           | Tracks the changes in node categories across permutations for `experiment_1`.                                                                        | See nested structure for detailed swaps in categories like "Chosen Unique Pattern" and "Shared Pattern".                                                    | Tracks swaps in `Pattern Categories` such as `Chosen Unique Pattern` ↔ `Shared Pattern` for each permutation (e.g., `"2"`, `"3"`).                                    |
| `triple_deviation_pct`               | Object           | Deviation percentages for node configurations in different permutations of `experiment_1`.                                                           | `{ "2": 0.25, "3": 0.25, "4": 0.375, "5": 0.375, "6": 0.25 }`                                                                                               | Maps permutation IDs (`"2"`, `"3"`, etc.) to their deviation percentages.                                                                                                |
| `results_permutations`               | Object           | Summarized results of different knowledge graph permutations for `experiment_1`.                                                                     | "The unique pattern received the highest preference ranking..."                                                                                             | Maps permutation IDs (`"2"`, `"3"`, etc.) to textual summaries of results.                                                                                              |
| `num_graph_permutations`             | Object           | Number of permutations generated for `experiment_1` and overall total.                                                                               | `{ "experiment_1": 5, "total": 5 }`                                                                                                                         | `experiment_1`: Number of permutations for this experiment. `total`: Total permutations across all experiments.                                                        |
| `token_cost`                         | Object           | Cost metrics related to computational processing of methods, knowledge graph, and permutations.                                                      | `{ "sum_met": 0.0487375, "res_to_kg": 0.0508325, "total": 0.113905 }`                                                                                       | Tracks cost components such as `sum_met`, `res_to_kg`, and total costs.                                                                                                 |

