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
