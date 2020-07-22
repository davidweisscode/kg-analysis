# kg-analysis
Knowledge Graph and Linked Data uniformity analysis with affiliation networks  

<img src="https://github.com/davidweisscode/kg-analysis/blob/master/bigraph.png" alt="Bipartite graph" width="500px">

---
## Setup
* Install Python development headers  
```
apt install python3.7-dev
```
* Install [Python C++11 bindings](http://pybind11.readthedocs.io/en/stable/)  
```
pip install pybind11
```
* Install project dependencies
```
pip install hdt rdflib networkx numpy scipy pandas tqdm
```  
* Clone this project
```
git clone https://github.com/davidweisscode/kg-analysis.git
```
* Download HDT serialized [datasets, indexfiles](http://fragments.dbpedia.org/hdt/) and [ontologies](http://downloads.dbpedia.org/2016-04/) from [dbpedia.org](https://wiki.dbpedia.org/) and [rdfhdt.org](http://www.rdfhdt.org/datasets/)
```
mkdir kg/ && cd kg/
wget -c http://fragments.dbpedia.org/hdt/dbpedia2016-04en.hdt
wget -c http://fragments.dbpedia.org/hdt/dbpedia2016-04en.hdt.index.v1-1
wget -c http://downloads.dbpedia.org/2016-04/dbpedia_2016-04.owl
```

---

## Getting started
### Configuration
Specify your runs with a custom configuration of classes, data size, and projection approach.
```python
config = {
    "classes": ["Athlete", "Artist"],        # List of DBpedia class names to analyze
    "project_method": "intersect",           # Choose between 'dot', 'hop', 'intersect', or 'nx'
    "kg_source": "kg/dbpedia2016-04en.hdt",  # Relative path to .hdt serialized Knowledge Graph
    "kg_ontology": "kg/dbpedia.owl",         # Relative path to respective Knowledge Graph ontology
    "subject_limit": 0,                      # SPARQL subject limit for each subclass (0 for unlimited)
    "predicate_limit": 0,                    # SPARQL predicate limit for each subject (0 for unlimited)
}
```

### DBpedia classes
Analyze classes and its subclasses from the DBpedia [class mappings](http://mappings.dbpedia.org/server/ontology/classes/).

### Main Steps
Run the following four scripts in sequence together with your run configuration  

 1. Building  
    - Query your dataset and build a bipartite Knowledge Graph for each `Superclass` specified in your config file  
    - Run `python3 build_graph.py run_config.py` to output an edgelist in `out/Superclass.g.csv`  

 2. Projecting  
    - Project your bipartite graph into its two onemode representations  
    - Run `python3 project_graph.py run_config.py` to output onemode edgelists in `out/Superclass.t` and `out/Superclass.b`  

 3. Computing  
    - Compute a KNC (k-neighborhood-connectivity) plot based on onemode graphs  
    - Run `python3 compute_knc.py run_config.py` to output a KNC list in `out/Superclass.k.csv`  

 4. Analyzing  
    - Get properties of the KNC plots computed beforehand  
    - Run `python3 analyze_knc.py run_config.py` to save properties in your run's result file `out/_results_run_config.py`  

```
python3 build_graph.py run_config.py >> log.txt && python3 project_graph.py run_config.py >> log.txt && python3 compute_knc.py run_config.py >> log.txt && python3 analyze_knc.py run_config.py >> log.txt
```  

### Results
The results of your `run_config.py` runs are saved in `out/_results_run_config.py`  
