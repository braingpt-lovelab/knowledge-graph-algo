# An example repo generating possible outcomes of experiments using a knowledge graph approach

## Knowledge graph approach overview
This section highlights the key steps for deriving, manipulating, and generating textual interpretations of knowledge graphs:

### Initial Knowledge Graph Creation:
Extracts a structured knowledge graph from the full paper text using `KnowledgeGraphCreator.create_initial_kg`.

### Knowledge Graph to Text:
Converts the knowledge graph for each experiment into descriptive text via `KnowledgeGraphCreator.convert_kg_to_text_single_experiment`.

### Semantic Group Identification:
Clusters related nodes in the knowledge graph into semantic groups with `KnowledgeGraphCreator.identify_semantic_groups`.

### Knowledge Graph Permutations:
Generates alternative knowledge graph structures using permute_knowledge_graph.create_permutations.

### Permuted Knowledge Graph to Text:
Converts sampled permutations into alternative descriptive texts, leveraging the original results for consistency.