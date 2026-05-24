# Lord of the Mysteries Character Graph

Static interactive character graph for *Lord of the Mysteries*.

## Repository flow

1. `Lord of the mysteries.csv`
   Source relationship table.
2. `build_character_graph.py`
   Reads the CSV, aggregates edges, computes layout and scores, then exports JSON.
3. `character_graph_data.json`
   Static data consumed by the frontend.
4. `index.html`
   Frontend renderer used by GitHub Pages.

## Rebuild

```powershell
pwsh -NoLogo -Command "& 'C:/Users/Wxc/anaconda3/envs/layout/python.exe' 'G:/lord-of-the-mysteries-character-graph/build_character_graph.py'"
```

## Pages URL

`https://dadongshancc.github.io/lord-of-the-mysteries-character-graph/`
